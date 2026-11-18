# Image Airflow cho DP1-DP3 + DAG edai2 (RAG, materialize, score_bookings, drift_monitor) trên GKE
# (chart apache-airflow/airflow, KubernetesExecutor). Build từ gốc repo (cần cả edai1/ và edai2/):
#   docker build -f edai1/k8s/airflow.Dockerfile -t REGISTRY/data/airflow-booking:TAG .
# DAG nằm sẵn trong image thay vì git-sync: không cần token GitHub trong cluster; đổi DAG thì build lại image.
# spark-submit lấy từ pip pyspark (cùng bản Spark 3.5.6 của k8s/spark.Dockerfile), cần JRE để chạy.
# Feast repo chép vào /opt/airflow/feature_repo (Variable feast_repo_path); biến FEAST_PG_* lấy từ Secret của chart.
# Context build gốc repo chỉ gửi các thư mục COPY dưới đây (airflow.Dockerfile.dockerignore, BuildKit).
FROM apache/airflow:2.10.5-python3.12
USER root
RUN apt-get update && apt-get install -y --no-install-recommends openjdk-17-jre-headless \
 && rm -rf /var/lib/apt/lists/*
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
USER airflow
# pyarrow: validate_shards (dp1) đọc Bronze bằng pyarrow.dataset; ghim theo constraints Airflow
RUN pip install --no-cache-dir "apache-airflow==2.10.5" apache-airflow-providers-apache-spark \
      apache-airflow-providers-amazon apache-airflow-providers-postgres acryl-datahub-airflow-plugin s3fs pyarrow \
      scipy httpx prometheus-client \
      -c https://raw.githubusercontent.com/apache/airflow/constraints-2.10.5/constraints-3.12.txt \
 && pip install --no-cache-dir pyspark==3.5.6 "great_expectations>=1,<2"
# DAG edai2: feast (materialize, RAG), sentence-transformers (embed, torch bản CPU), mlflow + kfp (drift_monitor).
# Cài riêng không ghim constraints Airflow như pyspark; feast cùng bản với booking-mcp (mcp_server/requirements.txt).
RUN pip install --no-cache-dir "feast[postgres]==0.68.0" sentence-transformers mlflow-skinny kfp \
      --extra-index-url https://download.pytorch.org/whl/cpu
COPY --chown=airflow:root edai1/dags/ edai2/dags/ /opt/airflow/dags/
# 2 thư mục DAG đều có .airflowignore, COPY chung thì file sau đè file trước: gộp lại
COPY edai1/dags/.airflowignore /tmp/ignore1
COPY edai2/dags/.airflowignore /tmp/ignore2
RUN cat /tmp/ignore1 /tmp/ignore2 > /opt/airflow/dags/.airflowignore
COPY edai1/sql/ /opt/airflow/sql/
COPY edai1/governance/ /opt/airflow/governance/
COPY edai2/feature_repo/ /opt/airflow/feature_repo/
# governance là package dùng chung; dp2 tìm sql ở dags/../sql; drift_stats nằm cùng thư mục dags
ENV PYTHONPATH=/opt/airflow
