"""DAG chấm xác suất huỷ một lần cho mỗi booking, ngay sau ngày tạo, khi materialize đưa feature lên online store.

Rubric:
  - edai-2 › Feature Store › materialize -> serving : chạy theo Airflow Dataset ONLINE_BATCH của feast_materialize_incremental
  - final › Web API kéo dữ liệu                     : gọi risk-api /v1/cancel-risk/batch (Feast online + KServe)
Kết quả ghi gold.booking_risk (1 dòng / booking): propose_overbooking cộng dồn booking còn giữ phòng theo
hotel × stay_date, drift_monitor so tỉ lệ huỷ dự báo với thực tế.
Chỉ chấm booking tạo trong ngày (không chấm lại mỗi ngày mọi booking sắp nhận phòng): request tới KServe khi đó có
phân phối lead_days như lúc train, drift-api (KS) không báo drift giả do booking lead dài bị gửi tới 30 lần.
shortcut: điểm không cập nhật khi feature của khách / khách sạn đổi sau ngày tạo; chấm lại theo lịch nếu cần.
Backfill quanh mốc drift (2025-06-01): online store mới, `feast materialize 2025-01-01T00:00:00 2025-05-15T00:00:00`
rồi backfill chuỗi DP (DP3 xong -> materialize -> score, tuần tự từng ngày):
  airflow dags backfill dp1_ingest_bronze -s 2025-05-15 -e 2025-06-15   (tương tự dp2_bronze_to_gold, dp3_offline_features)
Ngày chấm (as_of) lấy từ data_interval_end của run materialize gây ra event, không phải giờ máy.
Connection warehouse và Variable risk_api_url đặt trong Airflow.
"""
from datetime import datetime

from airflow.datasets import Dataset
from airflow.decorators import dag, task
from airflow.models import Variable

ONLINE_BATCH = Dataset("feast://online/batch")
BATCH = 1000                               # = max_length của BatchRequest trong risk-api
NEW_SQL = """
SELECT f.booking_id, h.hotel_id, f.checkin_date AS stay_date
FROM gold.fact_bookings f JOIN gold.dim_hotel h USING (hotel_key)
WHERE f.booking_date = %(as_of)s::date - 1                            -- tạo trong ngày ds (as_of = 0h ngày ds + 1)
  AND f.checkin_date >= %(as_of)s::date
  AND (f.cancelled_at IS NULL OR f.cancelled_at > %(as_of)s)          -- huỷ ngay trong ngày tạo thì không cần chấm
"""


@dag(dag_id="score_bookings", start_date=datetime(2025, 1, 1), schedule=[ONLINE_BATCH], catchup=False,
     max_active_runs=1, tags=["serving"])
def score_bookings():

    @task
    def score(triggering_dataset_events=None) -> int:
        """Lấy booking tạo trong ngày, chấm theo lô 1000 qua risk-api, upsert gold.booking_risk."""
        import httpx
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        as_of = max(e.source_dag_run.data_interval_end for evs in triggering_dataset_events.values() for e in evs)
        pg = PostgresHook(postgres_conn_id="warehouse")
        df = pg.get_pandas_df(NEW_SQL, parameters={"as_of": as_of}).set_index("booking_id")
        probs = {}                                           # booking_id -> (xác suất, model_version)
        with httpx.Client(base_url=Variable.get("risk_api_url"), timeout=60) as http:
            for i in range(0, len(df), BATCH):
                r = http.post("/v1/cancel-risk/batch", json={"booking_ids": df.index[i:i + BATCH].tolist()})
                r.raise_for_status()
                probs.update({x["booking_id"]: (x["probability"], x["model_version"]) for x in r.json()["results"]})
        # missing = booking chưa lên online store (booking_attributes): chỉ ghi log, không có lần chấm sau
        print(f"{len(df) - len(probs)} booking chưa lên online store, không chấm")
        rows = [(b, int(df.at[b, "hotel_id"]), df.at[b, "stay_date"], p, as_of.date(), v)
                for b, (p, v) in probs.items()]
        pg.insert_rows("gold.booking_risk", rows,
                       ["booking_id", "hotel_id", "stay_date", "probability", "scored_date", "model_version"],
                       replace=True, replace_index=["booking_id", "scored_date"])
        return len(rows)

    score()


score_bookings()
