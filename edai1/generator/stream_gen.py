"""Sinh event log cho booking app rồi phát lại vào Kafka theo đồng hồ giả lập.

Rubric edai-1 › Implement Data Generator › Simulate online data problems:
  - Simulate late arrivals         : ingest_time = event_time + độ trễ theo nguồn: mobile offline 5-20 phút
                                     (vượt watermark 10 phút + allowedLateness 5 phút -> có event vào side output),
                                     booking qua channel manager 1-4 giờ, webhook thanh toán 1-15 phút
  - Another streaming data problem : 1.5% payment_callback gửi 2 lần, cùng event_id (at-least-once)
Tái lập: event được SINH trước (ghi Parquet, sắp theo ingest_time) và PHÁT sau; tốc độ phát chỉ đổi thời
điểm đến Kafka, không đổi nội dung event. Không đọc giờ thật khi sinh.
Một thế giới với batch: event dựng từ CHÍNH các dòng gen_bookings của ngày đó (cùng booking_id, giá, checkin,
nhãn huỷ); các ngày 365–394 cũng được offline_gen ghi ra landing như lô batch của ngày hôm sau.
"""
import heapq
import json
import multiprocessing as mp
import os
import sys
import time

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from kafka import KafkaProducer

from generator.offline_gen import cancellations, gen_bookings, gen_dims, gen_quotes, load_config, partition_rng

EVENT_DIR = os.environ.get("EVENT_DIR", "/data/events")
TOPIC = "booking_events"
QUOTE_TOPIC = "quotes"                                   # tách topic: lượng quote lớn không làm chậm nhánh booking
TYPE_CODE = {"booking_created": 0, "payment_callback": 1, "booking_cancelled": 2, "quote": 3}
INVALID_CODE = 4                                         # event_id của bản sao lỗi: không trùng event thật
VIOLATIONS = ("price", "hotel_id", "event_time")         # = reason của flink_jobs/contract.py
TOPICS = os.environ.get("STREAM_TOPICS", f"{TOPIC},{QUOTE_TOPIC}").split(",")   # chỉ phát booking: STREAM_TOPICS=booking_events
GEN_WORKERS = int(os.environ.get("GEN_WORKERS", os.cpu_count() or 1))   # số process sinh event log lần đầu
_DIMS = None                                             # dims của process cha, process con fork dùng chung (copy-on-write)


def _delay_ms(rng: np.random.Generator, n: int, share: float, min_s: int, max_s: int) -> np.ndarray:
    """Độ trễ (ms): share phần trăm event bị trễ trong [min_s, max_s], phần còn lại trễ < 1 giây."""
    late = rng.random(n) < share
    return np.where(late, rng.uniform(min_s, max_s, n) * 1000, rng.exponential(300, n)).astype(np.int64)


def _ms(ts: pd.Series) -> np.ndarray:
    """Timestamp (naive, coi là UTC) -> epoch milliseconds."""
    return ts.values.astype("datetime64[ms]").astype(np.int64)


def gen_events(cfg: dict, dims, day_idx: int, shard: int) -> pd.DataFrame:
    """Dựng event của 1 partition từ đúng 2 bảng landing của nó: booking_created <-> dòng bookings,
    booking_cancelled <-> dòng cancellations. event_time là lúc xảy ra, ingest_time là lúc tới Kafka."""
    s = cfg["stream"]
    b = gen_bookings(cfg, dims, day_idx, shard).rename(columns={"room_type": "room_category"})
    rng = partition_rng(cfg, day_idx, shard, "events")
    n = len(b)
    created = _ms(b["created_at"])
    late = s["late"]
    cm = late["channel_manager"]                                   # booking từ OTA khác qua channel manager: tới trễ 1-4 giờ
    device = b["channel"].values                                   # channel của chính booking (cột của landing v2)
    base = pd.DataFrame({                                          # đủ cột để Flink tính window theo hotel × stay_date
        "booking_id": b["booking_id"].values,
        "idempotency_key": b["idempotency_key"].values,
        "customer_id": b["customer_id"].values,
        "hotel_id": b["hotel_id"].values,
        "room_category": b["room_category"].values,
        "checkin": b["checkin"].dt.strftime("%Y-%m-%d").values,
        "nights": b["nights"].values,
        "price": b["price"].values,
        "device": device,
    })

    mo = late["mobile_offline"]
    delay = np.select([device == "mobile", device == "channel_manager"],
                      [_delay_ms(rng, n, mo["share"], mo["min_s"], mo["max_s"]), _delay_ms(rng, n, 1.0, cm["min_s"], cm["max_s"])],
                      _delay_ms(rng, n, 0.0, 0, 0))
    created_ev = base.assign(type="booking_created", event_time=created, ingest_time=created + delay)

    first = ~b["idempotency_key"].duplicated().values             # 1 payment / idempotency_key, như gen_payments
    paid = created[first] + rng.integers(5_000, 120_000, first.sum())
    webhook = late["payment_webhook"]
    pay_ev = base[first].assign(type="payment_callback", event_time=paid,
                                ingest_time=paid + (rng.uniform(webhook["min_s"], webhook["max_s"], first.sum())
                                                    * 1000).astype(np.int64))
    dup = pay_ev[rng.random(len(pay_ev)) < s["callback_dup_rate"]].copy()
    dup["ingest_time"] += rng.integers(1_000, 30_000, len(dup))    # bản gửi lại tới sau vài giây

    c = cancellations(b)                                           # cùng hàm sinh bảng cancellations trên landing
    cancel_at = _ms(c["cancelled_at"])
    cancel_ev = base.set_index("booking_id").loc[c["booking_id"]].reset_index().assign(
        type="booking_cancelled", event_time=cancel_at, ingest_time=cancel_at + _delay_ms(rng, len(c), 0.0, 0, 0))

    # data contract: bản sao lỗi của vài booking_created (producer hỏng), event thật giữ nguyên nên stream = landing
    # vẫn đúng; violation = trường bị làm sai, replay bỏ trường event_time khỏi payload khi violation = event_time
    bad = created_ev[rng.random(n) < cfg["anomalies"]["contract_violation_share"]].copy()
    bad["violation"] = rng.choice(VIOLATIONS, len(bad))
    bad.loc[bad["violation"] == "price", "price"] *= -1
    bad.loc[bad["violation"] == "hotel_id", "hotel_id"] = 0

    ev = pd.concat([created_ev, pay_ev, dup, cancel_ev, bad], ignore_index=True)
    ev["event_id"] = ev["booking_id"] * 10 + ev["type"].map(TYPE_CODE)   # bản trùng giữ nguyên event_id
    ev.loc[ev["violation"].notna(), "event_id"] = ev["booking_id"] * 10 + INVALID_CODE
    return ev.sort_values(["ingest_time", "event_id"], kind="stable").reset_index(drop=True)


def gen_quote_events(cfg: dict, dims, day_idx: int, shard: int) -> pd.DataFrame:
    """Event của bảng quotes (log phía server: tới Kafka gần như ngay, không trễ kiểu mobile)."""
    q = gen_quotes(cfg, dims, day_idx, shard)
    rng = partition_rng(cfg, day_idx, shard, "events")
    t = _ms(q["quoted_at"])
    ev = pd.DataFrame({
        "quote_id": q["quote_id"].values, "hotel_id": q["hotel_id"].values, "room_type": q["room_type"].values,
        "stay_date": q["stay_date"].dt.strftime("%Y-%m-%d").values, "rate_plan": q["rate_plan"].values,
        "price": q["price"].values, "available": q["available"].values, "booked": q["booked"].values,
        "type": "quote", "event_time": t, "ingest_time": t + _delay_ms(rng, len(q), 0.0, 0, 0),
        "event_id": q["quote_id"].values * 10 + TYPE_CODE["quote"],
    })
    return ev.sort_values(["ingest_time", "event_id"], kind="stable").reset_index(drop=True)


DAY_MS = 86_400_000


def _window_events(args: tuple) -> pd.DataFrame:
    """Event của 1 partition (ngày tạo, shard) có ingest_time trong cửa sổ [start, end)."""
    cfg, day_idx, shard, start, end = args
    ev = gen_events(cfg, _DIMS, day_idx, shard)
    return ev[(ev["ingest_time"] >= start) & (ev["ingest_time"] < end)]


def write_event_log(cfg: dict, first_day: int, last_day: int) -> dict[int, list[str]]:
    """Sinh event log cho cửa sổ [first_day, last_day), gom theo NGÀY INGEST để replay mỗi ngày chỉ mở vài file.
    - booking: sinh partition của các ngày tạo [first_day - cancel_lookback_days, last_day) (lùi lại để có event huỷ
      của booking tạo trước cửa sổ), giữ event có ingest_time trong cửa sổ, ghi nối vào 1 file / ngày ingest rồi sắp lại;
    - quote: 1 file / (ngày, shard) cho [first_day - 1, last_day) (quote tới Kafka gần như ngay, chỉ tràn qua nửa đêm).
    Trả {ngày ingest: [file]}. Có file _DONE thì dùng lại; đổi config.yaml thì xoá EVENT_DIR.
    Lần đầu (~2.900 partition) sinh song song GEN_WORKERS process (fork, Linux); imap giữ thứ tự nên file ra như chạy
    tuần tự. Windows không fork được thì chạy tuần tự."""
    import pyarrow as pa
    global _DIMS
    _DIMS = dims = gen_dims(cfg)
    start, end = window_ms(cfg, first_day, last_day)
    bdir = f"{EVENT_DIR}/bookings_{first_day}_{last_day}"
    if not os.path.exists(f"{bdir}/_DONE"):
        os.makedirs(bdir, exist_ok=True)
        writers = {}
        tasks = [(cfg, d, s, start, end) for d in range(max(first_day - cfg["cancel_lookback_days"], 0), last_day)
                 for s in range(cfg["shards_per_day"])]
        pool = mp.get_context("fork").Pool(GEN_WORKERS) if GEN_WORKERS > 1 and hasattr(os, "fork") else None
        try:
            for ev in (pool.imap(_window_events, tasks) if pool else map(_window_events, tasks)):
                for iday, g in ev.groupby(first_day + (ev["ingest_time"] - start) // DAY_MS):
                    t = pa.Table.from_pandas(g, preserve_index=False)
                    if iday not in writers:
                        writers[iday] = pq.ParquetWriter(f"{bdir}/day={iday:04d}.unsorted.parquet", t.schema)
                    writers[iday].write_table(t.cast(writers[iday].schema))
        finally:
            if pool:
                pool.close()
        for iday, w in writers.items():                        # sắp lại theo (ingest_time, event_id) cho heapq.merge
            w.close()
            tmp = f"{bdir}/day={iday:04d}.unsorted.parquet"
            df = pd.read_parquet(tmp).sort_values(["ingest_time", "event_id"], kind="stable")
            df.to_parquet(f"{bdir}/day={iday:04d}.parquet", index=False)
            os.remove(tmp)
        open(f"{bdir}/_DONE", "w").close()
    files = {d: [f"{bdir}/day={d:04d}.parquet"] for d in range(first_day, last_day)
             if os.path.exists(f"{bdir}/day={d:04d}.parquet")}
    if QUOTE_TOPIC in TOPICS:
        for day_idx in range(max(first_day - 1, 0), last_day):
            for shard in range(cfg["shards_per_day"]):
                path = f"{EVENT_DIR}/quotes/day={day_idx:04d}/shard={shard:02d}.parquet"
                if not os.path.exists(path):
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                    gen_quote_events(cfg, dims, day_idx, shard).to_parquet(path, index=False)
                for d in (day_idx, day_idx + 1):              # quote cuối ngày có thể ingest sang ngày sau
                    if first_day <= d < last_day:
                        files.setdefault(d, []).append(path)
    return files


def iter_rows(path: str):
    """Đọc 1 file event log theo thứ tự đã sắp (ingest_time, event_id), từng lô 10k dòng."""
    for batch in pq.ParquetFile(path).iter_batches(batch_size=10_000):
        yield from batch.to_pylist()


def window_ms(cfg: dict, first_day: int, last_day: int) -> tuple[int, int]:
    """Cửa sổ phát [đầu ngày first_day, đầu ngày last_day) theo ingest_time, tính bằng epoch ms."""
    start = pd.Timestamp(cfg["start_date"])
    return tuple(int((start + pd.Timedelta(days=d)).timestamp() * 1000) for d in (first_day, last_day))


def replay(cfg: dict, files: dict[int, list[str]], speed: float, first_day: int, last_day: int) -> None:
    """Phát từng ngày ingest theo thứ tự; trong ngày gộp các file theo (ingest_time, event_id) và chỉ phát event có
    ingest_time trong ngày đó. speed=60: 1 phút giả lập = 1 giây thật; speed=0: phát nhanh nhất có thể."""
    producer = KafkaProducer(
        bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP", "kafka:9092"),
        value_serializer=lambda v: json.dumps(v).encode(),
        key_serializer=lambda k: k.encode(),
    )
    t0_sim, t0_wall = None, time.monotonic()
    for day in range(first_day, last_day):
        lo, hi = window_ms(cfg, day, day + 1)
        for r in heapq.merge(*(iter_rows(p) for p in files.get(day, [])), key=lambda r: (r["ingest_time"], r["event_id"])):
            if not lo <= r["ingest_time"] < hi:
                continue
            if t0_sim is None:
                t0_sim = r["ingest_time"]
            if speed > 0:
                wait = (r["ingest_time"] - t0_sim) / 1000 / speed - (time.monotonic() - t0_wall)
                if wait > 0:
                    time.sleep(wait)
            topic = QUOTE_TOPIC if r["type"] == "quote" else TOPIC
            if topic not in TOPICS:
                continue
            # Flink chỉ thấy event_time; nhãn violation là ground truth để đối soát DLQ, không phát đi
            drop = {"ingest_time", "violation"} | ({"event_time"} if r.get("violation") == "event_time" else set())
            payload = {k: v for k, v in r.items() if k not in drop and v is not None}
            producer.send(topic, key=str(r["hotel_id"]), value=payload)
    producer.flush()


if __name__ == "__main__":
    first, last, spd = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3])
    config = load_config(os.environ.get("GENERATOR_CONFIG", "generator/config.yaml"))   # test e2e dùng config thu nhỏ
    replay(config, write_event_log(config, first, last), spd, first, last)
