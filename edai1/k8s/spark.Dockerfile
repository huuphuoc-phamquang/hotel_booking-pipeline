# Image Spark cho DP1/DP2 và bài skew (Airflow SparkSubmitOperator, master k8s://). Build từ thư mục edai1:
#   docker build -f k8s/spark.Dockerfile -t REGISTRY/data/spark-booking:TAG .
# Catalog Iceberg `lake` = JDBC catalog trên PostgreSQL (không thêm Hive Metastore), warehouse s3a://lake/ trên MinIO;
# cấu hình ở extra của Connection spark_default (spark.sql.catalog.lake.*), khoá MinIO/Postgres từ Secret.
FROM apache/spark:3.5.6-scala2.12-java17-python3-ubuntu
USER root
# curl -f + sha1 của Maven: ADD <url> từng để lại jar 0 byte mà build vẫn qua (lỗi chỉ lộ khi job chạy)
RUN set -e; cd /opt/spark/jars; M=https://repo1.maven.org/maven2; \
    for j in org/apache/iceberg/iceberg-spark-runtime-3.5_2.12/1.9.2/iceberg-spark-runtime-3.5_2.12-1.9.2.jar \
             org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar \
             com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar \
             org/postgresql/postgresql/42.7.7/postgresql-42.7.7.jar; do \
      f=$(basename $j); curl -fsSL -o $f $M/$j; \
      echo "$(curl -fsSL $M/$j.sha1)  $f" | sha1sum -c -; chmod 644 $f; \
    done
COPY spark_jobs/ /opt/jobs/
USER spark
