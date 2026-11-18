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

from datahub.emitter.mce_builder import make_assertion_urn, make_data_job_urn, make_dataset_urn, make_tag_urn
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    AssertionInfoClass, AssertionResultClass, AssertionResultTypeClass, AssertionRunEventClass, AssertionRunStatusClass,
    AssertionStdOperatorClass, AssertionTypeClass, DatasetAssertionInfoClass, DatasetAssertionScopeClass,
    DataJobInputOutputClass, EditableDatasetPropertiesClass, GlobalTagsClass, TagAssociationClass,
)

PIPELINES = {
    # task Airflow                          : (bảng vào, bảng ra); DP1 copy nguyên landing/<t> -> raw_<t>
    **{(dag, f"ingest_{t}"): ([f"s3:landing/{t}"], [f"s3:lake/bronze/raw_{t}"])
       for dag, tables in (("dp1_ingest_bronze", ["quotes", "bookings", "payments", "cancellations"]),
                           ("dp1_load_dims", ["hotels", "hotel_changes", "customers", "inventory"]))
       for t in tables},
    ("dp2_bronze_to_gold", "silver_bookings"): (["s3:lake/bronze/raw_bookings", "s3:lake/bronze/raw_hotels",
                                                 "s3:lake/bronze/raw_cancellations"], ["iceberg:silver.stg_bookings"]),
    ("dp2_bronze_to_gold", "stage_gold"): (["iceberg:silver.stg_bookings", "s3:lake/bronze/raw_customers",
                                            "s3:lake/bronze/raw_hotels", "s3:lake/bronze/raw_hotel_changes",
                                            "s3:lake/bronze/raw_inventory"],
                                           ["postgres:warehouse.gold.stg_bookings", "postgres:warehouse.gold.stg_customers",
                                            "postgres:warehouse.gold.stg_hotel_changes",
                                            "postgres:warehouse.gold.stg_hotel_rooms"]),
    ("dp2_bronze_to_gold", "upsert_gold"): (["postgres:warehouse.gold.stg_bookings", "postgres:warehouse.gold.stg_customers",
                                             "postgres:warehouse.gold.stg_hotel_changes",
                                             "postgres:warehouse.gold.stg_hotel_rooms"],
                                            ["postgres:warehouse.gold.dim_hotel", "postgres:warehouse.gold.dim_customer",
                                             "postgres:warehouse.gold.fact_bookings", "postgres:warehouse.gold.hotel_rooms"]),
    ("dp3_offline_features", "build_features"): (["postgres:warehouse.gold.fact_bookings", "postgres:warehouse.gold.dim_hotel",
                                                  "postgres:warehouse.gold.dim_customer"],
                                                 ["postgres:warehouse.gold.feat_customer_booking_stats",
                                                  "postgres:warehouse.gold.feat_hotel_demand"]),
}


# Mô tả nhiệm vụ từng bảng (tab Documentation) + tag zone; schema do 3 recipe trong governance/datahub/ ingest.
G, S, B = "postgres:warehouse.gold.", "iceberg:silver.", "s3:lake/bronze/"
TABLES = {
    "bronze": {
        B + "raw_quotes": "Log lượt xem giá, một dòng mỗi lượt; bảng lớn nhất (mốc 100GB), dùng cho bài skew.",
        B + "raw_bookings": "Sự kiện đặt phòng lúc tạo, chưa có trạng thái huỷ; còn bản trùng do double submit và 2 phiên bản schema.",
        B + "raw_cancellations": "Các lần huỷ, chia theo ngày huỷ nên partition dt=ds không chứa lần huỷ tương lai.",
        B + "raw_payments": "Giao dịch thanh toán của booking.",
        B + "raw_hotels": "Danh mục khách sạn: thành phố, hạng sao, giá gốc.",
        B + "raw_hotel_changes": "Lịch sử đổi giá của khách sạn, nguồn của SCD2 dim_hotel.",
        B + "raw_customers": "Danh mục khách: thành phố, hạng thành viên.",
        B + "raw_inventory": "Số phòng mở bán theo khách sạn, loại phòng và đêm.",
    },
    "silver": {
        S + "stg_bookings": "Một dòng mỗi booking sau dedup theo idempotency_key, gộp schema v1/v2, gắn city/stars và "
                           "trạng thái huỷ (MERGE mỗi ngày).",
        S + "stg_quotes": "Lượt xem giá kèm số phòng mở bán của ô hotel × room_type × stay_date (kết quả bài join lệch).",
    },
    "gold": {
        G + "dim_hotel": "Dimension SCD2 của khách sạn: mỗi lần đổi giá sinh một phiên bản (valid_from_ts, valid_to_ts, is_current).",
        G + "dim_customer": "Dimension khách hàng.",
        G + "fact_bookings": "Một dòng mỗi booking, trỏ tới phiên bản dim_hotel có hiệu lực lúc đặt và tới dim_customer.",
        G + "labels_cancel": "View nhãn huấn luyện: is_cancelled = huỷ trước ngày nhận phòng.",
        G + "feat_customer_booking_stats": "Feature lịch sử 90 ngày của khách (DP3), point-in-time theo event_timestamp.",
        G + "feat_hotel_demand": "Feature nhu cầu 7 và 30 ngày của khách sạn (DP3).",
        G + "feat_hotel_realtime": "Số booking trong 1 giờ gần nhất của khách sạn, Flink ghi.",
        G + "booking_risk": "Xác suất huỷ của từng booking kèm phiên bản model đã chấm (DAG score_bookings).",
        G + "hotel_rooms": "Số phòng mở bán theo khách sạn và đêm (DP2 upsert 30 đêm tới mỗi ngày).",
        G + "overbooking_limits": "Số phòng bán vượt K đã được revenue manager duyệt.",
        G + "stream_bookings_1m": "Số booking từng phút do Flink đếm, để đối soát stream với batch.",
        G + "stream_late_bookings": "Event trễ hơn watermark + allowed lateness (side output của Flink).",
        G + "stg_bookings": "Staging DP2: booking tạo hoặc huỷ trong ngày ds, Spark ghi qua JDBC, ghi đè mỗi lần chạy.",
        G + "stg_customers": "Staging DP2: khách của các booking trong ngày ds.",
        G + "stg_hotel_changes": "Staging DP2: lần đổi giá khách sạn, nạp vào dim_hotel bằng SCD2.",
        G + "stg_hotel_rooms": "Staging DP2: số phòng mở bán của 30 đêm sau ds, upsert vào hotel_rooms.",
    },
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


def emit_table_docs(emitter: DatahubRestEmitter) -> None:
    """Mô tả + tag zone cho từng bảng. Dùng aspect editable/tags: recipe ingest không ghi đè các aspect này."""
    for zone, tables in TABLES.items():
        for ref, desc in tables.items():
            urn = ds_urn(ref)
            emitter.emit(MetadataChangeProposalWrapper(entityUrn=urn, aspect=EditableDatasetPropertiesClass(description=desc)))
            emitter.emit(MetadataChangeProposalWrapper(
                entityUrn=urn, aspect=GlobalTagsClass(tags=[TagAssociationClass(tag=make_tag_urn(zone))])))


def emit_validation(emitter: DatahubRestEmitter, table_ref: str, check: str, passed: bool) -> None:
    """Gửi kết quả 1 expectation (vd idempotency_key unique): AssertionInfo khai báo assertion gắn với dataset (tab
    Validation cần để hiện tên và phạm vi), rồi AssertionRunEvent là kết quả của lần chạy."""
    urn = make_assertion_urn(f"{table_ref}-{check}")
    info = AssertionInfoClass(type=AssertionTypeClass.DATASET, description=check, datasetAssertion=DatasetAssertionInfoClass(
        dataset=ds_urn(table_ref), scope=DatasetAssertionScopeClass.DATASET_ROWS,
        operator=AssertionStdOperatorClass._NATIVE_, nativeType=check))
    emitter.emit(MetadataChangeProposalWrapper(entityUrn=urn, aspect=info))
    now_ms = int(time.time() * 1000)
    event = AssertionRunEventClass(
        timestampMillis=now_ms,
        assertionUrn=urn,
        asserteeUrn=ds_urn(table_ref),
        runId=f"{check}-{now_ms}",
        status=AssertionRunStatusClass.COMPLETE,
        result=AssertionResultClass(type=AssertionResultTypeClass.SUCCESS if passed
                                    else AssertionResultTypeClass.FAILURE),
    )
    emitter.emit(MetadataChangeProposalWrapper(entityUrn=event.assertionUrn, aspect=event))


def emit_from_airflow(table_ref: str, check: str, passed: bool) -> None:
    """Gọi trong task Airflow: GMS lấy từ Connection datahub_rest_default (governance/ deploy cạnh dags/), password
    của Connection là Personal Access Token (GMS bật xác thực)."""
    import re

    from airflow.hooks.base import BaseHook
    conn = BaseHook.get_connection("datahub_rest_default")
    # host có thể đã gồm scheme + cổng (http://gms:8080) hoặc chỉ tên host, cổng nằm ở trường port của Connection
    gms = conn.host if "://" in conn.host else f"http://{conn.host}"
    gms = gms if not conn.port or re.search(r":\d+$", gms) else f"{gms}:{conn.port}"
    emit_validation(DatahubRestEmitter(gms_server=gms, token=conn.password or None), table_ref, check, passed)


if __name__ == "__main__":
    em = DatahubRestEmitter(gms_server=os.environ.get("DATAHUB_GMS", "http://datahub-gms:8080"),
                            token=os.environ.get("DATAHUB_TOKEN") or None)
    emit_lineage(em)
    emit_table_docs(em)
    # Kết quả validation không emit ở đây: task validate_* của DAG gửi kết quả GX thật (dags/dp1_ingest_bronze.py)


def validate_sql(conn_id: str, checks: dict[str, dict[str, str]], ds: str) -> None:
    """Data validation cho Gold: {bảng: {tên check: SQL trả về 1 boolean}}; mỗi kết quả đẩy lên DataHub vào đúng bảng
    được kiểm, fail task nếu có check sai ({ds} trong SQL thay bằng ngày logic)."""
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    hook, failed = PostgresHook(postgres_conn_id=conn_id), []
    for table_ref, table_checks in checks.items():
        for name, sql in table_checks.items():
            passed = bool(hook.get_first(sql.format(ds=ds))[0])
            emit_from_airflow(table_ref, name, passed)
            if not passed:
                failed.append(f"{table_ref}:{name}")
    if failed:
        raise ValueError(f"check fail {failed}")
