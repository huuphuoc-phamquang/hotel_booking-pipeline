"""Một chuỗi nhân quả quote -> booking -> huỷ; landing là các bảng append-only; stream là đúng các bảng đó lọc theo cửa sổ."""
import sys

import numpy as np
import pandas as pd
import pytest

from generator.offline_gen import (CITIES, apply_schema_version, gen_bookings, gen_dims, gen_quotes,
                                   landing_partitions, load_config)
from generator import stream_gen
from generator.stream_gen import gen_events, gen_quote_events, window_ms

DAY = 86_400_000


@pytest.fixture(scope="module")
def small():
    """Config thật, thu nhỏ dims và số shard để test chạy nhanh."""
    cfg = load_config("generator/config.yaml")
    cfg["dims"] = {"hotels": 300, "customers": 5000}
    cfg["shards_per_day"] = 2
    return cfg, gen_dims(cfg)


def ms(s: pd.Series) -> np.ndarray:
    return s.values.astype("datetime64[ms]").astype("int64")


def test_bookings_are_booked_quotes(small):
    cfg, dims = small
    q = gen_quotes(cfg, dims, 365, 0)
    b = gen_bookings(cfg, dims, 365, 0)
    first = b.drop_duplicates("idempotency_key")
    assert set(first["booking_id"]) == set(q.loc[q["booked"], "quote_id"])          # booking = quote đã chốt
    assert not (q["booked"] & ~q["available"]).any()                               # hết phòng thì không đặt được
    assert (q["hotel_id"] % cfg["shards_per_day"] == 0).all()                      # shard = hotel_id % shards
    m = first.merge(q, left_on="booking_id", right_on="quote_id")
    assert (m["price_x"] == m["price_y"]).all() and (m["checkin"] == m["stay_date"]).all()


def test_covariate_drift_lengthens_lead_time(small):
    """Từ covariate_drift.date lead time dài ra (×lead_scale): KS/PSI trên feature lead_days phải bắt được."""
    cfg, dims = small
    drift = (pd.Timestamp(cfg["covariate_drift"]["date"]) - pd.Timestamp(cfg["start_date"])).days
    lead = lambda days: pd.concat([gen_bookings(cfg, dims, d, s) for d in days for s in range(2)]).pipe(
        lambda b: (b["checkin"] - b["created_at"]).dt.days.clip(lower=0).mean())
    assert lead(range(drift, drift + 5)) > 1.3 * lead(range(drift - 5, drift))


def test_event_raises_quotes_only_after_announce(small):
    cfg, dims = small
    ev = cfg["events"][1]
    start = pd.Timestamp(cfg["start_date"])
    announce = (pd.Timestamp(ev["announce"]) - start).days
    stays = pd.date_range(ev["from"], ev["to"])
    city = np.flatnonzero(dims.city_code == CITIES.index(ev["city"])) + 1

    def views(days):
        q = pd.concat([gen_quotes(cfg, dims, d, s) for d in days for s in range(2)], ignore_index=True)
        return (q["hotel_id"].isin(city) & q["stay_date"].isin(stays)).sum() / len(days)
    assert views(range(announce, announce + 7)) > 2 * views(range(announce - 7, announce))


def test_schema_versions_do_not_touch_label_columns(small):
    cfg, dims = small
    b = gen_bookings(cfg, dims, 10, 0)
    v1 = apply_schema_version(cfg, b, pd.Timestamp("2025-01-11"))
    v2 = apply_schema_version(cfg, b, pd.Timestamp("2025-08-01"))
    assert "channel" not in v1 and "room_type" in v1 and {"channel", "room_category"} <= set(v2)
    assert "cancellation_policy" in v1 and "cancellation_policy" in v2              # nhãn không mất tín hiệu ở v1
    assert set(b["cancellation_policy"]) <= {"flexible", "non_refundable"}


def test_landing_has_no_label_in_bookings(small):
    cfg, dims = small
    parts = {k.split("/")[0]: df for k, df, _ in landing_partitions(cfg, dims, 365, 366) if "shard=00" in k}
    assert set(parts) == {"quotes", "bookings", "cancellations", "payments", "truth"}
    assert not {"status", "cancelled_at", "p_cancel_true"} & set(parts["bookings"].columns)
    assert list(parts["truth"].columns) == ["booking_id", "p_cancel_true"]            # p thật ra bucket riêng
    canc = [(k, df) for k, df, _ in landing_partitions(cfg, dims, 365, 366) if k.startswith("cancellations/")]
    for k, df in canc:                                       # partition dt= là ngày huỷ: không chứa huỷ tương lai
        assert (df["cancelled_at"].dt.strftime("%Y-%m-%d") == k.split("dt=")[1][:10]).all()
    assert len({k for k, _ in canc}) == len(canc)
    c = pd.concat([df for k, df in canc if "shard=00" in k], ignore_index=True)
    assert c["booking_id"].isin(parts["bookings"]["booking_id"]).all() and c["idempotency_key"].is_unique


def test_events_in_window_equal_landing_rows_in_window(small):
    """Bất biến: event trong cửa sổ = dòng landing trong cửa sổ, cho quotes, booking tạo và lần huỷ
    (kể cả huỷ của booking tạo trước cửa sổ)."""
    cfg, dims = small
    first, last = 365, 368
    start, end = window_ms(cfg, first, last)
    days = range(first - cfg["cancel_lookback_days"], last)
    land = {"quotes": [], "bookings": [], "cancellations": []}
    for k, df, _ in landing_partitions(cfg, dims, days.start, days.stop):
        if k.split("/")[0] in land:
            land[k.split("/")[0]].append(df)
    q, b, c = (pd.concat(land[t], ignore_index=True) for t in ("quotes", "bookings", "cancellations"))
    ev = pd.concat([gen_events(cfg, dims, d, s) for d in days for s in range(2)]
                   + [gen_quote_events(cfg, dims, d, s) for d in range(first - 1, last) for s in range(2)],
                   ignore_index=True)
    ev = ev[(ev["event_time"] >= start) & (ev["event_time"] < end)]
    in_win = lambda t: (t >= start) & (t < end)

    assert set(ev.loc[ev["type"] == "quote", "quote_id"]) == set(q.loc[in_win(ms(q["quoted_at"])), "quote_id"])
    assert set(ev.loc[ev["type"] == "booking_created", "booking_id"]) == set(b.loc[in_win(ms(b["created_at"])), "booking_id"])
    cancelled = ev.loc[ev["type"] == "booking_cancelled", "booking_id"]
    assert cancelled.is_unique
    assert set(cancelled) == set(c.loc[in_win(ms(c["cancelled_at"])), "booking_id"])
    assert (c.loc[in_win(ms(c["cancelled_at"])), "booking_id"] // 10**10 < first).any()   # huỷ của booking cũ


def test_cancelled_at_matches_status_and_precedes_checkin(small):
    cfg, dims = small
    b = gen_bookings(cfg, dims, 365, 0)
    assert (b["cancelled_at"].notna() == (b["status"] == "cancelled")).all()
    c = b.dropna(subset=["cancelled_at"])
    assert (c["cancelled_at"] > c["created_at"]).all()
    assert (c["cancelled_at"] <= c["checkin"].clip(lower=c["created_at"] + pd.Timedelta(hours=1, minutes=1))).all()


def test_late_events_reach_past_watermark_and_lateness(small):
    cfg, dims = small
    ev = pd.concat([gen_events(cfg, dims, d, s) for d in range(365, 375) for s in range(2)], ignore_index=True)
    created = ev[ev["type"] == "booking_created"]
    assert ((created["ingest_time"] - created["event_time"]) > 15 * 60_000).any()   # vượt watermark 10' + lateness 5'
    cm = created[created["device"] == "channel_manager"]
    assert len(cm) and ((cm["ingest_time"] - cm["event_time"]) >= 3_600_000).all()


def test_window_bounds_and_determinism(small):
    cfg, dims = small
    start, end = window_ms(cfg, 365, 395)
    assert end - start == 30 * DAY and start == int(pd.Timestamp("2026-01-01").timestamp() * 1000)
    assert gen_events(cfg, dims, 365, 1).equals(gen_events(cfg, dims, 365, 1))     # sinh lại ra đúng y hệt
    assert gen_quotes(cfg, dims, 200, 1).equals(gen_quotes(cfg, dims, 200, 1))


def test_event_log_grouped_by_ingest_day(small, tmp_path, monkeypatch):
    """Mỗi ngày ingest 1 file booking đã sắp; gộp lại đúng bằng mọi event có ingest_time trong cửa sổ."""
    cfg, dims = small
    cfg = {**cfg, "cancel_lookback_days": 20}
    monkeypatch.setattr(stream_gen, "EVENT_DIR", str(tmp_path))
    monkeypatch.setattr(stream_gen, "TOPICS", [stream_gen.TOPIC])
    first, last = 365, 367
    files = stream_gen.write_event_log(cfg, first, last)
    assert sorted(files) == [first, first + 1] and all(len(v) == 1 for v in files.values())
    got = []
    for day, (path,) in files.items():
        df = pd.read_parquet(path)
        lo, hi = window_ms(cfg, day, day + 1)
        assert df["ingest_time"].between(lo, hi - 1).all() and df["ingest_time"].is_monotonic_increasing
        got.append(df)
    start, end = window_ms(cfg, first, last)
    ev = pd.concat([gen_events(cfg, dims, d, s) for d in range(first - 20, last) for s in range(2)], ignore_index=True)
    ev = ev[(ev["ingest_time"] >= start) & (ev["ingest_time"] < end)]
    assert sorted(pd.concat(got)["event_id"]) == sorted(ev["event_id"])


def test_contract_flags_exactly_the_injected_events(small):
    """Novelty edai-1: DLQ theo contract = đúng các bản sao lỗi generator cài, đúng loại; event thật không bị chặn."""
    pytest.importorskip("jsonschema")
    sys.path.insert(0, "flink_jobs")
    from contract import violation
    cfg, dims = small
    ev = pd.concat([gen_events(cfg, dims, d, s) for d in range(365, 380) for s in range(2)], ignore_index=True)
    bad = ev[ev["violation"].notna()]
    assert len(bad) > 0 and set(bad["violation"]) == set(stream_gen.VIOLATIONS)
    assert not set(bad["event_id"]) & set(ev.loc[ev["violation"].isna(), "event_id"])   # không đè event_id thật
    for r in ev.to_dict("records"):
        drop = {"ingest_time", "violation"} | ({"event_time"} if r["violation"] == "event_time" else set())
        payload = {k: v.item() if hasattr(v, "item") else v for k, v in r.items()
                   if k not in drop and not (isinstance(v, float) and np.isnan(v))}
        assert violation(payload) == (None if pd.isna(r["violation"]) else r["violation"]), r


def test_contract_rejects_future_event_time():
    """event_time ở tương lai xa (vd ghi nhầm µs thay vì ms) ra DLQ, không kịp đẩy watermark của Flink."""
    pytest.importorskip("jsonschema")
    sys.path.insert(0, "flink_jobs")
    from contract import violation
    ev = {"event_id": 1, "type": "booking_created", "event_time": 1_751_328_000_000, "booking_id": 1,
          "idempotency_key": 1, "hotel_id": 1, "price": 100.0}
    assert violation(ev) is None
    assert violation({**ev, "event_time": ev["event_time"] * 1000}) == "event_time"
