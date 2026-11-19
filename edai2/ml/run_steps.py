"""Chạy 4 step của training_pipeline (load_from_feast -> split_by_time -> train -> evaluate_and_register) tuần tự trong
1 pod, gọi đúng hàm Python bên trong từng component KFP. Dùng khi cluster chưa có Kubeflow Pipelines (tài khoản quota
thấp); có KFP thì chạy pipeline đã compile như bình thường.
Chạy (image train-base, cần pip install kfp kfp-kubernetes): python ml/run_steps.py [since] [until] [sample_pct]
Env: WAREHOUSE_DSN, ICEBERG_CATALOG_URI, S3_ENDPOINT, AWS_ACCESS_KEY_ID/SECRET (MinIO), FEAST_PG_* (feature_store.yaml).
"""
import json
import sys
import tempfile
from types import SimpleNamespace

import training_pipeline as tp


class Metrics:
    """Thay Output[Metrics] của KFP: giữ metric trong dict để in ra."""
    def __init__(self):
        self.values = {}

    def log_metric(self, key, value):
        self.values[key] = float(value)


if __name__ == "__main__":
    since, until, pct = (sys.argv[1:] + ["2025-01-01", "2025-06-01", "5"][len(sys.argv) - 1:])[:3]
    d = tempfile.mkdtemp()
    art = lambda name: SimpleNamespace(path=f"{d}/{name}")
    data, train, valid, model, metrics = art("data.parquet"), art("train.parquet"), art("valid.parquet"), \
        art("model.joblib"), Metrics()
    snapshot_id = tp.load_from_feast.python_func(features=tp.FEATURES, label_sql=tp.LABEL_SQL, since=since,
                                                 until=until, sample_pct=int(pct), data=data)
    print("load_from_feast: snapshot", snapshot_id)
    tp.split_by_time.python_func(data=data, train=train, valid=valid)
    tp.train.python_func(train=train, model=model, inputs=tp.MODEL_INPUTS, label=tp.LABEL)
    tp.evaluate_and_register.python_func(model=model, valid=valid, train_data=train, metrics=metrics,
                                         inputs=tp.MODEL_INPUTS, label=tp.LABEL, mlflow_uri=tp.MLFLOW_URI,
                                         model_name=tp.MODEL_NAME, min_auc=tp.MIN_AUC,
                                         max_calib_gap=tp.MAX_CALIB_GAP, train_snapshot_id=snapshot_id)
    print("evaluate:", json.dumps(metrics.values))
