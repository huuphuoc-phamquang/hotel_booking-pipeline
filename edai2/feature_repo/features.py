"""Định nghĩa Feast cho booking app: entity, feature view offline/streaming (có TTL) và chunk embedding cho RAG.

Rubric edai-2:
  - Web API kéo dữ liệu theo ID (edai-2): booking_attributes theo booking_id cho tool predict_cancellation
  - Feature Store › streaming feature: Flink booking_events_window upsert offline gold.feat_hotel_realtime;
    DAG feast_materialize_realtime đưa lên online mỗi 5 phút. PushSource hotel_realtime_push để sẵn cho
    store.push(..., to=PushMode.ONLINE) khi cần độ tươi tính bằng giây (chưa có job gọi)
  - RAG Data Pipeline › lưu embedding vector qua Feast: feature view policy_chunks có vector_index
TTL = độ cũ tối đa của 1 dòng feature (KHÁC cửa sổ tính 90d/7d/1h): khách sạn có snapshot hằng ngày -> 2 ngày;
khách đặt thưa (trung vị 3 lần/năm với khách có đặt), dòng chỉ ghi khi có hoạt động -> 90 ngày (= cửa sổ tính, quá 90 ngày
thì bookings_90d chắc chắn đã về 0); stream -> 2 giờ (nhu cầu phòng cũ hơn thế không còn đúng).
"""
from datetime import timedelta

from feast import Entity, FeatureView, Field, PushSource
from feast.infra.offline_stores.contrib.postgres_offline_store.postgres_source import PostgreSQLSource
from feast.types import Array, Float32, Int64, String
from feast.value_type import ValueType

customer = Entity(name="customer", join_keys=["customer_id"], value_type=ValueType.INT64)
hotel = Entity(name="hotel", join_keys=["hotel_id"], value_type=ValueType.INT64)
chunk = Entity(name="chunk", join_keys=["chunk_id"], value_type=ValueType.STRING)
booking = Entity(name="booking", join_keys=["booking_id"], value_type=ValueType.INT64)

# Thuộc tính của chính booking (predict_cancellation nhận booking_id): lấy thẳng từ Gold, không cần bảng feat_ riêng.
# TTL 365 ngày: booking cần chấm điểm tới ngày nhận phòng (lead time dài nhất < 1 năm).
booking_source = PostgreSQLSource(
    name="booking_attributes",
    query="""SELECT f.booking_id, c.customer_id, h.hotel_id, f.lead_days, f.nights,
                    (f.cancellation_policy = 'flexible')::int AS free_cancel, c.loyalty_tier,
                    f.booking_date::timestamp AS event_timestamp, f.booking_date::timestamp AS created
             FROM gold.fact_bookings f JOIN gold.dim_customer c USING (customer_key)
             JOIN gold.dim_hotel h USING (hotel_key)""",
    timestamp_field="event_timestamp",
    created_timestamp_column="created",
)

booking_fv = FeatureView(
    name="booking_attributes",
    entities=[booking],
    ttl=timedelta(days=365),
    schema=[Field(name="customer_id", dtype=Int64), Field(name="hotel_id", dtype=Int64),
            Field(name="lead_days", dtype=Int64), Field(name="nights", dtype=Int64),
            Field(name="free_cancel", dtype=Int64), Field(name="loyalty_tier", dtype=Int64)],
    source=booking_source,
    online=True,
)

customer_stats_source = PostgreSQLSource(
    name="feat_customer_booking_stats",
    query="SELECT * FROM gold.feat_customer_booking_stats",
    timestamp_field="event_timestamp",
    created_timestamp_column="created",
)

customer_stats_fv = FeatureView(
    name="customer_booking_stats",
    entities=[customer],
    ttl=timedelta(days=90),
    schema=[Field(name="bookings_90d", dtype=Int64), Field(name="cancel_rate_90d", dtype=Float32),
            Field(name="avg_lead_days_90d", dtype=Float32)],
    source=customer_stats_source,
    online=True,
)

hotel_demand_source = PostgreSQLSource(
    name="feat_hotel_demand",
    query="SELECT * FROM gold.feat_hotel_demand",
    timestamp_field="event_timestamp",
    created_timestamp_column="created",
)

hotel_demand_fv = FeatureView(
    name="hotel_demand",
    entities=[hotel],
    ttl=timedelta(days=2),
    schema=[Field(name="bookings_7d", dtype=Int64), Field(name="cancel_rate_30d", dtype=Float32)],
    source=hotel_demand_source,
    online=True,
)

hotel_realtime_batch = PostgreSQLSource(
    name="feat_hotel_realtime",
    query="SELECT * FROM gold.feat_hotel_realtime",
    timestamp_field="event_timestamp",
    created_timestamp_column="created",
)
hotel_realtime_push = PushSource(name="hotel_realtime_push", batch_source=hotel_realtime_batch)

hotel_realtime_fv = FeatureView(
    name="hotel_realtime",
    entities=[hotel],
    ttl=timedelta(hours=2),
    schema=[Field(name="bookings_1h", dtype=Int64)],
    source=hotel_realtime_push,
    online=True,
)

chunks_source = PostgreSQLSource(
    name="feat_policy_chunks",
    query="SELECT * FROM gold.feat_policy_chunks",
    timestamp_field="event_timestamp",
    created_timestamp_column="created",
)

policy_chunks_fv = FeatureView(
    name="policy_chunks",
    entities=[chunk],
    ttl=timedelta(days=365),
    schema=[
        Field(name="text", dtype=String),
        Field(name="source", dtype=String),
        Field(name="doc_sha256", dtype=String),                  # version tài liệu nguồn (governance RAG)
        Field(name="embed_model", dtype=String),
        Field(name="embedding", dtype=Array(Float32), vector_index=True, vector_length=1024,   # bge-m3
              vector_search_metric="cosine"),
    ],
    source=chunks_source,
    online=True,
)
