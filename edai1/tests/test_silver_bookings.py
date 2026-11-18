"""silver_bookings + stage_gold trên Bronze dựng từ generator, qua mốc schema v2 (2025-07-01).

  - Schema evolution : file v1 (room_type, không channel) và v2 (room_category, channel) đọc chung không mất dòng
  - Double submit    : sau dedup mỗi idempotency_key đúng 1 dòng
  - Nhãn             : status lấy từ cancellations, đúng bằng kết cục generator sinh (không mất lần huỷ nào sau dedup)
  - Skew             : salted_join cho đúng kết quả như join thường
  - Incremental      : chèn booking từng ngày + áp lần huỷ từng ngày (như MERGE của run_incremental) = dựng lại cả bảng
  - stage_gold       : changed_bookings = booking tạo hoặc huỷ trong ngày ds; rooms_ahead = tổng inventory theo đêm
Cần pyspark + Java; chạy: pytest tests/test_silver_bookings.py"""
import sys
from pathlib import Path

import pandas as pd
import pytest

pyspark = pytest.importorskip("pyspark")
sys.path.insert(0, "spark_jobs")

from generator.offline_gen import (apply_schema_version, cancellations, gen_bookings, gen_dims,  # noqa: E402
                                   gen_inventory, load_config)
from silver_bookings import (build_spark, dedup_bookings, hot_keys, new_bookings, read_bookings,  # noqa: E402
                             salted_join, with_cancellations)
from stage_gold import changed_bookings, rooms_ahead  # noqa: E402

DAYS = (180, 181)                        # 2025-06-30 (v1) và 2025-07-01 (v2)
PQ = {"coerce_timestamps": "us", "allow_truncated_timestamps": True}


def small_config() -> dict:
    cfg = load_config("generator/config.yaml")
    cfg["dims"] = {"hotels": 300, "customers": 5000}
    return cfg


@pytest.fixture(scope="module")
def bronze(tmp_path_factory):
    cfg = small_config()
    cfg["shards_per_day"] = 2
    dims = gen_dims(cfg)
    root = tmp_path_factory.mktemp("bronze")
    truth = []
    for d in DAYS:
        day = pd.Timestamp(cfg["start_date"]) + pd.Timedelta(days=d)
        for s in range(2):
            b = gen_bookings(cfg, dims, d, s)
            truth.append(b)
            land = apply_schema_version(cfg, b.drop(columns=["status", "cancelled_at", "p_cancel_true"]), day)
            out = root / f"raw_bookings/dt={day:%Y-%m-%d}"
            out.mkdir(parents=True, exist_ok=True)
            land.to_parquet(out / f"shard={s:02d}.parquet", **PQ)
            c = cancellations(b)                                         # partition theo ngày huỷ như landing
            for cday, g in c.groupby(c["cancelled_at"].dt.strftime("%Y-%m-%d")):
                out = root / f"raw_cancellations/dt={cday}"
                out.mkdir(parents=True, exist_ok=True)
                g.to_parquet(out / f"part-{d}-{s}.parquet", **PQ)
    (root / "raw_hotels").mkdir()
    dims.hotels.to_parquet(root / "raw_hotels/part-0.parquet", **PQ)
    (root / "raw_inventory").mkdir()
    pd.concat([gen_inventory(cfg, dims, d) for d in range(DAYS[0], DAYS[0] + 40)]) \
        .to_parquet(root / "raw_inventory/part-0.parquet", **PQ)
    spark = build_spark(optimized=True)
    yield spark, str(root), pd.concat(truth, ignore_index=True), dims
    spark.stop()


def test_schema_dedup_and_labels(bronze):
    spark, root, truth, _ = bronze
    raw = read_bookings(spark, f"{root}/raw_bookings")
    assert raw.count() == len(truth)                                         # không mất dòng qua mốc v2
    silver = with_cancellations(spark, root, dedup_bookings(raw)).toPandas()
    first = truth.drop_duplicates("idempotency_key")
    assert len(silver) == len(first) and silver["idempotency_key"].is_unique
    assert silver["room_category"].notna().all()
    v1 = pd.to_datetime(silver["dt"]) < pd.Timestamp("2025-07-01")             # phiên bản schema theo partition dt
    assert silver.loc[v1, "channel"].isna().all() and silver.loc[~v1, "channel"].notna().all()
    # status sau dedup = kết cục thật của lần đặt đầu tiên (cancellations ghi theo idempotency_key)
    got = silver.set_index("idempotency_key")["status"].sort_index()
    want = first.set_index("idempotency_key")["status"].sort_index()
    pd.testing.assert_series_equal(got, want, check_names=False)


def test_salted_join_equals_plain_join(bronze):
    spark, root, _, _ = bronze
    b = dedup_bookings(read_bookings(spark, f"{root}/raw_bookings"))
    hotels = spark.read.parquet(f"{root}/raw_hotels").select("hotel_id", "city", "stars")
    cols = ["booking_id", "city", "stars"]
    plain = b.join(hotels, "hotel_id").select(*cols).toPandas().sort_values("booking_id").reset_index(drop=True)
    salted = salted_join(b, hotels, hot_keys(b, ("hotel_id",))).select(*cols).toPandas() \
        .sort_values("booking_id").reset_index(drop=True)
    pd.testing.assert_frame_equal(plain, salted)


def test_changed_bookings_for_ds(bronze):
    spark, root, _, _ = bronze
    silver = with_cancellations(spark, root, dedup_bookings(read_bookings(spark, f"{root}/raw_bookings")))
    got = changed_bookings(silver, "2025-07-01").toPandas()
    s = silver.toPandas()
    day = pd.Timestamp("2025-07-01")
    want = s[(s["created_at"].dt.normalize() == day) | (s["cancelled_at"].dt.normalize() == day)]
    assert set(got["booking_id"]) == set(want["booking_id"]) and len(got) > 0 and got["booking_id"].is_unique
    # silver dựng từ cả Bronze nên biết lần huỷ sau ds: staging phải nhìn như lúc hết ngày ds, không rò tương lai
    end = day + pd.Timedelta(days=1)
    known = want.set_index("booking_id")["cancelled_at"].where(lambda c: c < end)
    got = got.set_index("booking_id").loc[known.index]
    assert (got["cancelled_at"].isna() == known.isna()).all() and (s["cancelled_at"] >= end).any()
    assert (got["status"] == known.notna().map({True: "cancelled", False: "confirmed"})).all()


def test_incremental_equals_full_rebuild(bronze):
    """Mô phỏng 2 MERGE của run_incremental bằng pandas, ngày theo thứ tự: chèn booking mới theo idempotency_key,
    rồi áp lần huỷ của ngày đó; tới hết ngày huỷ cuối phải bằng with_cancellations trên toàn bộ Bronze."""
    spark, root, _, _ = bronze
    full = with_cancellations(spark, root, dedup_bookings(read_bookings(spark, f"{root}/raw_bookings"))).toPandas()
    booking_days = {p.name[3:] for p in Path(root, "raw_bookings").iterdir()}
    cancel_days = {p.name[3:] for p in Path(root, "raw_cancellations").iterdir()}
    silver = None
    for ds in sorted(booking_days | cancel_days):
        if ds in booking_days:
            new = new_bookings(spark, root, ds).toPandas()
            silver = new if silver is None else \
                pd.concat([silver, new[~new["idempotency_key"].isin(silver["idempotency_key"])]], ignore_index=True)
        if ds in cancel_days:
            c = spark.read.parquet(f"{root}/raw_cancellations/dt={ds}").toPandas()
            c = c.set_index("booking_id")["cancelled_at"]
            hit = silver["booking_id"].isin(c.index)
            silver.loc[hit, "status"] = "cancelled"
            silver.loc[hit, "cancelled_at"] = silver.loc[hit, "booking_id"].map(c)
    label = lambda df: df.set_index("booking_id")[["status", "cancelled_at"]].sort_index() \
        .astype({"cancelled_at": "datetime64[ns]"})                     # Spark trả giây, pandas ns: so cùng đơn vị
    pd.testing.assert_frame_equal(label(silver), label(full), check_dtype=False)


def test_rooms_ahead(bronze):
    spark, root, _, dims = bronze
    got = rooms_ahead(spark.read.parquet(f"{root}/raw_inventory"), "2025-07-01").toPandas()
    assert got["stay_date"].nunique() == 30 and str(got["stay_date"].min()) == "2025-07-02"
    want = gen_inventory(small_config(), dims, 182).groupby("hotel_id")["rooms"].sum().sort_index()
    day = got[got["stay_date"].astype(str) == "2025-07-02"].set_index("hotel_id")["rooms"].sort_index()
    pd.testing.assert_series_equal(day, want, check_names=False, check_dtype=False, check_index_type=False)


def test_incremental_merge_on_iceberg(bronze):
    """2 câu MERGE thật của run_incremental trên Iceberg (image k8s/spark.Dockerfile), từng ngày theo thứ tự,
    = dựng lại cả bảng; chạy lại 1 ngày không đổi số dòng. Cần Docker + image booking-spark:local."""
    import shutil
    import subprocess
    # docker run thay vì image inspect: store containerd của Docker Desktop có khi inspect theo tag báo không thấy
    if not shutil.which("docker") or subprocess.run(["docker", "run", "--rm", "--entrypoint", "true",
                                                     "booking-spark:local"], capture_output=True).returncode:
        pytest.skip("cần Docker + image booking-spark:local")
    _, root, _, _ = bronze
    r = subprocess.run(["docker", "run", "--rm", "-v", f"{Path.cwd()}:/work:ro", "-v", f"{root}:/bronze:ro",
                        "booking-spark:local", "/opt/spark/bin/spark-submit", "/work/tests/iceberg_merge_check.py",
                        "/bronze", "/tmp/wh"], capture_output=True, text=True, timeout=1200)
    assert r.returncode == 0 and "RESULT" in r.stdout, (r.stdout + r.stderr)[-3000:]
