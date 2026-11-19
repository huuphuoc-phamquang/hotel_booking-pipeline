# MLflow tracking server + model registry (rubric edai-2 › lưu model, data, metadata mỗi lần train lên MLflow).
# Image chính thức thiếu driver Postgres và boto3: metadata trên Postgres sẵn có, artifact trên MinIO (S3).
# Build từ thư mục edai2:  docker build -f docker/mlflow.Dockerfile -t REGISTRY/ml/mlflow:3.6.0 .
FROM python:3.11-slim
# sqlalchemy 2.1 bỏ FallbackAsyncAdaptedQueuePool mà mlflow 3.6 import -> server không khởi động
RUN pip install --no-cache-dir mlflow==3.6.0 "sqlalchemy<2.1" psycopg2-binary boto3
EXPOSE 5000
