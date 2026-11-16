"""DP2 (sql/dp2_upsert_gold.sql) và DP3 (sql/dp3_features.sql) trên PostgreSQL thật (Docker, image pgvector như GKE).

Staging dựng từ generator đúng như stage_gold.py ghi: booking (đã dedup theo idempotency_key) tạo hoặc huỷ trong
ngày ds, khách của chúng, mọi lần đổi giá có hiệu lực tới ds. Chạy tuần tự từng ngày như Airflow.
  - SCD2      : mỗi khách sạn có 1 + số lần đổi giá tới ds phiên bản, đúng 1 bản hiện hành; fact trỏ đúng phiên bản
  - Fact      : đủ booking, status khớp kết cục generator tới ds, chạy lại cùng ngày không đổi gì
  - Nhãn      : view labels_cancel 2 cột
  - DP3       : feature khớp tính lại bằng pandas; mọi check validate của DAG (dags/gold_checks.py) đều đúng
Cần Docker; chạy: pytest tests/test_gold_sql.py"""
import shutil
import subprocess
import sys
import time
import uuid

import pandas as pd
import pytest

psycopg = pytest.importorskip("psycopg")
if not shutil.which("docker") or subprocess.run(["docker", "info"], capture_output=True).returncode:
    pytest.skip("cần Docker", allow_module_level=True)
sys.path.insert(0, "dags")

from generator.offline_gen import gen_bookings, gen_dims, load_config  # noqa: E402
from gold_checks import FEATURE_CHECKS, GOLD_CHECKS  # noqa: E402

START = pd.Timestamp("2025-01-01")
DAYS = range(0, 40)


@pytest.fixture(scope="module")
def pg():
    name, port = f"gold-test-{uuid.uuid4().hex[:8]}", 55432
    subprocess.run(["docker", "run", "-d", "--rm", "--name", name, "-e", "POSTGRES_PASSWORD=test", "-e", "POSTGRES_DB=warehouse",
                    "-p", f"{port}:5432", "pgvector/pgvector:pg17"], check=True, capture_output=True)
    dsn = f"postgresql://postgres:test@localhost:{port}/warehouse"
    try:
        for _ in range(60):
            try:
                conn = psycopg.connect(dsn, autocommit=True)
                break
            except psycopg.OperationalError:
                time.sleep(1)
        conn.execute(open("schema/gold_schema.sql", encoding="utf-8").read())
        yield conn
        conn.close()
    finally:
        subprocess.run(["docker", "rm", "-f", name], capture_output=True)


@pytest.fixture(scope="module")
def world():
    cfg = load_config("generator/config.yaml")
    cfg["dims"] = {"hotels": 200, "customers": 3000}
    cfg["shards_per_day"] = 2
    dims = gen_dims(cfg)
    b = pd.concat([gen_bookings(cfg, dims, d, s) for d in DAYS for s in range(2)], ignore_index=True)
    b = b.sort_values(["created_at", "booking_id"]).drop_duplicates("idempotency_key")      # = dedup ở Silver
    return dims, b


def copy(conn, table: str, df: pd.DataFrame) -> None:
    conn.execute(f"TRUNCATE {table}")
    with conn.cursor().copy(f"COPY {table} ({', '.join(df.columns)}) FROM STDIN") as cp:
        for row in df.itertuples(index=False):
            cp.write_row([None if pd.isna(v) else v for v in row])


def stage(conn, dims, b: pd.DataFrame, ds: pd.Timestamp) -> None:
    day = ds.normalize()
    changed = b[(b["created_at"].dt.normalize() == day) | (b["cancelled_at"].dt.normalize() == day)].copy()
    changed["cancelled_at"] = changed["cancelled_at"].where(changed["cancelled_at"] < day + pd.Timedelta(days=1))
    changed["status"] = changed["cancelled_at"].notna().map({True: "cancelled", False: "confirmed"})
    copy(conn, "gold.stg_bookings", changed[["booking_id", "customer_id", "hotel_id", "created_at", "checkin", "nights",
                                             "price", "cancellation_policy", "channel", "status", "cancelled_at"]])
    cust = dims.customers[dims.customers["customer_id"].isin(changed["customer_id"])]
    copy(conn, "gold.stg_customers", cust.assign(home_city=cust["home_city"].astype(str))[
        ["customer_id", "home_city", "loyalty_tier"]])
    ch = dims.hotel_changes[dims.hotel_changes["valid_from"] <= day].merge(dims.hotels[["hotel_id", "city", "stars"]])
    copy(conn, "gold.stg_hotel_changes", ch[["hotel_id", "city", "stars", "price", "valid_from"]])


def run_day(conn, dims, b, d: int) -> str:
    ds = START + pd.Timedelta(days=d)
    stage(conn, dims, b, ds)
    conn.execute(open("sql/dp2_upsert_gold.sql", encoding="utf-8").read())
    conn.execute(open("sql/dp3_features.sql", encoding="utf-8").read().replace("{{ ds }}", f"{ds:%Y-%m-%d}"))
    return f"{ds:%Y-%m-%d}"


@pytest.fixture(scope="module")
def loaded(pg, world):
    dims, b = world
    for d in DAYS:
        run_day(pg, dims, b, d)
    return pg, dims, b


def q(conn, sql: str):
    return conn.execute(sql).fetchall()


def test_fact_matches_generator(loaded):
    conn, _, b = loaded
    end = START + pd.Timedelta(days=DAYS.stop)
    fact = pd.DataFrame(q(conn, "SELECT booking_id, status FROM gold.fact_bookings"), columns=["booking_id", "status"])
    want = b[b["created_at"] < end]
    assert set(fact["booking_id"]) == set(want["booking_id"])
    cancelled = set(want.loc[want["cancelled_at"] < end, "booking_id"])
    assert set(fact.loc[fact["status"] == "cancelled", "booking_id"]) == cancelled and cancelled


def test_scd2_versions_and_fact_points_to_version_at_booking(loaded):
    conn, dims, _ = loaded
    end = START + pd.Timedelta(days=DAYS.stop - 1)
    versions = dict(q(conn, "SELECT hotel_id, count(*) FROM gold.dim_hotel GROUP BY hotel_id"))
    want = dims.hotel_changes[dims.hotel_changes["valid_from"] <= end].groupby("hotel_id").size()
    assert versions == want.to_dict() and max(versions.values()) >= 3            # có khách sạn đổi giá >= 2 lần
    assert q(conn, "SELECT count(*) FROM gold.dim_hotel WHERE is_current")[0][0] == len(want)
    bad = q(conn, """SELECT count(*) FROM gold.fact_bookings f JOIN gold.dim_hotel h USING (hotel_key)
                     JOIN gold.stg_bookings s USING (booking_id)
                     WHERE NOT (s.created_at >= h.valid_from_ts AND s.created_at < h.valid_to_ts)""")[0][0]
    assert bad == 0


def test_rerun_same_day_is_idempotent(loaded):
    conn, dims, b = loaded
    snap = lambda: q(conn, "SELECT (SELECT count(*) FROM gold.fact_bookings), (SELECT count(*) FROM gold.dim_hotel), "
                           "(SELECT count(*) FROM gold.feat_customer_booking_stats), (SELECT count(*) FROM gold.feat_hotel_demand)")
    before = snap()
    run_day(conn, dims, b, DAYS.stop - 1)
    assert snap() == before


def test_labels_view(loaded):
    conn, _, _ = loaded
    cols = [c.name for c in conn.execute("SELECT * FROM gold.labels_cancel LIMIT 1").description]
    assert cols == ["booking_id", "is_cancelled"]
    assert q(conn, "SELECT count(*) FROM gold.labels_cancel")[0][0] == q(conn, "SELECT count(*) FROM gold.fact_bookings")[0][0]


def test_hotel_features_match_pandas(loaded):
    conn, dims, b = loaded
    ds = START + pd.Timedelta(days=DAYS.stop - 1)
    got = pd.DataFrame(q(conn, f"SELECT hotel_id, bookings_7d, cancel_rate_30d FROM gold.feat_hotel_demand "
                               f"WHERE event_timestamp = '{ds + pd.Timedelta(days=1):%Y-%m-%d}'"),
                       columns=["hotel_id", "bookings_7d", "cancel_rate_30d"]).set_index("hotel_id").sort_index()
    day = b["created_at"].dt.normalize()
    w30 = b[(day > ds - pd.Timedelta(days=30)) & (day <= ds)]
    want = pd.DataFrame({
        "bookings_7d": w30[w30["created_at"].dt.normalize() > ds - pd.Timedelta(days=7)].groupby("hotel_id").size(),
        "cancel_rate_30d": (w30["cancelled_at"] < ds + pd.Timedelta(days=1)).groupby(w30["hotel_id"]).mean(),
    }).fillna({"bookings_7d": 0}).sort_index()
    assert list(got.index) == list(want.index)
    assert (got["bookings_7d"].values == want["bookings_7d"].values).all()
    assert ((got["cancel_rate_30d"].astype(float) - want["cancel_rate_30d"]).abs() < 1e-4).all()


def test_dag_validation_checks_pass(loaded):
    conn, _, _ = loaded
    ds = f"{START + pd.Timedelta(days=DAYS.stop - 1):%Y-%m-%d}"
    for name, sql in {**GOLD_CHECKS, **FEATURE_CHECKS}.items():
        assert q(conn, sql.format(ds=ds))[0][0] is True, name
