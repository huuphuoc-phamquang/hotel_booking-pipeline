"""DP1: kéo Parquet booking từ MinIO landing -> Bronze, rồi validate; DP2 (dp2_bronze_to_gold), DP3 (dp3_offline_features)
chạy sau, cùng ngày logic.

Rubric edai-1 › Data Pipeline Orchestration:
  - DP1 Ingest stage   : task ingest_<table> copy partition ngày {{ ds }} vào lake/bronze/raw_<table>
  - DP1 Validate stage : task validate_<table> chạy Great Expectations, fail thì DAG đỏ
  - DP2, DP3           : cùng mẫu ingest -> validate; DP2 gọi spark_jobs/silver_bookings.py,
                         DP3 dựng feat_customer_booking_stats (xem docs)
  - "All connection and variables should be put inside Airflow": dùng Connection minio_landing,
    spark_default và Variable bronze_tables, không hard-code endpoint/secret.
Dims (hotels, hotel_changes, customers, inventory) không chia theo ngày nên nạp bằng DAG dp1_load_dims, trigger tay 1 lần.
Rubric edai-1 › Data Governance › Lineage: inlets/outlets giúp DataHub vẽ lineage DAG -> bảng.
Proof: docs/Airflow.md chụp Graph view của 3 DAG + giải thích từng task.
"""
from datetime import date, datetime, timedelta

from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datahub_airflow_plugin.entities import Dataset

# image Spark (Iceberg + s3a + JDBC) do Jenkins đặt vào Variable spark_image mỗi lần build (ci/Jenkinsfile.data)
SPARK_CONF = {"spark.kubernetes.container.image": "{{ var.value.get('spark_image', 'spark-booking:latest') }}"}

TABLES = Variable.get("bronze_tables", deserialize_json=True, default_var=["quotes", "bookings", "payments", "cancellations"])
# cancellations partition theo ngày huỷ: copy dt=ds chỉ lấy lần huỷ đã xảy ra trong ngày ds (như CDC từ nguồn)
SHARDS = int(Variable.get("shards_per_day", default_var=16))
LANDING_START = Variable.get("landing_start_date", default_var="2025-01-01")   # = start_date trong generator/config.yaml

default_args = {"owner": "data-eng", "retries": 2, "retry_delay": timedelta(minutes=5)}


def check_landing(table: str, ds: str) -> None:
    """Fail sớm nếu generator chưa ghi xong dữ liệu ngày ds lên landing."""
    hook = S3Hook(aws_conn_id="minio_landing")
    if table == "cancellations":
        # lần huỷ ngày ds đến từ booking của mọi ngày <= ds, mỗi lần chạy generator thêm 1 file part- nên không đếm
        # file được: đợi các manifest (generator ghi khi chạy xong [first, last)) phủ liền [0, ngày ds]
        day = (date.fromisoformat(ds) - date.fromisoformat(LANDING_START)).days
        if manifest_coverage(hook.list_keys(bucket_name="landing", prefix="_manifests/") or []) <= day:
            raise ValueError(f"cancellations ngày {ds}: generator chưa chạy xong mọi ngày tới {ds}")
        return
    keys = hook.list_keys(bucket_name="landing", prefix=f"{table}/dt={ds}/") or []
    if len(keys) < SHARDS:
        raise ValueError(f"{table} ngày {ds}: mới có {len(keys)}/{SHARDS} shard trên landing")


def manifest_coverage(keys: list) -> int:
    """Từ các key _manifests/manifest_<first>_<last>.json, trả về ngày đầu tiên chưa được phủ liền từ ngày 0."""
    covered = 0
    for first, last in sorted(tuple(map(int, k.rsplit("/", 1)[-1][9:-5].split("_"))) for k in keys):
        if first > covered:
            break
        covered = max(covered, last)
    return covered


def validate_bronze(table: str, ds: str) -> None:
    """Validate stage: Great Expectations 1.x (governance/bronze_checks.py) trên partition ngày ds của Bronze,
    chỉ đọc các cột cần kiểm. Khoá MinIO lấy từ Connection minio_landing (cần s3fs trong image Airflow)."""
    import pandas as pd
    from governance.bronze_checks import columns, validate_frame
    from governance.emit_datahub import emit_from_airflow
    conn = S3Hook(aws_conn_id="minio_landing").get_connection("minio_landing")
    df = pd.read_parquet(f"s3://lake/bronze/raw_{table}/dt={ds}/", columns=columns(table), storage_options={
        "key": conn.login, "secret": conn.password, "client_kwargs": {"endpoint_url": conn.extra_dejson["endpoint_url"]}})
    result = validate_frame(table, df)
    emit_from_airflow(f"s3:lake/bronze/raw_{table}", f"gx_bronze_{table}", result.success)
    if not result.success:
        raise ValueError(f"Data validation fail cho bronze raw_{table} ngày {ds}")


with DAG(
    dag_id="dp1_ingest_bronze",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args=default_args,
    tags=["dp1", "bronze", "booking"],
) as dag:
    for t in TABLES:
        sensor = PythonOperator(task_id=f"check_{t}", python_callable=check_landing,
                                op_kwargs={"table": t, "ds": "{{ ds }}"})
        ingest = SparkSubmitOperator(
            task_id=f"ingest_{t}",
            conn_id="spark_default", conf=SPARK_CONF,
            application="/opt/jobs/landing_to_bronze.py",
            application_args=["--table", t, "--ds", "{{ ds }}"],
            inlets=[Dataset("s3", f"landing/{t}")],
            outlets=[Dataset("s3", f"lake/bronze/raw_{t}")],
        )
        validate = PythonOperator(task_id=f"validate_{t}", python_callable=validate_bronze,
                                  op_kwargs={"table": t, "ds": "{{ ds }}"})
        sensor >> ingest >> validate

with DAG(dag_id="dp1_load_dims", start_date=datetime(2025, 1, 1), schedule=None, catchup=False,
         default_args=default_args, tags=["dp1", "bronze", "booking"]) as dims_dag:
    for t in ["hotels", "hotel_changes", "customers", "inventory"]:
        SparkSubmitOperator(task_id=f"ingest_{t}", conn_id="spark_default", conf=SPARK_CONF, application="/opt/jobs/landing_to_bronze.py",
                            application_args=["--table", t],
                            inlets=[Dataset("s3", f"landing/{t}")], outlets=[Dataset("s3", f"lake/bronze/raw_{t}")])
