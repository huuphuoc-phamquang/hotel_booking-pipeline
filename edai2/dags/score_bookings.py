"""DAG chấm xác suất huỷ một lần cho mỗi booking, ngay sau ngày tạo, khi materialize đưa feature lên online store.

Rubric:
  - edai-2 › Feature Store › materialize -> serving : chạy theo Airflow Dataset ONLINE_BATCH của feast_materialize_incremental
  - edai-2 › ML Inference Service                    : gọi booking-mcp /v1/cancel-risk/batch (Feast online + KServe)
Kết quả ghi gold.booking_risk (1 dòng / booking): propose_overbooking cộng dồn booking còn giữ phòng theo
hotel × stay_date, drift_monitor so tỉ lệ huỷ dự báo với thực tế.
Chỉ chấm booking tạo trong ngày (không chấm lại mỗi ngày mọi booking sắp nhận phòng): request tới KServe khi đó có
phân phối lead_days như lúc train, drift-api (KS) không báo drift giả do booking lead dài bị gửi tới 30 lần.
shortcut: điểm không cập nhật khi feature của khách / khách sạn đổi sau ngày tạo; chấm lại theo lịch nếu cần.
DAG rescore_active (Jenkinsfile.ml gọi khi promote = 100): chấm lại mọi booking còn giữ phòng bằng bản vừa promote,
nếu không propose_overbooking vẫn cộng điểm của bản cũ cho các đêm sắp tới tới khi booking cũ nhận phòng hết.
Backfill quanh mốc drift (2025-06-01): online store mới, `feast materialize 2025-01-01T00:00:00 2025-05-15T00:00:00`
rồi backfill chuỗi DP (DP3 xong -> materialize -> score, tuần tự từng ngày):
  airflow dags backfill dp1_ingest_bronze -s 2025-05-15 -e 2025-06-15   (tương tự dp2_bronze_to_gold, dp3_offline_features)
Ngày chấm (as_of) lấy từ data_interval_end của run materialize gây ra event, không phải giờ máy.
Connection warehouse và Variable booking_mcp_url đặt trong Airflow.
"""
from datetime import datetime

from airflow.datasets import Dataset
from airflow.decorators import dag, task
from airflow.models import Variable

ONLINE_BATCH = Dataset("feast://online/batch")
BATCH = 1000                               # = max_length của BatchRequest trong booking-mcp
NEW_SQL = """
SELECT f.booking_id, h.hotel_id, f.checkin_date AS stay_date
FROM gold.fact_bookings f JOIN gold.dim_hotel h USING (hotel_key)
WHERE f.booking_date = %(as_of)s::date - 1                            -- tạo trong ngày ds (as_of = 0h ngày ds + 1)
  AND f.checkin_date >= %(as_of)s::date
  AND (f.cancelled_at IS NULL OR f.cancelled_at > %(as_of)s)          -- huỷ ngay trong ngày tạo thì không cần chấm
"""
# as_of = ngày chấm mới nhất đã có (giờ dữ liệu, không theo giờ máy); booking tạo trước đó, chưa nhận phòng, chưa huỷ.
# ~11 triệu dòng (389 nghìn booking/ngày × lead ~29 ngày): chia RESCORE_PARTS task song song theo booking_id.
ACTIVE_SQL = """
SELECT f.booking_id, h.hotel_id, f.checkin_date AS stay_date
FROM gold.fact_bookings f JOIN gold.dim_hotel h USING (hotel_key)
WHERE f.booking_date < %(as_of)s AND f.checkin_date >= %(as_of)s
  AND (f.cancelled_at IS NULL OR f.cancelled_at > %(as_of)s)
  AND f.booking_id %% %(parts)s = %(part)s
"""
RESCORE_PARTS = 8
CHUNK = 50_000                             # dòng / lần đọc từ server-side cursor: vừa worker Airflow 1Gi


def score_and_store(pg, df, scored_date, bulk: bool = False) -> int:
    """Chấm df (index booking_id, cột hotel_id, stay_date) theo lô 1000 qua booking-mcp, upsert gold.booking_risk.
    bulk=True: booking-mcp gọi cancel-risk-bulk (không KServe logger) để drift-api không nhận cả loạt chấm lại."""
    import httpx
    probs = {}                                           # booking_id -> (xác suất, model_version)
    with httpx.Client(base_url=Variable.get("booking_mcp_url"), timeout=60) as http:
        for i in range(0, len(df), BATCH):
            r = http.post("/v1/cancel-risk/batch", json={"booking_ids": df.index[i:i + BATCH].tolist(), "bulk": bulk})
            r.raise_for_status()
            probs.update({x["booking_id"]: (x["probability"], x["model_version"]) for x in r.json()["results"]})
    # missing = booking chưa lên online store (booking_attributes): chỉ ghi log
    print(f"{len(df) - len(probs)} booking chưa lên online store, không chấm")
    rows = [(b, int(df.at[b, "hotel_id"]), df.at[b, "stay_date"], p, scored_date, v) for b, (p, v) in probs.items()]
    pg.insert_rows("gold.booking_risk", rows,
                   ["booking_id", "hotel_id", "stay_date", "probability", "scored_date", "model_version"],
                   replace=True, replace_index=["booking_id", "scored_date"], executemany=True)
    return len(rows)


@dag(dag_id="score_bookings", start_date=datetime(2025, 1, 1), schedule=[ONLINE_BATCH], catchup=False,
     max_active_runs=1, tags=["serving"])
def score_bookings():

    @task
    def score(triggering_dataset_events=None) -> int:
        """Lấy booking tạo trong ngày, chấm qua booking-mcp, upsert gold.booking_risk."""
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        as_of = max(e.source_dag_run.data_interval_end for evs in triggering_dataset_events.values() for e in evs)
        pg = PostgresHook(postgres_conn_id="warehouse")
        df = pg.get_pandas_df(NEW_SQL, parameters={"as_of": as_of}).set_index("booking_id")
        return score_and_store(pg, df, as_of.date())

    score()


@dag(dag_id="rescore_active", start_date=datetime(2025, 1, 1), schedule=None, catchup=False, max_active_runs=1,
     tags=["serving"])
def rescore_active():
    """Chấm lại booking còn giữ phòng sau khi promote (canary 100%), qua cancel-risk-bulk (không logger, drift-api
    không thấy). RESCORE_PARTS task song song, mỗi task đọc phần của mình theo khối CHUNK dòng."""

    @task
    def as_of_date():
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        return str(PostgresHook(postgres_conn_id="warehouse").get_first(
            "SELECT max(scored_date) FROM gold.booking_risk")[0])

    @task
    def rescore(part: int, as_of: str) -> int:
        import pandas as pd
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        pg = PostgresHook(postgres_conn_id="warehouse")
        n = 0
        with pg.get_conn() as conn, conn.cursor(name=f"active_{part}") as cur:   # server-side: không kéo hết về worker
            cur.itersize = CHUNK
            cur.execute(ACTIVE_SQL, {"as_of": as_of, "parts": RESCORE_PARTS, "part": part})
            while rows := cur.fetchmany(CHUNK):
                df = pd.DataFrame(rows, columns=["booking_id", "hotel_id", "stay_date"]).set_index("booking_id")
                n += score_and_store(pg, df, as_of, bulk=True)
        return n

    rescore.partial(as_of=as_of_date()).expand(part=list(range(RESCORE_PARTS)))


score_bookings()
rescore_active()
