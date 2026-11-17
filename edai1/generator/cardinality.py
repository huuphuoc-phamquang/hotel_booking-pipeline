"""Cardinality từng cột (số giá trị khác nhau / số dòng) và histogram skew, in bảng markdown cho
docs/edai-1/data_generator.md › Simulate skew.

Chạy từ thư mục edai1:  python -m generator.cardinality [ngày, mặc định 195] [file png]
Mẫu: quotes 1 shard của ngày đó (~2,4 triệu dòng; giữ cả ngày thì hết RAM), bookings landing đủ shard của ngày đó.
Tỉ lệ đo trên mẫu 1 ngày: cột như customer_id có tỉ lệ cao hơn khi đo cả năm vì khách ít khi đặt lại trong 1 ngày.
"""
import sys

import numpy as np
import pandas as pd

from generator.offline_gen import apply_schema_version, gen_bookings, gen_dims, gen_quotes, load_config


def cardinality(df: pd.DataFrame) -> pd.DataFrame:
    """Mỗi cột: số giá trị khác nhau, tỉ lệ trên số dòng, mức (high ≥ 50%, low < 1%)."""
    n = len(df)
    u = df.nunique()
    level = np.select([u / n >= 0.5, u / n < 0.01], ["high", "low"], "medium")
    return pd.DataFrame({"unique": u, "ratio": u / n, "level": level})


def main(day: int, png: str | None) -> None:
    cfg = load_config("generator/config.yaml")
    dims = gen_dims(cfg)
    date = pd.Timestamp(cfg["start_date"]) + pd.Timedelta(days=day)
    q_hotel, b_all = pd.Series(dtype=float), []
    for s in range(cfg["shards_per_day"]):
        q = gen_quotes(cfg, dims, day, s)
        b = gen_bookings(cfg, dims, day, s, q)
        b_all.append(apply_schema_version(cfg, b.drop(columns=["status", "cancelled_at", "p_cancel_true"]), date))
        q_hotel = q_hotel.add(q.groupby("hotel_id").size(), fill_value=0)
        if s == 0:
            q0 = q
    b = pd.concat(b_all, ignore_index=True)

    print(f"Ngày {date.date()}: quotes shard 0 = {len(q0):,} dòng, bookings đủ shard = {len(b):,} dòng\n")
    for name, df in (("quotes", q0), ("bookings", b)):
        print(f"| {name}: cột | Số giá trị khác nhau | Tỉ lệ / số dòng | Mức |\n|---|---|---|---|")
        for col, r in cardinality(df).sort_values("ratio", ascending=False).iterrows():
            print(f"| `{col}` | {r['unique']:,} | {r['ratio']:.4%} | {r['level']} |")
        print()

    cell = q0.groupby(["hotel_id", "room_type", "stay_date"]).size()
    print(f"| Lượt xem / ô (hotel, room_type, stay_date), shard 0 | Giá trị |\n|---|---|")
    for label, v in (("số ô", len(cell)), ("trung vị", cell.median()), ("p99", cell.quantile(0.99)), ("max", cell.max())):
        print(f"| {label} | {v:,.0f} |")

    if png:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        b_hotel = b.drop_duplicates("idempotency_key").groupby("hotel_id").size()
        fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4))
        for c, label in ((q_hotel, "lượt xem"), (b_hotel, "booking")):
            v = np.sort(c.values)[::-1]
            a1.loglog(np.arange(1, len(v) + 1), v, label=label)
        a1.set(title=f"Số dòng / khách sạn theo hạng, {date.date()}", xlabel="hạng khách sạn", ylabel="số dòng")
        a1.legend()
        a2.hist(cell.values, bins=np.logspace(0, np.log10(cell.max() + 1), 40))
        a2.set(xscale="log", yscale="log", title="Lượt xem / ô (hotel, room_type, stay_date)",
               xlabel="lượt xem trong ô", ylabel="số ô")
        fig.tight_layout()
        fig.savefig(png, dpi=120)
        print(f"\nđã lưu {png}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 195, sys.argv[2] if len(sys.argv) > 2 else None)
