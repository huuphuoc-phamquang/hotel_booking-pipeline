"""Sinh dữ liệu offline cho booking app (đặt phòng khách sạn) và đẩy lên MinIO (nguồn cho Bronze).

Một chuỗi nhân quả: quote (lượt xem giá) -> booking (quote có booked = 1) -> huỷ -> event (stream_gen).
  - quotes   : mỗi ngày, mỗi shard (= hotel_id % shards) rút lượt xem giá theo độ phổ biến khách sạn (Zipf),
               lead time (dài ra từ covariate_drift.date), hệ số mùa + sự kiện theo STAY_DATE; giá P̄ · mùa^a · u^b;
               booked ~ P(book | giá) của demand.py; hết phòng cắt cầu (censored). Quotes là log lượt xem
               (100GB, bài skew); không có model nào ước lượng cầu từ bảng này.
  - bookings : các quote có booked = 1 (booking_id = quote_id), gắn khách theo mức hay đi (đuôi dài).
  - cancellations : nhãn huỷ logistic đã biết + thời điểm huỷ; bảng append-only, dt= theo ngày huỷ, shard= của booking gốc.
Rubric edai-1 › Implement Data Generator › Simulate offline data problems:
  - Simulate skew              : Zipf theo khách sạn + 70% khách sạn ở 3 thành phố + mùa cao điểm theo stay_date
  - Simulate schema evolution  : từ schema_v2_date bookings thêm cột channel, đổi room_type -> room_category
                                 (không đụng cột nào trong công thức nhãn: lỗi dữ liệu tách khỏi nhãn)
  - Another offline problem    : 2% booking bị gửi 2 lần (double submit), cùng idempotency_key
  - Store data after generating: ghi Parquet lên MinIO bucket "landing", partition dt=/shard=
Tái lập: mọi số ngẫu nhiên lấy từ SeedSequence(seed, day, shard, table) hoặc hash tất định; không đọc giờ thật.
Số đo của dữ liệu sinh ra: generator/profile_data.py.
"""
import hashlib
import io
import json
import os
import sys
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pyarrow
import yaml
from minio import Minio
from minio.error import S3Error

from generator.demand import SEGMENT_OF_STARS, book_prob, season_of

BUCKET = "landing"
TRUTH_BUCKET = "truth"                    # ground truth (xác suất huỷ thật): ngoài landing, pipeline không đọc
TABLE_IDS = {"dims": 0, "bookings": 1, "payments": 2, "events": 3, "quotes": 4}
CITIES = ["Ho Chi Minh", "Ha Noi", "Da Nang", "Nha Trang", "Da Lat", "Phu Quoc", "Hue", "Hoi An"]
ROOM_TYPES = np.array(["standard", "deluxe", "suite"])
RATE_PLANS = np.array(["flexible", "non_refundable"])
HORIZON_DAYS = 240                   # lead time dài nhất có thể sinh (gamma(2, 10) gần như không vượt 200 ngày)


def load_config(path: str) -> dict:
    """Đọc config.yaml và giữ sha256 của nội dung để ghi vào manifest."""
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    cfg = yaml.safe_load(raw)
    cfg["sha256"] = hashlib.sha256(raw.encode()).hexdigest()
    return cfg


def partition_rng(cfg: dict, day_idx: int, shard: int, table: str) -> np.random.Generator:
    """Luồng số ngẫu nhiên riêng cho (ngày, shard, bảng): sinh lại 1 partition không cần chạy các partition khác."""
    return np.random.default_rng(np.random.SeedSequence([cfg["seed"], day_idx, shard, TABLE_IDS[table]]))


def make_ids(day_idx: int, shard: int, n: int) -> np.ndarray:
    """ID tất định, không trùng giữa partition: day*10^10 + shard*10^7 + i (shard < 100, n < 10^7)."""
    assert n < 10**7, n
    return day_idx * 10**10 + shard * 10**7 + np.arange(n, dtype=np.int64)


def hash_normal(seed: int, a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """N(0, 1) tất định theo cặp (a, b) (splitmix64 + Box–Muller): cùng ô luôn cùng giá trị, ở partition nào cũng vậy."""
    def mix(x):
        x = (x + np.uint64(0x9E3779B97F4A7C15)) & np.uint64(0xFFFFFFFFFFFFFFFF)
        x = (x ^ (x >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)
        x = (x ^ (x >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)
        return x ^ (x >> np.uint64(31))
    with np.errstate(over="ignore"):
        x = mix(np.uint64(seed) ^ mix(a.astype(np.uint64)) ^ mix(b.astype(np.uint64) << np.uint64(20)))
        y = mix(x)
    u1 = ((x >> np.uint64(11)).astype(np.float64) + 0.5) / 2.0**53
    u2 = ((y >> np.uint64(11)).astype(np.float64) + 0.5) / 2.0**53
    return np.sqrt(-2 * np.log(u1)) * np.cos(2 * np.pi * u2)


def gen_dims(cfg: dict) -> SimpleNamespace:
    """Sinh hotels, lịch sử giá (nguồn SCD2), customers và các tham số ẩn của hàm cầu một lần; giữ trong bộ nhớ."""
    rng = partition_rng(cfg, 0, 0, "dims")
    d = cfg["demand"]
    n_h, n_c = cfg["dims"]["hotels"], cfg["dims"]["customers"]
    hot = cfg["skew"]["hot_city_share"]
    city_p = np.r_[np.full(3, hot / 3), np.full(len(CITIES) - 3, (1 - hot) / (len(CITIES) - 3))]
    hotels = pd.DataFrame({
        "hotel_id": np.arange(1, n_h + 1),
        "city": rng.choice(CITIES, n_h, p=city_p),
        "stars": rng.integers(1, 6, n_h),
        "base_price": rng.lognormal(13.5, 0.5, n_h).round(-3),   # P̄ của phòng standard
    })
    rank = rng.permutation(n_h) + 1                              # hạng phổ biến, xáo để không trùng hotel_id
    pop = 1.0 / rank ** cfg["skew"]["hotel_zipf_a"]
    pop /= pop.mean()                                            # độ phổ biến, trung bình 1

    start = pd.Timestamp(cfg["start_date"])
    n_chg = rng.poisson(4, n_h)                                  # trung bình 4 lần đổi giá / năm
    changes = pd.DataFrame({
        "hotel_id": np.repeat(hotels["hotel_id"].values, n_chg),
        "valid_from": start + pd.to_timedelta(rng.integers(1, cfg["offline_days"], n_chg.sum()), unit="D"),
        "price_factor": rng.uniform(0.85, 1.25, n_chg.sum()).round(2),
    })
    first = pd.DataFrame({"hotel_id": hotels["hotel_id"], "valid_from": start, "price_factor": 1.0})
    hotel_changes = (pd.concat([first, changes], ignore_index=True)
                     .sort_values(["hotel_id", "valid_from"], kind="stable")
                     .drop_duplicates(["hotel_id", "valid_from"], keep="last"))
    hotel_changes["price"] = (hotel_changes["hotel_id"].map(hotels.set_index("hotel_id")["base_price"])
                              * hotel_changes["price_factor"]).round(-3)

    customers = pd.DataFrame({                                   # city dạng category, tier int8 cho nhẹ bộ nhớ
        "customer_id": np.arange(1, n_c + 1),
        "home_city": pd.Categorical.from_codes(rng.integers(0, len(CITIES), n_c), CITIES),
        "loyalty_tier": rng.choice(np.array([0, 1, 2, 3], dtype=np.int8), n_c, p=[0.6, 0.25, 0.1, 0.05]),
    })
    propensity = rng.normal(0, 1, n_c)                           # cột ẩn: xu hướng huỷ, KHÔNG ghi ra landing
    activity = rng.lognormal(0, cfg["customer_activity_sigma"], n_c)   # cột ẩn: mức hay đi của khách (đuôi dài)

    # sức chứa theo hotel: ngày thường lấp target_occupancy ở giá tối ưu không ràng buộc (cầu theo demand.book_prob)
    seg = SEGMENT_OF_STARS[hotels["stars"].values]
    beta = np.array(d["beta"])[seg]                              # (hotel, nhóm lead time)
    lo, hi, _ = d["grid"]
    p_free = np.clip(beta / (beta - 1) * d["cost_frac"], lo, hi)
    normal = (d["quotes_per_cell"] * np.array(d["lead_share"]) * d["conversion"] * p_free ** -beta).sum(1)
    cap = np.maximum(1.0, np.round(pop * normal / d["target_occupancy"]))

    shards = cfg["shards_per_day"]
    by_shard = []
    for s in range(shards):                                      # mỗi shard giữ trọn khách sạn của nó
        idx = np.flatnonzero(hotels["hotel_id"].values % shards == s)
        by_shard.append((idx, np.cumsum(pop[idx]) / pop[idx].sum(), pop[idx].sum()))

    n_days = cfg["offline_days"] + 60 + HORIZON_DAYS             # đủ cho stay_date của batch + stream
    days = pd.date_range(start, periods=n_days)
    city_code = pd.Categorical(hotels["city"], categories=CITIES).codes
    return SimpleNamespace(hotels=hotels, pop=pop, seg=seg, beta=beta, cap=cap, by_shard=by_shard,
                           city_code=city_code, hotel_changes=hotel_changes, customers=customers,
                           propensity=propensity, customer_cdf=np.cumsum(activity) / activity.sum(),
                           season=season_of(cfg, days), events=cfg.get("events", []))


def demand_factor(cfg: dict, dims: SimpleNamespace, hotel_idx: np.ndarray, stay_idx: np.ndarray,
                  quote_idx: int) -> np.ndarray:
    """Hệ số lượt xem của ô: mùa theo stay_date × sự kiện (chỉ từ announce_date: trước khi công bố cầu như thường)."""
    f = dims.season[stay_idx].copy()
    start = pd.Timestamp(cfg["start_date"])
    for ev in dims.events:
        lo, hi = ((pd.Timestamp(ev[k]) - start).days for k in ("from", "to"))
        if quote_idx >= (pd.Timestamp(ev["announce"]) - start).days:
            hit = (dims.city_code[hotel_idx] == CITIES.index(ev["city"])) & (stay_idx >= lo) & (stay_idx <= hi)
            f[hit] *= ev["factor"]
    return f


def max_factor(dims: SimpleNamespace) -> float:
    """Chặn trên của demand_factor, dùng cho phép rút loại (thinning)."""
    return float(dims.season.max() * max([ev["factor"] for ev in dims.events] + [1.0]))


def price_as_of(changes: pd.DataFrame, hotel_id: np.ndarray, at: pd.Series) -> np.ndarray:
    """P̄ hiệu lực tại thời điểm at (đúng phiên bản SCD2) bằng merge_asof; trả về theo thứ tự đầu vào."""
    left = pd.DataFrame({"i": np.arange(len(at)), "hotel_id": hotel_id, "at": at.values}).sort_values("at")
    right = changes[["hotel_id", "valid_from", "price"]].sort_values("valid_from")
    m = pd.merge_asof(left, right, left_on="at", right_on="valid_from", by="hotel_id")
    return m.sort_values("i")["price"].values


def gen_inventory(cfg: dict, dims: SimpleNamespace, stay_idx: int) -> pd.DataFrame:
    """Số phòng mở bán của mỗi (hotel, room_type) cho đêm stay_idx: sức chứa dims.cap chia theo room_share.
    Bảng dim lớn (~50k × 3 × 665 đêm ≈ 100 triệu dòng, không broadcast được) cho bài skew quotes ⋈ inventory."""
    share = np.array(cfg["demand"]["room_share"])
    rooms = np.maximum(1, np.round(dims.cap[:, None] * share)).astype(np.int32)      # (hotel, room_type)
    return pd.DataFrame({
        "hotel_id": np.repeat(dims.hotels["hotel_id"].values, len(ROOM_TYPES)),
        "room_type": np.tile(ROOM_TYPES, len(dims.hotels)),
        "stay_date": pd.Timestamp(cfg["start_date"]) + pd.Timedelta(days=stay_idx),
        "rooms": rooms.ravel(),
    })


def gen_quotes(cfg: dict, dims: SimpleNamespace, day_idx: int, shard: int) -> pd.DataFrame:
    """Lượt xem giá của 1 partition (ngày xem day_idx, shard = hotel_id % shards).
    Số lượt ~ quotes_per_cell · độ phổ biến · hệ số mùa/sự kiện của stay_date (rút loại theo demand_factor)."""
    d = cfg["demand"]
    rng = partition_rng(cfg, day_idx, shard, "quotes")
    idx, cdf, pop_sum = dims.by_shard[shard]
    fmax = max_factor(dims)
    n = rng.poisson(d["quotes_per_cell"] * pop_sum * fmax)
    h = idx[np.searchsorted(cdf, rng.random(n), side="right").clip(max=len(idx) - 1)]
    cd = cfg["covariate_drift"]                                  # drift trên feature (lead time) để KS/PSI bắt được
    scale = cd["lead_scale"] if day_idx >= (pd.Timestamp(cd["date"]) - pd.Timestamp(cfg["start_date"])).days else 1.0
    lead = rng.gamma(2.0, 10.0 * scale, n).astype(int).clip(max=HORIZON_DAYS - 1)
    stay = day_idx + lead
    keep = rng.random(n) * fmax < demand_factor(cfg, dims, h, stay, day_idx)
    h, lead, stay = h[keep], lead[keep], stay[keep]
    n = len(h)

    day = pd.Timestamp(cfg["start_date"]) + pd.Timedelta(days=day_idx)
    quoted_at = day + pd.to_timedelta(rng.integers(0, 86_400, n), unit="s")
    room = rng.choice(len(ROOM_TYPES), n, p=d["room_share"])
    plan = rng.choice(len(RATE_PLANS), n, p=d["rate_plan_share"])
    hotel_id = dims.hotels["hotel_id"].values[h]
    u = np.exp(d["latent_sigma"] * hash_normal(cfg["seed"], hotel_id, stay) - d["latent_sigma"] ** 2 / 2)
    season = dims.season[stay]
    rel = season ** d["policy"]["season_pass"] * u ** d["policy"]["latent_pass"]   # giá / P̄
    unit = (price_as_of(dims.hotel_changes, hotel_id, pd.Series(quoted_at))
            * np.array(d["room_mult"])[room] * np.array(d["rate_plan_mult"])[plan])
    early = (lead >= d["early_lead_days"]).astype(int)
    beta = dims.beta[h, 1 - early]                                               # cột 0 = đặt sớm, 1 = đặt muộn

    # shortcut: hết phòng tính theo xác suất từ cầu kỳ vọng của ô (không giữ tồn phòng qua các ngày) để vẫn sinh
    # lại được từng partition; cần tồn phòng chính xác thì phải sinh tuần tự theo ngày.
    exp_demand = (d["quotes_per_cell"] * dims.pop[h] * demand_factor(cfg, dims, h, stay, day_idx)
                  * d["conversion"] * u ** (1 + d["kappa"])
                  * (np.array(d["lead_share"]) * rel[:, None] ** -dims.beta[h]).sum(1))
    available = rng.random(n) < np.minimum(1.0, dims.cap[h] / np.maximum(exp_demand, 1e-9))
    booked = available & (rng.random(n) < book_prob(cfg, rel, u, beta))
    start = pd.Timestamp(cfg["start_date"])
    return pd.DataFrame({
        "quote_id": make_ids(day_idx, shard, n),
        "quoted_at": quoted_at,
        "hotel_id": hotel_id,
        "room_type": ROOM_TYPES[room],
        "stay_date": start + pd.to_timedelta(stay, unit="D"),
        "nights": rng.integers(1, 6, n),
        "rate_plan": RATE_PLANS[plan],
        "price": (unit * rel).round(-3),
        "available": available,
        "booked": booked,
    })


def draw_status(cfg: dict, rng: np.random.Generator, df: pd.DataFrame, dims: SimpleNamespace,
                day: pd.Timestamp) -> tuple[np.ndarray, np.ndarray]:
    """Nhãn huỷ sinh từ công thức logistic đã biết; trả (status, p thật) để chấm calibration / Brier / sai số K."""
    lab = cfg["label"]
    coef = dict(lab["coef"])
    if day >= pd.Timestamp(lab["drift"]["date"]):
        coef.update(lab["drift"]["coef"])                        # concept drift có chủ đích để demo retrain
    cust = df["customer_id"].values - 1
    lead = (df["checkin"] - df["created_at"]).dt.days.clip(lower=0)
    x = (lab["intercept"]
         + coef["lead_time"] * np.log1p(lead) / 3
         + coef["free_cancel"] * (df["cancellation_policy"] == "flexible").astype(int)
         + coef["propensity"] * dims.propensity[cust]
         + coef["loyalty"] * dims.customers["loyalty_tier"].values[cust])
    p = 1 / (1 + np.exp(-x))
    return np.where(rng.random(len(df)) < p, "cancelled", "confirmed"), p


def draw_cancelled_at(rng: np.random.Generator, df: pd.DataFrame) -> pd.Series:
    """Thời điểm huỷ của booking bị huỷ: rải đều từ lúc đặt tới ngày nhận phòng (ít nhất 1 giờ sau khi đặt)."""
    span = (df["checkin"] - df["created_at"]).clip(lower=pd.Timedelta(hours=1))
    at = df["created_at"] + pd.Timedelta(minutes=1) + span * rng.random(len(df))
    return at.dt.floor("s").where(df["status"] == "cancelled")


def inject_double_submit(cfg: dict, rng: np.random.Generator, df: pd.DataFrame) -> pd.DataFrame:
    """Nhân đôi DUP% dòng: booking_id mới nhưng cùng idempotency_key, created_at lệch 1-3 giây."""
    mask = rng.random(len(df)) < cfg["anomalies"]["double_submit_rate"]
    dup = df[mask].copy()
    dup["created_at"] += pd.to_timedelta(rng.integers(1, 4, len(dup)), unit="s")
    dup["booking_id"] += 5 * 10**9                               # vẫn nằm trong dải ID của cùng ngày
    return pd.concat([df, dup], ignore_index=True)


def apply_schema_version(cfg: dict, df: pd.DataFrame, day: pd.Timestamp) -> pd.DataFrame:
    """Schema v1 chưa có cột channel; v2 thêm channel và đổi tên room_type -> room_category."""
    if day < pd.Timestamp(cfg["anomalies"]["schema_v2_date"]):
        return df.drop(columns=["channel"])
    return df.rename(columns={"room_type": "room_category"})


def gen_bookings(cfg: dict, dims: SimpleNamespace, day_idx: int, shard: int,
                 quotes: pd.DataFrame | None = None) -> pd.DataFrame:
    """Booking của 1 partition = các quote có booked = 1, kèm kết cục thật (status, cancelled_at) và channel.
    Bảng gốc (schema mới nhất); landing áp phiên bản schema, stream đọc thẳng bảng này.
    quotes: quotes đã sinh của đúng partition này (tránh sinh lại); None thì tự sinh."""
    q = gen_quotes(cfg, dims, day_idx, shard) if quotes is None else quotes
    q = q[q["booked"]].reset_index(drop=True)
    rng = partition_rng(cfg, day_idx, shard, "bookings")
    n = len(q)
    s = cfg["stream"]
    cm = s["late"]["channel_manager"]["share"]
    df = pd.DataFrame({
        "booking_id": q["quote_id"].values,                      # booking chính là quote đã chốt
        # rút khách theo mức hay đi (searchsorted trên CDF, nhanh hơn rng.choice(p=...) với hàng chục triệu khách)
        "customer_id": np.searchsorted(dims.customer_cdf, rng.random(n), side="right") + 1,
        "hotel_id": q["hotel_id"].values,
        "room_type": q["room_type"].values,
        "created_at": q["quoted_at"] + pd.to_timedelta(rng.integers(30, 600, n), unit="s"),
        "checkin": q["stay_date"].values,
        "nights": q["nights"].values,
        "cancellation_policy": q["rate_plan"].values,
        "price": q["price"].values,
        "channel": rng.choice(["mobile", "web", "channel_manager"], n,
                              p=[s["mobile_share"], 1 - s["mobile_share"] - cm, cm]),
    })
    df["idempotency_key"] = df["booking_id"]
    day = pd.Timestamp(cfg["start_date"]) + pd.Timedelta(days=day_idx)
    df["status"], df["p_cancel_true"] = draw_status(cfg, rng, df, dims, day)
    df["cancelled_at"] = draw_cancelled_at(rng, df)
    return inject_double_submit(cfg, rng, df)


def gen_payments(cfg: dict, bookings: pd.DataFrame, day_idx: int, shard: int) -> pd.DataFrame:
    """1 payment cho mỗi idempotency_key (bản gửi trùng không bị trừ tiền 2 lần)."""
    rng = partition_rng(cfg, day_idx, shard, "payments")
    b = bookings.drop_duplicates("idempotency_key")
    n = len(b)
    return pd.DataFrame({
        "payment_id": b["booking_id"].values,
        "booking_id": b["booking_id"].values,
        "amount": (b["price"] * b["nights"]).values,
        "provider": rng.choice(["vnpay", "momo", "card"], n, p=[0.5, 0.3, 0.2]),
        "status": rng.choice(["success", "failed"], n, p=[0.95, 0.05]),
    })


def cancellations(bookings: pd.DataFrame) -> pd.DataFrame:
    """Các lần huỷ của một partition booking, 1 lần / idempotency_key (bản double submit không huỷ lần 2)."""
    c = bookings.drop_duplicates("idempotency_key").dropna(subset=["cancelled_at"])
    return c[["booking_id", "idempotency_key", "cancelled_at"]].reset_index(drop=True)


def landing_partitions(cfg: dict, dims: SimpleNamespace, first_day: int, last_day: int):
    """Sinh (key, DataFrame, sort_by) cho landing: các bảng append-only như hệ thống nguồn, partition dt=/shard=:
    quotes (log lượt xem giá), bookings (sự kiện lúc đặt, không có status), payments theo ngày phát sinh;
    cancellations (booking_id, cancelled_at) theo NGÀY HUỶ, nên partition dt=d chỉ chứa lần huỷ đã xảy ra trong
    ngày d (DP1 copy dt=ds không thấy trước lần huỷ tương lai). Nhãn = left join + checkin < ngày chạy.
    Một lần chạy [first_day, last_day) ghi file part-<first_day> trong mỗi partition huỷ, nên các lần chạy song song
    theo khoảng ngày không ghi đè nhau và chạy lại cùng khoảng thì ghi đè đúng file của nó.
    shortcut: đổi ranh giới khoảng ngày giữa các lần chạy để lại file part- cũ, khi đó xoá prefix cancellations/ rồi sinh lại."""
    pending = {}                                                 # (ngày huỷ, shard) -> các lần huỷ chờ ghi

    def flush(before: pd.Timestamp):
        """Ghi các partition huỷ có ngày < before: booking từ ngày before trở đi không huỷ lùi về trước nữa."""
        for cday, shard in sorted(k for k in pending if k[0] < before):
            yield (f"cancellations/dt={cday:%Y-%m-%d}/shard={shard:02d}/part-{first_day}.parquet",
                   pd.concat(pending.pop((cday, shard)), ignore_index=True), "booking_id")

    for day_idx in range(first_day, last_day):
        day = pd.Timestamp(cfg["start_date"]) + pd.Timedelta(days=day_idx)
        yield from flush(day)
        for shard in range(cfg["shards_per_day"]):
            part = f"dt={day:%Y-%m-%d}/shard={shard:02d}/part-0.parquet"
            quotes = gen_quotes(cfg, dims, day_idx, shard)
            yield f"quotes/{part}", quotes, "quote_id"
            truth = gen_bookings(cfg, dims, day_idx, shard, quotes)
            bookings = apply_schema_version(cfg, truth.drop(columns=["status", "cancelled_at", "p_cancel_true"]), day)
            yield f"bookings/{part}", bookings, "booking_id"
            yield f"truth/p_cancel/{part}", truth[["booking_id", "p_cancel_true"]], "booking_id"
            c = cancellations(truth)
            for cday, g in c.groupby(c["cancelled_at"].dt.normalize()):
                pending.setdefault((cday, shard), []).append(g)
            yield f"payments/{part}", gen_payments(cfg, bookings, day_idx, shard), "payment_id"
    yield from flush(pd.Timestamp.max)


def upload_parquet(client: Minio, df: pd.DataFrame, key: str, sort_by) -> dict:
    """Sắp thứ tự cố định rồi ghi đè 1 file Parquet; trả về dòng manifest (rows, sha256).
    Key bắt đầu bằng truth/ đi vào bucket truth (không phải landing) để DP1 và model không thấy."""
    df = df.sort_values(sort_by, kind="stable")
    buf = io.BytesIO()
    # micro giây: Spark 3.5 không đọc được TIMESTAMP(NANOS) mặc định của pandas
    df.to_parquet(buf, index=False, compression="zstd", coerce_timestamps="us", allow_truncated_timestamps=True)
    data = buf.getvalue()
    bucket, key = (TRUTH_BUCKET, key[len("truth/"):]) if key.startswith("truth/") else (BUCKET, key)
    client.put_object(bucket, key, io.BytesIO(data), length=len(data))
    return {"bucket": bucket, "key": key, "rows": len(df), "sha256": hashlib.sha256(data).hexdigest()}


def main(config_path: str = "generator/config.yaml", first_day: int = 0, last_day: int | None = None) -> None:
    """Sinh dims rồi các partition [first_day, last_day); chạy lại cùng tham số ghi đè đúng các file đó."""
    cfg = load_config(config_path)
    last_day = cfg["offline_days"] if last_day is None else last_day
    client = Minio(os.environ["MINIO_ENDPOINT"], access_key=os.environ["MINIO_ACCESS_KEY"],
                   secret_key=os.environ["MINIO_SECRET_KEY"], secure=False)
    for b in (BUCKET, TRUTH_BUCKET):
        if not client.bucket_exists(b):
            try:
                client.make_bucket(b)
            except S3Error as e:                             # pod song song của Indexed Job vừa tạo trước
                if e.code != "BucketAlreadyOwnedByYou":
                    raise

    dims = gen_dims(cfg)
    manifest = {"config_sha256": cfg["sha256"], "numpy": np.__version__, "pandas": pd.__version__,
                "pyarrow": pyarrow.__version__, "partitions": []}
    # bảng dim tĩnh, tất định: chỉ lần chạy chứa ngày 0 ghi (8 pod của Indexed Job không cùng ghi đè 30 triệu khách),
    # các lần khác vẫn sinh dims trong bộ nhớ để dựng booking
    if first_day == 0:
        manifest["partitions"] += [
            upload_parquet(client, dims.hotels, "hotels/part-0.parquet", "hotel_id"),
            upload_parquet(client, dims.hotel_changes, "hotel_changes/part-0.parquet", ["hotel_id", "valid_from"]),
            upload_parquet(client, dims.customers, "customers/part-0.parquet", "customer_id"),
        ]
        for s in range(len(dims.season)):
            inv = gen_inventory(cfg, dims, s)
            manifest["partitions"].append(upload_parquet(
                client, inv, f"inventory/stay_date={inv['stay_date'].iloc[0]:%Y-%m-%d}/part-0.parquet",
                ["hotel_id", "room_type"]))
    for key, df, sort_by in landing_partitions(cfg, dims, first_day, last_day):
        manifest["partitions"].append(upload_parquet(client, df, key, sort_by))
    data = json.dumps(manifest, indent=2).encode()      # chỉ ghi lên MinIO: container chạy appuser, /app không ghi được
    # ghi cuối cùng = đánh dấu khoảng ngày đã xong; DP1 check_landing đợi các manifest phủ liền tới ngày chạy
    client.put_object(BUCKET, f"_manifests/manifest_{first_day}_{last_day}.json", io.BytesIO(data), length=len(data))


if __name__ == "__main__":
    main(first_day=int(sys.argv[1]) if len(sys.argv) > 1 else 0,
         last_day=int(sys.argv[2]) if len(sys.argv) > 2 else None)
