"""Ground truth của nhánh stream trên cluster, đọc thẳng event log replayer đã ghi (EVENT_DIR trên PVC event-log).

Cùng phép đối soát với tests/test_stream_e2e.py nhưng gom theo ngày event_time để so với Gold:
  created  : booking_created đúng contract, sau dedup idempotency_key (theo thứ tự tới Kafka)
             = sum(gold.stream_bookings_1m) + count(gold.stream_late_bookings) của ngày đó
  dup      : bản double submit bị dedup bỏ (BASELINE đếm cả các bản này)
  late_15m : booking_created tới trễ hơn 15 phút (watermark 10 + allowedLateness 5), cận dưới của side output
  dup_cb   : payment_callback gửi lặp (cùng event_id)
  violation: bản sao sai contract theo reason = số message DLQ
Chạy trong pod replayer: kubectl -n data exec -i job/event-replayer -- python - 2026-01-03 < generator/stream_truth.py
(tham số: chỉ tính event_time trước ngày này, vì các phút sau watermark chưa đóng).
"""
import glob
import os
import sys

import pandas as pd

EVENT_DIR = os.environ.get("EVENT_DIR", "/data/events")
cutoff = int(pd.Timestamp(sys.argv[1]).timestamp() * 1000)
files = sorted(glob.glob(f"{EVENT_DIR}/bookings_*/day=*.parquet"))
ev = pd.concat([pd.read_parquet(f, columns=["type", "event_id", "idempotency_key", "event_time", "ingest_time",
                                            "violation"]) for f in files], ignore_index=True)
ev = ev[ev["event_time"].fillna(0) < cutoff]
day = pd.to_datetime(ev["event_time"], unit="ms").dt.date
created = ev[(ev["type"] == "booking_created") & ev["violation"].isna()]
first = ~created.duplicated("idempotency_key")
out = pd.DataFrame({
    "created": first.groupby(day).sum(),
    "dup": (~first).groupby(day).sum(),
    "late_15m": ((created["ingest_time"] - created["event_time"]) > 15 * 60_000)[first].groupby(day).sum(),
    "dup_cb": ev[ev["type"] == "payment_callback"].duplicated("event_id").groupby(day).sum(),
}).fillna(0).astype(int)
print(out.to_string())
print("violation:", ev["violation"].value_counts().to_dict())
