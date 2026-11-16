"""PyFlink job: đếm booking theo khách sạn trong 1 giờ qua (trượt mỗi 5 phút), xử lý late arrival và callback trùng.

Rubric edai-1 › Processing Jobs › Flink job to handle streaming data problems:
  - Baseline (without optimization)   : BASELINE=True -> watermark 0s, không dedup
  - Handle late arrival with explanation: watermark 10 phút + allowedLateness 5 phút + side output. Side output
    lấy ở nhánh đối soát tumbling 1 phút: với cửa sổ trượt 1 giờ, event chỉ rơi ra side output khi trễ hơn cả
    cửa sổ cuối chứa nó (> 1h15'), nên gần như không thấy. Đối soát: mỗi giờ
    sum(gold.stream_bookings_1m) + count(gold.stream_late_bookings) = số booking (dedup idempotency_key) ở Silver.
  - Handle other streaming problem     : dedup payment_callback theo event_id bằng keyed state + TTL; data contract
                                         (flink_jobs/contract.py) chặn event sai trước watermark -> booking_events_dlq
  - Window processing                  : sliding event-time window 1 giờ, trượt 5 phút (SlidingEventTimeWindows),
                                         tumbling 1 phút cho đối soát (TumblingEventTimeWindows)
Đầu vào: topic booking_events do generator/stream_gen.py phát lại (key = hotel_id).
Kết quả bookings_1h upsert vào gold.feat_hotel_realtime theo (hotel_id, event_timestamp = window_end): đây là
batch source của Feast hotel_realtime; DAG feast_materialize_realtime đưa lên online store mỗi 5 phút. Upsert nên window bắn lại do allowedLateness ghi đè chứ không cộng trùng;
cùng checkpoint EXACTLY_ONCE (offset Kafka + state dedup khôi phục khi restart) thì kết quả cuối không trùng.
Cần jar flink-connector-jdbc + driver PostgreSQL trên classpath; JDBC lấy từ biến môi trường FEAT_JDBC_*.
Proof: docs/edai-1/processing_jobs.md (ảnh ở docs/images/edai-1/) chụp Flink UI (số record ở side output, watermark lag, backpressure, checkpoint).
"""
import json
import os
from datetime import datetime, timezone

from pyflink.common import Duration, Row, Time, Types, WatermarkStrategy
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.watermark_strategy import TimestampAssigner
from pyflink.datastream import CheckpointingMode, OutputTag, StreamExecutionEnvironment
from pyflink.datastream.connectors.jdbc import JdbcConnectionOptions, JdbcExecutionOptions, JdbcSink
from pyflink.datastream.connectors.kafka import (KafkaOffsetsInitializer, KafkaRecordSerializationSchema, KafkaSink,
                                                 KafkaSource)
from pyflink.datastream.functions import KeyedProcessFunction, ProcessFunction, ProcessWindowFunction, RuntimeContext

from contract import violation
from pyflink.datastream.state import StateTtlConfig, ValueStateDescriptor
from pyflink.datastream.window import SlidingEventTimeWindows, TumblingEventTimeWindows

BASELINE = False
MAX_OUT_OF_ORDER = Duration.of_minutes(0 if BASELINE else 10)
ALLOWED_LATENESS_MS = 5 * 60 * 1000
LATE_TAG = OutputTag("too-late", Types.STRING())
DLQ_TAG = OutputTag("contract-violation", Types.STRING())
DLQ_TOPIC = "booking_events_dlq"
FEAT_ROW = Types.ROW([Types.LONG(), Types.LONG(), Types.SQL_TIMESTAMP()])     # hotel_id, count, window_end
LATE_ROW = Types.ROW([Types.LONG(), Types.LONG(), Types.SQL_TIMESTAMP()])     # event_id, hotel_id, event_time
UPSERT_SQL = ("INSERT INTO gold.feat_hotel_realtime (hotel_id, bookings_1h, event_timestamp) VALUES (?, ?, ?) "
              "ON CONFLICT (hotel_id, event_timestamp) DO UPDATE SET bookings_1h = EXCLUDED.bookings_1h, created = now()")
MINUTE_SQL = ("INSERT INTO gold.stream_bookings_1m (hotel_id, bookings, window_end) VALUES (?, ?, ?) "
              "ON CONFLICT (hotel_id, window_end) DO UPDATE SET bookings = EXCLUDED.bookings")
LATE_SQL = ("INSERT INTO gold.stream_late_bookings (event_id, hotel_id, event_time) VALUES (?, ?, ?) "
            "ON CONFLICT (event_id) DO NOTHING")


def utc(ms: int) -> datetime:
    """Epoch ms -> datetime UTC naive như cột TIMESTAMP."""
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).replace(tzinfo=None)


def late_row(v: str) -> Row:
    e = json.loads(v)
    return Row(e["event_id"], e["hotel_id"], utc(e["event_time"]))


class EventTimeAssigner(TimestampAssigner):
    """Lấy event_time (ms) trong JSON làm event time thay vì thời điểm Kafka nhận. Event sai contract (thiếu event_time,
    không phải JSON) nhận timestamp 0: không đẩy watermark lên (watermark lấy max), và ContractCheck chuyển nó sang DLQ."""

    def extract_timestamp(self, value, record_timestamp):
        try:
            t = json.loads(value).get("event_time")
        except (json.JSONDecodeError, AttributeError):
            return 0
        return t if isinstance(t, int) else 0


class CountPerWindow(ProcessWindowFunction):
    """Đếm booking mới của 1 khách sạn trong cửa sổ kết thúc tại window_end."""

    def process(self, key, context, elements):
        yield Row(key, sum(1 for _ in elements), utc(context.window().end))


class ContractCheck(ProcessFunction):
    """Event đúng contract đi tiếp; event sai (hoặc không phải JSON) ra DLQ kèm reason = trường vi phạm."""

    def process_element(self, value, ctx):
        try:
            reason = violation(json.loads(value))
        except json.JSONDecodeError:
            reason = "json"
        if reason is None:
            yield value
        else:
            yield DLQ_TAG, json.dumps({"reason": reason, "raw": value})


class DedupByEventId(KeyedProcessFunction):
    """Chỉ cho qua lần đầu tiên của mỗi key (event_id hoặc idempotency_key); state tự hết hạn sau 1 giờ."""

    def open(self, runtime_context: RuntimeContext):
        desc = ValueStateDescriptor("seen", Types.BOOLEAN())
        desc.enable_time_to_live(StateTtlConfig.new_builder(Time.hours(1)).build())
        self.seen = runtime_context.get_state(desc)

    def process_element(self, value, ctx):
        if self.seen.value() is None:
            self.seen.update(True)
            yield value


def kafka_source(topic: str) -> KafkaSource:
    """Kafka source đọc chuỗi JSON; lần đầu đọc từ đầu để replay, restart thì lấy offset từ checkpoint."""
    return (KafkaSource.builder().set_bootstrap_servers(os.environ.get("KAFKA_BOOTSTRAP", "kafka:9092")).set_topics(topic)
            .set_group_id(f"flink-{topic}").set_starting_offsets(KafkaOffsetsInitializer.earliest())
            .set_value_only_deserializer(SimpleStringSchema()).build())


def kafka_sink(topic: str) -> KafkaSink:
    return (KafkaSink.builder().set_bootstrap_servers(os.environ.get("KAFKA_BOOTSTRAP", "kafka:9092"))
            .set_record_serializer(KafkaRecordSerializationSchema.builder().set_topic(topic)
                                   .set_value_serialization_schema(SimpleStringSchema()).build()).build())


def jdbc_sink(sql: str, row_type):
    """Upsert vào Postgres; at-least-once của JDBC + upsert theo khoá = ghi lại không làm sai kết quả."""
    conn = (JdbcConnectionOptions.JdbcConnectionOptionsBuilder().with_url(os.environ["FEAT_JDBC_URL"])
            .with_driver_name("org.postgresql.Driver").with_user_name(os.environ["FEAT_JDBC_USER"])
            .with_password(os.environ["FEAT_JDBC_PASSWORD"]).build())
    opts = JdbcExecutionOptions.builder().with_batch_interval_ms(1000).with_batch_size(500).with_max_retries(3).build()
    return JdbcSink.sink(sql, row_type, conn, opts)


def main() -> None:
    """booking_created -> sliding 1h (feature) + tumbling 1 phút (đối soát, side output); payment_callback -> dedup."""
    env = StreamExecutionEnvironment.get_execution_environment()
    if os.environ.get("FLINK_PARALLELISM"):          # chạy local: mặc định = số core, nhiều hơn số partition Kafka
        env.set_parallelism(int(os.environ["FLINK_PARALLELISM"]))
    env.enable_checkpointing(60_000, CheckpointingMode.EXACTLY_ONCE)
    wm = WatermarkStrategy.for_bounded_out_of_orderness(MAX_OUT_OF_ORDER).with_timestamp_assigner(EventTimeAssigner())
    # Đo trên PyFlink 1.20.1 (tests/test_stream_e2e.py): WatermarkStrategy đưa vào from_source bỏ qua TimestampAssigner
    # viết bằng Python (dùng timestamp Kafka = giờ produce) và with_idleness làm watermark đứng yên -> gán timestamp ngay
    # sau source, không idleness. Vì vậy parallelism không được vượt số partition Kafka: subtask không có partition
    # nào giữ watermark ở mức thấp nhất và mọi window đứng chờ (FlinkDeployment 2 <= 6 partition).
    raw = env.from_source(kafka_source("booking_events"), WatermarkStrategy.no_watermarks(), "booking_events")              .assign_timestamps_and_watermarks(wm)
    events = raw.process(ContractCheck(), Types.STRING())
    events.get_side_output(DLQ_TAG).sink_to(kafka_sink(DLQ_TOPIC))

    created = events.filter(lambda v: json.loads(v)["type"] == "booking_created")
    if not BASELINE:                             # double submit: 2 booking_id, cùng idempotency_key -> đếm 1 lần như Silver
        created = created.key_by(lambda v: json.loads(v)["idempotency_key"], key_type=Types.LONG()) \
                         .process(DedupByEventId(), Types.STRING())
    by_hotel = created.key_by(lambda v: json.loads(v)["hotel_id"], key_type=Types.LONG())
    (by_hotel.window(SlidingEventTimeWindows.of(Time.hours(1), Time.minutes(5)))
     .allowed_lateness(ALLOWED_LATENESS_MS)
     .process(CountPerWindow(), FEAT_ROW)
     .add_sink(jdbc_sink(UPSERT_SQL, FEAT_ROW)))
    minutes = (by_hotel.window(TumblingEventTimeWindows.of(Time.minutes(1)))
               .allowed_lateness(ALLOWED_LATENESS_MS)
               .side_output_late_data(LATE_TAG)
               .process(CountPerWindow(), FEAT_ROW))
    minutes.add_sink(jdbc_sink(MINUTE_SQL, FEAT_ROW))
    # trễ hơn watermark + allowedLateness: không mất, ghi lại để đối soát
    minutes.get_side_output(LATE_TAG).map(late_row, LATE_ROW).add_sink(jdbc_sink(LATE_SQL, LATE_ROW))

    callbacks = events.filter(lambda v: json.loads(v)["type"] == "payment_callback")
    if not BASELINE:
        callbacks = callbacks.key_by(lambda v: json.loads(v)["event_id"], key_type=Types.LONG()) \
                             .process(DedupByEventId(), Types.STRING())
    callbacks.print()

    env.execute("booking_events_window")


if __name__ == "__main__":
    main()
