# Image Airflow cho DP1-DP3 trên GKE (chart apache-airflow/airflow, KubernetesExecutor). Build từ thư mục edai1:
#   docker build -f k8s/airflow.Dockerfile -t REGISTRY/data/airflow-booking:TAG .
# DAG nằm sẵn trong image thay vì git-sync: không cần token GitHub trong cluster; đổi DAG thì build lại image.
# spark-submit lấy từ pip pyspark (cùng bản Spark 3.5.6 của k8s/spark.Dockerfile), cần JRE để chạy.
FROM apache/airflow:2.10.5-python3.12
USER root
RUN apt-get update && apt-get install -y --no-install-recommends openjdk-17-jre-headless \
 && rm -rf /var/lib/apt/lists/*
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
USER airflow
RUN pip install --no-cache-dir "apache-airflow==2.10.5" apache-airflow-providers-apache-spark \
      apache-airflow-providers-amazon apache-airflow-providers-postgres acryl-datahub-airflow-plugin s3fs \
      -c https://raw.githubusercontent.com/apache/airflow/constraints-2.10.5/constraints-3.12.txt \
 && pip install --no-cache-dir pyspark==3.5.6 "great_expectations>=1,<2"
COPY dags/ /opt/airflow/dags/
COPY sql/ /opt/airflow/sql/
COPY governance/ /opt/airflow/governance/
# governance là package dùng chung; dp2 tìm sql ở dags/../sql
ENV PYTHONPATH=/opt/airflow
