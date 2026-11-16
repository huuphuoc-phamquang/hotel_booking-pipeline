# Image train-base cho mọi component KFP + worker TrainJob. xgboost / scikit-learn trùng bản với serving/Dockerfile
# (model pickle bằng joblib phải nạp được trong sklearnserver). Build từ thư mục edai2:
#   docker build -f ml/Dockerfile -t REGISTRY/ml/train-base:1.4 .
FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir xgboost==3.2.0 scikit-learn==1.5.2 pandas==2.2.3 pyarrow==19.0.1 joblib \
    "feast[postgres]==0.68.0" mlflow==3.6.0 "pyiceberg[sql-postgres,pyarrow,s3fs]==0.12.0" kubernetes s3fs fsspec \
    sqlalchemy psycopg2-binary
COPY ml/ /app/ml/
COPY feature_repo/ /feature_repo/
ENV PYTHONPATH=/app/ml
