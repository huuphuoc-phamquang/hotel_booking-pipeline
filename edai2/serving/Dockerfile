# Image KServe cancel-risk (model-inside-image): runtime sklearnserver + xgboost (XGBClassifier lưu bằng joblib), model
# nằm sẵn ở /mnt/models nên pod không tải model lúc start. Build từ thư mục edai2 sau khi ci/fetch_model.py tải model về
# serving/model/:  docker build -f serving/Dockerfile --build-arg MODEL_VERSION=<v> -t REGISTRY/ml/cancel-risk:v<v> .
FROM kserve/sklearnserver:v0.15.2
# venv /prod_venv thuộc user kserve (1000) của image gốc: cài thẳng, không cần root. xgboost >= 3.3 cần Python 3.12 còn
# image này là 3.11: ghim 3.2.0 + scikit-learn 1.5.2 (bản sẵn trong image) và ml/Dockerfile dùng đúng 2 bản này
RUN pip install --no-cache-dir xgboost==3.2.0
ARG MODEL_VERSION
RUN test -n "$MODEL_VERSION"
ENV MODEL_VERSION=$MODEL_VERSION
COPY serving/model/ /mnt/models/
COPY serving/predictor.py /app/predictor.py
# predictor.py thay sklearnserver: trả thêm model_version trong response
ENTRYPOINT ["python", "/app/predictor.py"]
