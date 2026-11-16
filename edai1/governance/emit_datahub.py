"""Đẩy lineage và kết quả data validation lên DataHub cho các bảng booking của DP1/DP2/DP3.

Rubric edai-1 › Data Governance (DP1, DP2, DP3 linked with related tables):
  - Lineage between the pipeline and tables : DataJob (task Airflow) có inputDatasets/outputDatasets
  - Data validation                         : AssertionRunEvent gắn vào dataset -> tab "Validation" trên DataHub
Thường thì datahub-airflow-plugin tự emit lineage từ inlets/outlets; file này dùng khi cần emit tay
(vd job Spark chạy ngoài Airflow) hoặc để đẩy kết quả Great Expectations.
Proof: docs/DataHub.md chụp màn hình Lineage graph và tab Validation của từng bảng.
"""
import os
import time

from datahub.emitter.mce_builder import make_assertion_urn, make_data_job_urn, make_dataset_urn
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    AssertionResultClass, AssertionResultTypeClass, AssertionRunEventClass, AssertionRunStatusClass,
    DataJobInputOutputClass,
)

PIPELINES = {
    # task Airflow                          : (bảng vào, bảng ra)
    ("dp1_ingest_bronze", "ingest_bookings"): (["s3:landing/bookings"], ["s3:lake/bronze/raw_bookings"]),
    ("dp2_bronze_to_gold", "silver_bookings"): (["s3:lake/bronze/raw_bookings", "s3:lake/bronze/raw_hotels",
                                                 "s3:lake/bronze/raw_cancellations"], ["iceberg:silver.stg_bookings"]),
    ("dp2_bronze_to_gold", "stage_gold"): (["iceberg:silver.stg_bookings", "s3:lake/bronze/raw_customers",
                                            "s3:lake/bronze/raw_hotel_changes"],
                                           ["postgres:warehouse.gold.stg_bookings", "postgres:warehouse.gold.stg_customers",
                                            "postgres:warehouse.gold.stg_hotel_changes"]),
    ("dp2_bronze_to_gold", "upsert_gold"): (["postgres:warehouse.gold.stg_bookings", "postgres:warehouse.gold.stg_customers",
                                             "postgres:warehouse.gold.stg_hotel_changes"],
                                            ["postgres:warehouse.gold.dim_hotel", "postgres:warehouse.gold.dim_customer",
                                             "postgres:warehouse.gold.fact_bookings"]),
    ("dp3_offline_features", "build_features"): (["postgres:warehouse.gold.fact_bookings", "postgres:warehouse.gold.dim_hotel"],
                                                 ["postgres:warehouse.gold.feat_customer_booking_stats",
                                                  "postgres:warehouse.gold.feat_hotel_demand"]),
}


def ds_urn(ref: str) -> str:
    """'platform:name' -> URN dataset của DataHub (env PROD); name phải trùng tên Dataset ở inlets/outlets của DAG.
    Postgres phải có tên database (warehouse.schema.table) thì mới khớp entity DataHub ingest từ Postgres."""
    platform, name = ref.split(":", 1)
    return make_dataset_urn(platform=platform, name=name, env="PROD")


def emit_lineage(emitter: DatahubRestEmitter) -> None:
    """Mỗi task Airflow là 1 DataJob; khai báo input/output để DataHub nối DAG với bảng."""
    for (dag_id, task_id), (inputs, outputs) in PIPELINES.items():
        job_urn = make_data_job_urn(orchestrator="airflow", flow_id=dag_id, job_id=task_id, cluster="prod")
        aspect = DataJobInputOutputClass(inputDatasets=[ds_urn(i) for i in inputs],
                                         outputDatasets=[ds_urn(o) for o in outputs])
        emitter.emit(MetadataChangeProposalWrapper(entityUrn=job_urn, aspect=aspect))


def emit_validation(emitter: DatahubRestEmitter, table_ref: str, check: str, passed: bool) -> None:
    """Gửi kết quả 1 expectation (vd idempotency_key unique) thành AssertionRunEvent của dataset."""
    now_ms = int(time.time() * 1000)
    event = AssertionRunEventClass(
        timestampMillis=now_ms,
        assertionUrn=make_assertion_urn(f"{table_ref}-{check}"),
        asserteeUrn=ds_urn(table_ref),
        runId=f"{check}-{now_ms}",
        status=AssertionRunStatusClass.COMPLETE,
        result=AssertionResultClass(type=AssertionResultTypeClass.SUCCESS if passed
                                    else AssertionResultTypeClass.FAILURE),
    )
    emitter.emit(MetadataChangeProposalWrapper(entityUrn=event.assertionUrn, aspect=event))


def emit_from_airflow(table_ref: str, check: str, passed: bool) -> None:
    """Gọi trong task Airflow: GMS lấy từ Connection datahub_rest_default (governance/ deploy cạnh dags/)."""
    from airflow.hooks.base import BaseHook
    emit_validation(DatahubRestEmitter(gms_server=BaseHook.get_connection("datahub_rest_default").host),
                    table_ref, check, passed)


if __name__ == "__main__":
    em = DatahubRestEmitter(gms_server=os.environ.get("DATAHUB_GMS", "http://datahub-gms:8080"))
    emit_lineage(em)
    # Kết quả validation không emit ở đây: task validate_* của DAG gửi kết quả GX thật (dags/dp1_ingest_bronze.py)


def validate_sql(conn_id: str, table_ref: str, checks: dict[str, str]) -> None:
    """Data validation cho Gold: mỗi check là 1 câu SQL trả về 1 giá trị boolean; đẩy từng kết quả lên DataHub,
    fail task nếu có check sai."""
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    hook, failed = PostgresHook(postgres_conn_id=conn_id), []
    for name, sql in checks.items():
        passed = bool(hook.get_first(sql)[0])
        emit_from_airflow(table_ref, name, passed)
        if not passed:
            failed.append(name)
    if failed:
        raise ValueError(f"{table_ref}: check fail {failed}")
