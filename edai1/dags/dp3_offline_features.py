"""DP3: feature offline từ Gold cho ngày ds (sql/dp3_features.sql), validate, rồi bắn Airflow Dataset FEAT_BATCH để
DAG feast_materialize_incremental (edai2/dags/rag_pipeline.py) đưa feature lên online store.

Rubric edai-1 › Data Pipeline Orchestration › DP3:
  - Ingest stage   : build_features ghi feat_customer_booking_stats + feat_hotel_demand, event_timestamp = hết ngày ds
  - Validate stage : validate_features (entity không null, event_timestamp <= created, tỉ lệ trong [0, 1])
Chạy sau DP2 cùng ngày logic; backfill (airflow dags backfill) sinh đủ lịch sử point-in-time cho training.
"""
import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.datasets import Dataset as AirflowDataset
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.sensors.external_task import ExternalTaskSensor
from datahub_airflow_plugin.entities import Dataset

from gold_checks import FEATURE_CHECKS
from governance.emit_datahub import validate_sql

FEAT_BATCH = AirflowDataset("postgres://postgres:5432/warehouse/gold/feat_hotel_demand")     # feast_materialize_incremental lắng nghe

with DAG(
    dag_id="dp3_offline_features",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
    max_active_runs=1,
    template_searchpath=[os.path.join(os.path.dirname(__file__), "..", "sql")],
    default_args={"owner": "data-eng", "retries": 2, "retry_delay": timedelta(minutes=5)},
    tags=["dp3", "feature", "booking"],
) as dag:
    wait_dp2 = ExternalTaskSensor(task_id="wait_dp2", external_dag_id="dp2_bronze_to_gold", external_task_id=None,
                                  mode="reschedule", timeout=6 * 3600)
    build = SQLExecuteQueryOperator(
        task_id="build_features", conn_id="warehouse", sql="dp3_features.sql",
        inlets=[Dataset("postgres", "warehouse.gold.fact_bookings"), Dataset("postgres", "warehouse.gold.dim_hotel")],
        outlets=[Dataset("postgres", "warehouse.gold.feat_customer_booking_stats"),
                 Dataset("postgres", "warehouse.gold.feat_hotel_demand")])
    validate = PythonOperator(
        task_id="validate_features", outlets=[FEAT_BATCH], python_callable=lambda ds: validate_sql(
            "warehouse", "postgres:warehouse.gold.feat_hotel_demand",
            {k: v.format(ds=ds) for k, v in FEATURE_CHECKS.items()}))
    wait_dp2 >> build >> validate
