"""E2E nhánh stream trên Docker: replayer -> Kafka -> Flink booking_events_window (image k8s/flink.Dockerfile) -> Postgres.

Novelty edai-1 (đối soát có ground truth): ground truth tính lại từ generator trên host bằng đúng config thu nhỏ.
  - Đối soát : mỗi phút đã đóng, gold.stream_bookings_1m + gold.stream_late_bookings = số booking_created (đúng contract,
               dedup idempotency_key theo thứ tự tới Kafka) có event_time trong phút đó
  - DLQ      : số event trên booking_events_dlq theo reason = số bản sao lỗi generator cài theo loại
  - Feature  : gold.feat_hotel_realtime có dòng (sliding 1h / 5 phút)
Cần Docker + image booking-generator:multistage, booking-flink:local; chạy: pytest tests/test_stream_e2e.py (~5 phút).
Phút cuối cửa sổ chưa đóng (watermark đứng khi source idle) nên chỉ đối soát tới max(event_time) - 20 phút.
"""
import json
import os
import shutil
import subprocess
import time
import uuid

import pandas as pd
import pytest
import yaml

if not shutil.which("docker") or subprocess.run(["docker", "info"], capture_output=True).returncode:
    pytest.skip("cần Docker", allow_module_level=True)
for img in ("booking-generator:multistage", "booking-flink:local"):
    if subprocess.run(["docker", "image", "inspect", img], capture_output=True).returncode:
        pytest.skip(f"cần image {img}", allow_module_level=True)
psycopg = pytest.importorskip("psycopg")

from generator.offline_gen import gen_dims, load_config  # noqa: E402
from generator.stream_gen import gen_events, window_ms  # noqa: E402

DAY = (365, 366)
ID = uuid.uuid4().hex[:6]
NET, KAFKA, PG, FLINK = f"e2e-{ID}", f"kafka-{ID}", f"pg-{ID}", f"flink-{ID}"
PG_PORT = 55433


def sh(*args, check=True, **kw):
    return subprocess.run(["docker", *args], check=check, capture_output=True, text=True, **kw)


def small_config(tmp) -> str:
    cfg = yaml.safe_load(open("generator/config.yaml", encoding="utf-8"))
    cfg["dims"] = {"hotels": 200, "customers": 3000}
    cfg["shards_per_day"] = 2
    cfg["cancel_lookback_days"] = 20
    path = os.path.join(tmp, "config.yaml")
    yaml.safe_dump(cfg, open(path, "w", encoding="utf-8"), allow_unicode=True)
    return path


@pytest.fixture(scope="module")
def stack(tmp_path_factory):
    tmp = str(tmp_path_factory.mktemp("e2e"))
    cfg_path = small_config(tmp)
    sh("network", "create", NET)
    try:
        sh("run", "-d", "--rm", "--name", KAFKA, "--network", NET, "--network-alias", "kafka",
           "-e", "KAFKA_CFG_NODE_ID=0", "-e", "KAFKA_CFG_PROCESS_ROLES=controller,broker",
           "-e", "KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093",
           "-e", "KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=0@kafka:9093", "-e", "KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER",
           "-e", "KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092", "bitnamilegacy/kafka:3.7")
        sh("run", "-d", "--rm", "--name", PG, "--network", NET, "--network-alias", "pg", "-p", f"{PG_PORT}:5432",
           "-e", "POSTGRES_PASSWORD=test", "-e", "POSTGRES_DB=warehouse", "pgvector/pgvector:pg17")
        dsn = f"postgresql://postgres:test@localhost:{PG_PORT}/warehouse"
        for _ in range(60):
            try:
                conn = psycopg.connect(dsn, autocommit=True)
                break
            except psycopg.OperationalError:
                time.sleep(1)
        conn.execute(open("schema/gold_schema.sql", encoding="utf-8").read())
        for _ in range(60):                                                  # Kafka KRaft sẵn sàng
            r = sh("exec", KAFKA, "kafka-topics.sh", "--bootstrap-server", "localhost:9092", "--list", check=False)
            if r.returncode == 0:
                break
            time.sleep(2)
        for topic, parts, extra in (("booking_events", 3, []),
                                    ("booking_events_dlq", 1, ["--config", "message.timestamp.type=LogAppendTime"])):
            sh("exec", KAFKA, "kafka-topics.sh", "--bootstrap-server", "localhost:9092", "--create", "--topic", topic,
               "--partitions", str(parts), "--replication-factor", "1", *extra)
        # replay 1 ngày, nhanh nhất có thể, chỉ topic booking_events
        sh("run", "--rm", "--network", NET, "-v", f"{tmp}:/cfg", "-e", "GENERATOR_CONFIG=/cfg/config.yaml",
           "-e", "KAFKA_BOOTSTRAP=kafka:9092", "-e", "EVENT_DIR=/tmp/events", "-e", "STREAM_TOPICS=booking_events",
           "--entrypoint", "python", "booking-generator:multistage", "-m", "generator.stream_gen",
           str(DAY[0]), str(DAY[1]), "0", timeout=900)
        # không --rm: container dừng vì lỗi vẫn còn để đọc log
        sh("run", "-d", "--name", FLINK, "--network", NET, "-e", "KAFKA_BOOTSTRAP=kafka:9092", "-e", "FLINK_PARALLELISM=3",
           "-e", "FEAT_JDBC_URL=jdbc:postgresql://pg:5432/warehouse", "-e", "FEAT_JDBC_USER=postgres",
           "-e", "FEAT_JDBC_PASSWORD=test", "--entrypoint", "python", "booking-flink:local",
           "/opt/flink/usrlib/booking_events_window.py")
        last, stable = -1, 0
        for _ in range(90):              # đợi số dòng đứng yên 90 giây: qua ít nhất 1 checkpoint (DLQ sink flush khi checkpoint)
            time.sleep(10)
            n = conn.execute("SELECT (SELECT coalesce(sum(bookings), 0) FROM gold.stream_bookings_1m)"
                             " + (SELECT count(*) FROM gold.stream_late_bookings)").fetchone()[0]
            stable = stable + 1 if n == last and n > 0 else 0
            last = n
            if stable >= 9:
                break
        yield conn, load_config(cfg_path)
        logs = sh("logs", "--tail", "40", FLINK, check=False)
        print(logs.stdout[-4000:], logs.stderr[-4000:])
        conn.close()
    finally:
        for c in (FLINK, KAFKA, PG):
            sh("rm", "-f", c, check=False)
        sh("network", "rm", NET, check=False)


@pytest.fixture(scope="module")
def truth(stack):
    _, cfg = stack
    dims = gen_dims(cfg)
    start, end = window_ms(cfg, *DAY)
    ev = pd.concat([gen_events(cfg, dims, d, s) for d in range(DAY[0] - cfg["cancel_lookback_days"], DAY[1])
                    for s in range(cfg["shards_per_day"])], ignore_index=True)
    ev = ev[(ev["ingest_time"] >= start) & (ev["ingest_time"] < end)].sort_values(["ingest_time", "event_id"])
    return ev


def test_minute_reconciliation(stack, truth):
    conn, _ = stack
    created = truth[(truth["type"] == "booking_created") & truth["violation"].isna()].drop_duplicates("idempotency_key")
    want = (created["event_time"] // 60_000 + 1).value_counts()             # window_end (phút) của từng event
    got = pd.DataFrame(conn.execute("SELECT (extract(epoch FROM window_end) / 60)::bigint, bookings "
                                    "FROM gold.stream_bookings_1m").fetchall(), columns=["m", "n"]).groupby("m")["n"].sum()
    late = pd.Series([r[0] for r in conn.execute(
        "SELECT (extract(epoch FROM event_time) * 1000)::bigint / 60000 + 1 FROM gold.stream_late_bookings").fetchall()])
    got = got.add(late.value_counts(), fill_value=0)
    cutoff = created["event_time"].max() // 60_000 - 20
    idx = want.index.union(got.index)
    diff = pd.DataFrame({"want": want.reindex(idx, fill_value=0), "got": got.reindex(idx, fill_value=0)})
    diff = diff[diff.index <= cutoff]
    bad = diff[diff["want"] != diff["got"]]
    assert len(diff) > 100 and bad.empty, f"{len(bad)} phút lệch:\n{bad.head(20)}"


def test_dlq_matches_injected_violations(stack, truth):
    raw = sh("exec", KAFKA, "kafka-console-consumer.sh", "--bootstrap-server", "localhost:9092", "--topic",
             "booking_events_dlq", "--from-beginning", "--timeout-ms", "10000", check=False).stdout
    got = pd.Series([json.loads(line)["reason"] for line in raw.splitlines() if line.startswith("{")]).value_counts()
    want = truth["violation"].dropna().value_counts()
    assert len(want) and got.sort_index().to_dict() == want.sort_index().to_dict()


def test_realtime_feature_written(stack):
    conn, _ = stack
    assert conn.execute("SELECT count(*) FROM gold.feat_hotel_realtime").fetchone()[0] > 0
