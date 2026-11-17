"""DP2: Bronze -> Silver (Iceberg) -> Gold (PostgreSQL) cho ngày ds, chạy sau DP1 cùng ngày logic.

Rubric edai-1 › Data Pipeline Orchestration › DP2:
  - Ingest stage   : silver_bookings (Spark, dedup + schema evolution + salting) -> stage_gold (Spark -> staging JDBC)
                     -> upsert_gold (sql/dp2_upsert_gold.sql: dim_customer, dim_hotel SCD2, fact_bookings)
  - Validate stage : validate_gold, mỗi check đẩy kết quả lên DataHub (governance.emit_datahub.validate_sql)
Connection spark_default, warehouse (PostgreSQL) đặt trong Airflow. Dim phải nạp trước bằng DAG dp1_load_dims.
silver_bookings chạy chế độ incr: chỉ đọc partition dt=ds của bookings và cancellations, MERGE vào Silver.
"""
import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.sensors.external_task import ExternalTaskSensor
from datahub_airflow_plugin.entities import Dataset

from gold_checks import GOLD_CHECKS
from spark_conf import SPARK_CONF, job
from governance.emit_datahub import validate_sql


with DAG(
    dag_id="dp2_bronze_to_gold",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
    max_active_runs=1,                       # Silver MERGE theo ngày, Gold upsert: chạy tuần tự từng ngày
    template_searchpath=[os.path.join(os.path.dirname(__file__), "..", "sql")],
    default_args={"owner": "data-eng", "retries": 2, "retry_delay": timedelta(minutes=5)},
    tags=["dp2", "silver", "gold", "booking"],
) as dag:
    wait_dp1 = ExternalTaskSensor(task_id="wait_dp1", external_dag_id="dp1_ingest_bronze", external_task_id=None,
                                  mode="reschedule", timeout=6 * 3600)
    silver = SparkSubmitOperator(
        task_id="silver_bookings", conn_id="spark_default", conf=SPARK_CONF, application=job("silver_bookings.py"),
        application_args=["incr", "s3a://lake/bronze", "{{ ds }}"],
        inlets=[Dataset("s3", "lake/bronze/raw_bookings"), Dataset("s3", "lake/bronze/raw_hotels"),
                Dataset("s3", "lake/bronze/raw_cancellations")],
        outlets=[Dataset("iceberg", "silver.stg_bookings")])
    stage = SparkSubmitOperator(
        task_id="stage_gold", conn_id="spark_default", conf=SPARK_CONF, application=job("stage_gold.py"),
        application_args=["--ds", "{{ ds }}"],
        inlets=[Dataset("iceberg", "silver.stg_bookings")],
        outlets=[Dataset("postgres", f"warehouse.gold.{t}")
                 for t in ("stg_bookings", "stg_customers", "stg_hotel_changes", "hotel_rooms")])
    upsert = SQLExecuteQueryOperator(
        task_id="upsert_gold", conn_id="warehouse", sql="dp2_upsert_gold.sql",
        outlets=[Dataset("postgres", f"warehouse.gold.{t}") for t in ("dim_hotel", "dim_customer", "fact_bookings")])
    validate = PythonOperator(
        task_id="validate_gold", python_callable=lambda ds: validate_sql(
            "warehouse", "postgres:warehouse.gold.fact_bookings", {k: v.format(ds=ds) for k, v in GOLD_CHECKS.items()}))
    wait_dp1 >> silver >> stage >> upsert >> validate
