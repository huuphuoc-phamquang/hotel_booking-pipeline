"""Conf spark-submit chung của DP1/DP2 (module phụ trợ, không phải DAG): Spark on Kubernetes, s3a tới MinIO, catalog
Iceberg `lake` = JDBC catalog trên Postgres (cùng catalog DataHub đọc ở governance/datahub/iceberg_silver.yml).
Endpoint và khoá lấy từ Connection minio_landing, warehouse bằng template lúc chạy task, không hard-code;
conf là template field của SparkSubmitOperator. Master + deploy mode nằm ở Connection spark_default.
"""
# image Spark (Iceberg + s3a + JDBC) do Jenkins đặt vào Variable spark_image mỗi lần build (ci/Jenkinsfile.data)
_JDBC = "jdbc:postgresql://{{ conn.warehouse.host }}:{{ conn.warehouse.port }}/{{ conn.warehouse.schema }}"
SPARK_CONF = {
    "spark.kubernetes.container.image": "{{ var.value.get('spark_image', 'spark-booking:latest') }}",
    "spark.kubernetes.authenticate.driver.serviceAccountName": "spark",     # edai1/k8s/spark-rbac.yaml
    "spark.executor.instances": "{{ var.value.get('spark_executors', '4') }}",
    "spark.executor.memory": "4g",
    "spark.driver.memory": "2g",
    "spark.hadoop.fs.s3a.endpoint": "{{ conn.minio_landing.extra_dejson.endpoint_url }}",
    "spark.hadoop.fs.s3a.access.key": "{{ conn.minio_landing.login }}",
    "spark.hadoop.fs.s3a.secret.key": "{{ conn.minio_landing.password }}",
    "spark.hadoop.fs.s3a.path.style.access": "true",
    "spark.hadoop.fs.s3a.connection.ssl.enabled": "false",
    "spark.sql.extensions": "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
    "spark.sql.catalog.lake": "org.apache.iceberg.spark.SparkCatalog",
    "spark.sql.catalog.lake.type": "jdbc",
    "spark.sql.catalog.lake.uri": _JDBC,
    "spark.sql.catalog.lake.jdbc.user": "{{ conn.warehouse.login }}",
    "spark.sql.catalog.lake.jdbc.password": "{{ conn.warehouse.password }}",
    "spark.sql.catalog.lake.warehouse": "s3a://lake/",
    # stage_gold.py đọc JDBC Gold từ biến môi trường của driver
    "spark.kubernetes.driverEnv.WAREHOUSE_JDBC_URL": _JDBC,
    "spark.kubernetes.driverEnv.WAREHOUSE_JDBC_USER": "{{ conn.warehouse.login }}",
    "spark.kubernetes.driverEnv.WAREHOUSE_JDBC_PASSWORD": "{{ conn.warehouse.password }}",
}


def job(name: str) -> str:
    """Đường dẫn script trong image Spark; local:// để cluster mode không upload file từ pod Airflow."""
    return f"local:///opt/jobs/{name}"
