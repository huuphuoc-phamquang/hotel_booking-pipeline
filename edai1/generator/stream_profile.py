"""Đo lỗi streaming generator cài vào event log (late arrival theo nguồn, callback gửi lặp, vi phạm contract), in bảng
markdown cho docs/edai-1/data_generator.md › Simulate late arrivals / another streaming data problem.

Chạy từ thư mục edai1:  python -m generator.stream_profile [ngày, mặc định 195] [file png histogram]
Mẫu: event của mọi booking tạo trong ngày đó, đủ shard (cùng gen_events mà replayer phát vào Kafka).
"""
import sys

import numpy as np
import pandas as pd

from generator.offline_gen import gen_dims, load_config
from generator.stream_gen import gen_events

WM_MIN, LATENESS_MIN = 10, 5      # watermark và allowedLateness của flink_jobs/booking_events_window.py


def main(day: int, png: str | None) -> None:
    cfg = load_config("generator/config.yaml")
    dims = gen_dims(cfg)
    ev = pd.concat([gen_events(cfg, dims, day, s) for s in range(cfg["shards_per_day"])], ignore_index=True)
    date = (pd.Timestamp(cfg["start_date"]) + pd.Timedelta(days=day)).date()
    ok = ev[ev["violation"].isna()]
    created = ok[ok["type"] == "booking_created"]
    callbacks = ok[ok["type"] == "payment_callback"]
    delay = (ok["ingest_time"] - ok["event_time"]) / 60_000
    source = np.where(ok["type"] == "booking_created", "booking_created · " + ok["device"].astype(str), ok["type"])

    print(f"Ngày {date}, đủ {cfg['shards_per_day']} shard: {len(ev):,} event\n")
    print("| Nguồn | Event | Trễ trung vị | p99 | Max | Trễ > 10 phút | Trễ > 15 phút |\n|---|---|---|---|---|---|---|")
    for name, d in delay.groupby(source):
        print(f"| {name} | {len(d):,} | {d.median():.2f} phút | {d.quantile(.99):.1f} phút | {d.max():.0f} phút "
              f"| {(d > WM_MIN).mean():.2%} | {(d > WM_MIN + LATENESS_MIN).mean():.2%} |")

    dup_cb = callbacks["event_id"].duplicated()
    dup_bk = created["idempotency_key"].duplicated()
    print("\n| Lỗi stream | Số event | Tỉ lệ |\n|---|---|---|")
    print(f"| payment_callback gửi lặp (cùng event_id) | {dup_cb.sum():,} | {dup_cb.sum() / (~dup_cb).sum():.2%} callback |")
    print(f"| booking_created double submit (cùng idempotency_key) | {dup_bk.sum():,} | "
          f"{dup_bk.sum() / (~dup_bk).sum():.2%} booking |")
    for reason, n in ev["violation"].value_counts().sort_index().items():
        print(f"| vi phạm contract: `{reason}` | {n:,} | {n / len(created):.3%} booking_created |")

    if png:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(9, 4))
        bins = np.logspace(-3, np.log10(delay.max() + 1), 60)
        for name in sorted(set(source)):
            ax.hist(delay[source == name], bins=bins, histtype="step", linewidth=1.5, label=name)
        for x, label in ((WM_MIN, "watermark 10'"), (WM_MIN + LATENESS_MIN, "+ lateness 5'")):
            ax.axvline(x, color="k", linestyle="--", linewidth=1)
            ax.text(x, ax.get_ylim()[1] * 0.5, label, rotation=90, ha="right", va="center", fontsize=8)
        ax.set(xscale="log", yscale="log", xlabel="ingest_time − event_time (phút)", ylabel="số event",
               title=f"Độ trễ event theo nguồn, {date}")
        ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(png, dpi=120)
        print(f"\nđã lưu {png}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 195, sys.argv[2] if len(sys.argv) > 2 else None)
