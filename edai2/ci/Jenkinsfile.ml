// CI/CD cho model cancel-risk: training pipeline (KFP) -> image KServe model-inside-image -> canary A/B.
// Training pipeline (test component -> build image train -> compile KFP -> upload + tạo run qua
// KFP API), Inference engine (kéo model alias production từ MLflow -> build image -> apply InferenceService).
// Canary (ngoài phạm vi rubric edai-1/edai-2): CANARY_PERCENT > 0 thì revision mới nhận phần traffic đó, revision cũ là stable; 100 = promote.
pipeline {
  agent { kubernetes { yamlFile 'ci/pod-template.yaml'; defaultContainer 'tools' } }
  parameters {
    booleanParam(name: 'TRAIN', defaultValue: true, description: 'Chạy training_pipeline trên KFP')
    string(name: 'SINCE', defaultValue: '2025-01-01')
    string(name: 'UNTIL', defaultValue: '2025-10-01')
    string(name: 'CANARY_PERCENT', defaultValue: '50', description: '0 = rollback, 100 = promote')
  }
  environment {
    REGISTRY = "asia-southeast1-docker.pkg.dev/${env.GCP_PROJECT}/booking"
    TAG      = "${env.GIT_COMMIT.take(7)}"
  }
  stages {
    stage('Test component') {
      steps {
        sh 'pip install -q xgboost==3.2.0 scikit-learn==1.5.2 pandas pyarrow joblib fsspec "pyiceberg[sql-sqlite,pyarrow]==0.12.0" "kfp>=2" pytest'
        sh 'PYTHONPATH=ml pytest tests/test_data_version.py tests/test_train_xgb_dist.py -q'
      }
    }
    stage('Build image train-base') {
      steps {
        withVault([vaultSecrets: [[path: 'secret/ci/registry', secretValues: [[envVar: 'REG_KEY', vaultKey: 'json_key']]]]]) {
          sh 'echo "$REG_KEY" | docker login -u _json_key --password-stdin https://asia-southeast1-docker.pkg.dev'
          sh 'docker build -f ml/Dockerfile -t $REGISTRY/ml/train-base:$TAG . && docker push $REGISTRY/ml/train-base:$TAG'
        }
      }
    }
    stage('Compile + run KFP') {
      when { expression { params.TRAIN } }
      steps {
        // component dùng BASE_IMAGE: thay tag cố định bằng tag vừa build để run chạy đúng code của commit này
        sh "sed -i 's#registry.booking.local/ml/train-base:1.4#${REGISTRY}/ml/train-base:${TAG}#g' ml/training_pipeline.py"
        withVault([vaultSecrets: [[path: 'secret/ci/kfp', secretValues: [[envVar: 'KFP_HOST', vaultKey: 'host']]]]]) {
          sh 'python ci/kfp_run.py --host "$KFP_HOST" --version $TAG since=$SINCE until=$UNTIL > run_id.txt'
        }
        echo "KFP run ${readFile('run_id.txt').trim()} (evaluate_and_register tự gắn alias production nếu qua cổng)"
      }
    }
    stage('Build image KServe') {
      steps {
        withVault([vaultSecrets: [[path: 'secret/ci/mlflow', secretValues: [[envVar: 'MLFLOW_TRACKING_URI', vaultKey: 'uri']]]]]) {
          sh 'python ci/fetch_model.py --alias production > model_version.txt'
        }
        sh 'V=$(cat model_version.txt); docker build -f serving/Dockerfile --build-arg MODEL_VERSION=$V -t $REGISTRY/ml/cancel-risk:v$V . && docker push $REGISTRY/ml/cancel-risk:v$V'
      }
    }
    stage('Canary') {
      steps {
        // KServe Serverless: đổi image + canaryTrafficPercent -> revision mới nhận % traffic, revision cũ giữ phần còn lại
        sh '''
          V=$(cat model_version.txt)
          # JSON patch (không phải merge): merge patch thay cả mảng containers, mất args
          kubectl -n ml patch isvc cancel-risk --type json -p "[
            {\"op\": \"replace\", \"path\": \"/spec/predictor/containers/0/image\", \"value\": \"$REGISTRY/ml/cancel-risk:v$V\"},
            {\"op\": \"add\", \"path\": \"/spec/predictor/canaryTrafficPercent\", \"value\": ${CANARY_PERCENT}}]"
          kubectl -n ml wait isvc/cancel-risk --for=condition=Ready --timeout=300s
          kubectl -n ml get isvc cancel-risk -o jsonpath='{.status.components.predictor.traffic}'
          # promote: booking đang giữ phòng còn điểm của bản cũ, chấm lại bằng bản mới cho propose_overbooking,
          # qua cancel-risk-bulk (không logger) để drift-api không nhận cả loạt
          if [ "${CANARY_PERCENT}" = "100" ]; then
            kubectl -n ml patch isvc cancel-risk-bulk --type json -p "[
              {\"op\": \"replace\", \"path\": \"/spec/predictor/containers/0/image\", \"value\": \"$REGISTRY/ml/cancel-risk:v$V\"}]"
            kubectl -n ml wait isvc/cancel-risk-bulk --for=condition=Ready --timeout=300s
            kubectl -n airflow exec deploy/airflow-scheduler -- airflow dags trigger rescore_active
          fi
        '''
      }
    }
  }
}
