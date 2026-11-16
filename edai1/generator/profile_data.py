"""Đo đặc tính dữ liệu generator sinh ra và in bảng markdown (dán vào docs/edai-1/data_generator.md › Kết quả).
Không ghi số đo vào comment/config: đổi config thì chạy lại script này.

Chạy từ thư mục edai1:  python -m generator.profile_data [ngày mẫu, mặc định 12 ngày cách nhau 30 ngày]
Mẫu = đủ 16 shard của các ngày đó; số cả năm ngoại suy theo 365 ngày (rải đều cả năm để mùa vụ không làm lệch).
"""
import io
import sys

import numpy as np
import pandas as pd

from generator.offline_gen import (apply_schema_version, cancellations, gen_bookings, gen_dims, gen_quotes,
                                   load_config)
from generator.stream_gen import gen_events


def auc(score: np.ndarray, y: np.ndarray) -> float:
    """AUC = P(điểm của mẫu dương > mẫu âm), tính bằng hạng (Mann–Whitney)."""
    r = pd.Series(score).rank().values
    n1 = y.sum()
    return (r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * (len(y) - n1))


def parquet_bytes(df: pd.DataFrame) -> int:
    buf = io.BytesIO()
    df.to_parquet(buf, index=False, compression="zstd", coerce_timestamps="us", allow_truncated_timestamps=True)
    return len(buf.getvalue())


def main(days: list[int]) -> None:
    cfg = load_config("generator/config.yaml")
    dims = gen_dims(cfg)
    shards, start = cfg["shards_per_day"], pd.Timestamp(cfg["start_date"])
    b_all, size = [], {"quotes": [0, 0], "bookings": [0, 0], "cancellations": [0, 0]}
    q_hotel = pd.Series(0, index=dims.hotels["hotel_id"])        # gom theo shard: giữ mọi quote của 12 ngày thì hết RAM
    q_booked = q_avail = 0
    for d in days:
        for s in range(shards):
            q = gen_quotes(cfg, dims, d, s)
            b = gen_bookings(cfg, dims, d, s, q).assign(day=d)
            land = apply_schema_version(cfg, b.drop(columns=["status", "cancelled_at", "p_cancel_true", "day"]), start + pd.Timedelta(days=d))
            for t, df in (("quotes", q), ("bookings", land), ("cancellations", cancellations(b))):
                size[t][0] += len(df)
                size[t][1] += parquet_bytes(df)
            q_hotel = q_hotel.add(q.groupby("hotel_id").size(), fill_value=0)
            q_booked, q_avail = q_booked + q["booked"].sum(), q_avail + q["available"].sum()
            b_all.append(b)
    b = pd.concat(b_all, ignore_index=True)
    per_year = 365 / len(days)

    print(f"Mẫu: ngày {days}, đủ {shards} shard; số cả năm = mẫu × {per_year:.0f}. config_sha256 {cfg['sha256'][:12]}\n")
    print("| Bảng | Dòng / ngày | Byte / dòng (Parquet zstd) | Dòng / năm | Dung lượng / năm |\n|---|---|---|---|---|")
    total = 0
    for t, (rows, nbytes) in size.items():
        total += nbytes * per_year
        print(f"| {t} | {rows / len(days):,.0f} | {nbytes / rows:.1f} | {rows * per_year / 1e9:.2f} tỉ | {nbytes * per_year / 1e9:.1f} GB |")
    print(f"| **tổng** | | | | **{total / 1e9:.1f} GB** |\n")

    first = b.drop_duplicates("idempotency_key")
    print("| Phễu và lỗi dữ liệu | Giá trị |\n|---|---|")
    print(f"| Đặt / lượt xem (look-to-book) | {q_booked / size['quotes'][0]:.2%} |")
    print(f"| Lượt xem gặp hết phòng | {1 - q_avail / size['quotes'][0]:.2%} |")
    print(f"| Double submit (dòng thừa / booking) | {len(b) / len(first) - 1:.2%} |")
    drift = (pd.Timestamp(cfg["label"]["drift"]["date"]) - start).days
    for name, g in (("trước drift", first[first["day"] < drift]), ("sau drift", first[first["day"] >= drift])):
        if len(g):
            print(f"| Tỉ lệ huỷ {name} | {(g['status'] == 'cancelled').mean():.1%} |")
            print(f"| Lead time trung bình {name} (covariate drift) | "
                  f"{(g['checkin'] - g['created_at']).dt.days.clip(lower=0).mean():.1f} ngày |")
    v2 = (pd.Timestamp(cfg["anomalies"]["schema_v2_date"]) - start).days
    print(f"| Booking schema v1 / v2 trong mẫu | {(b['day'] < v2).sum():,} / {(b['day'] >= v2).sum():,} |\n")

    print("| Skew theo khách sạn (mỗi ngày, trung bình mẫu) | Lượt xem | Booking |\n|---|---|---|")
    n_h = len(dims.hotels)
    share = {}
    for name, c in (("q", q_hotel), ("b", first.groupby("hotel_id").size().reindex(dims.hotels["hotel_id"], fill_value=0))):
        c = c.sort_values(ascending=False)
        share[name] = (c.iloc[0] / c.sum(), c.iloc[:10].sum() / c.sum(), c.iloc[: n_h // 100].sum() / c.sum(),
                       c.median() / len(days))
    for i, label in enumerate(["Top 1 khách sạn", "Top 10 khách sạn", "Top 1% khách sạn"]):
        print(f"| {label} | {share['q'][i]:.1%} | {share['b'][i]:.1%} |")
    print(f"| Khách sạn trung vị (dòng / ngày) | {share['q'][3]:,.0f} | {share['b'][3]:,.1f} |\n")

    # số booking mỗi khách trong năm: Poisson theo mức hay đi, tổng = số booking/năm ước lượng
    rng = np.random.default_rng(0)
    lam = np.diff(np.r_[0, dims.customer_cdf]) * len(first) * per_year
    k = rng.poisson(lam)
    print("| Khách (1 năm) | Giá trị |\n|---|---|")
    print(f"| Booking / khách (trung bình) | {k.mean():.1f} |")
    print(f"| Khách không đặt trong năm | {(k == 0).mean():.0%} |")
    print(f"| Khách có đặt: trung vị / p99 | {np.median(k[k > 0]):.0f} / {np.percentile(k[k > 0], 99):.0f} |\n")

    # trần AUC: điểm = đúng công thức nhãn, bỏ dần thành phần model không thấy
    lab, coef = cfg["label"], dict(cfg["label"]["coef"])
    cust = first["customer_id"].values - 1
    lead = np.log1p((first["checkin"] - first["created_at"]).dt.days.clip(lower=0).values) / 3
    flex = (first["cancellation_policy"] == "flexible").values.astype(int)
    loy = dims.customers["loyalty_tier"].values[cust]
    y = (first["status"] == "cancelled").values.astype(int)
    after = (first["day"] >= drift).values
    print("| Trần AUC (điểm = công thức nhãn thật) | Trước drift | Sau drift |\n|---|---|---|")
    for name, use_prop, use_loy in (("oracle (biết propensity ẩn)", 1, 1),
                                    ("lead + policy + loyalty (input của cancel-risk, chưa tính lịch sử khách)", 0, 1),
                                    ("lead + policy (bỏ loyalty)", 0, 0)):
        cells = []
        for mask in (~after, after):
            c = dict(coef)
            if mask is after:
                c.update(lab["drift"]["coef"])
            score = (c["lead_time"] * lead + c["free_cancel"] * flex
                     + use_prop * c["propensity"] * dims.propensity[cust] + use_loy * c["loyalty"] * loy)
            cells.append(f"{auc(score[mask], y[mask]):.3f}" if mask.any() and y[mask].any() else "—")
        print(f"| {name} | {cells[0]} | {cells[1]} |")
    print()

    ev = gen_events(cfg, dims, days[-1], 0)
    cr = ev[ev["type"] == "booking_created"]
    delay = (cr["ingest_time"] - cr["event_time"]) / 60_000
    print("| Event trễ (booking_created, 1 shard) | Tỉ lệ |\n|---|---|")
    print(f"| Trễ 10–15 phút (vào lại qua allowed lateness) | {((delay > 10) & (delay <= 15)).mean():.2%} |")
    print(f"| Trễ > 15 phút (side output nhánh tumbling 1 phút) | {(delay > 15).mean():.2%} |")
    print(f"| Trễ > 75 phút (side output nhánh trượt 1 giờ) | {(delay > 75).mean():.2%} |")
    print(f"| Qua channel manager (trễ 1–4 giờ) | {(cr['device'] == 'channel_manager').mean():.2%} |")


if __name__ == "__main__":
    main([int(x) for x in sys.argv[1].split(",")] if len(sys.argv) > 1 else list(range(15, 365, 30)))
