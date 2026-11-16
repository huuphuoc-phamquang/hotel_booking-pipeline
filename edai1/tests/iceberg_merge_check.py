"""Chạy trong image Spark của dự án (k8s/spark.Dockerfile, có Iceberg): dựng Silver bằng đúng 2 câu MERGE của
silver_bookings.run_incremental theo từng ngày, so với dựng lại cả bảng từ Bronze. Gọi từ tests/test_silver_bookings.py:
  spark-submit tests/iceberg_merge_check.py <bronze> <warehouse>
Catalog `lake` kiểu hadoop trên đĩa cục bộ (thay JDBC catalog + MinIO của cluster); DDL lấy nguyên từ storage/optimize.sql.
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "spark_jobs"))
from pyspark.sql import SparkSession  # noqa: E402

from silver_bookings import (SILVER_COLS, dedup_bookings, merge_cancellations, merge_new_bookings,  # noqa: E402
                             read_bookings, with_cancellations)

bronze, warehouse = sys.argv[1], sys.argv[2]
spark = (SparkSession.builder.appName("iceberg_merge_check")
         .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
         .config("spark.sql.catalog.lake", "org.apache.iceberg.spark.SparkCatalog")
         .config("spark.sql.catalog.lake.type", "hadoop")
         .config("spark.sql.catalog.lake.warehouse", warehouse)
         .getOrCreate())
ddl = open(os.path.join(os.path.dirname(__file__), "..", "storage", "optimize.sql"), encoding="utf-8").read()
spark.sql(re.search(r"CREATE TABLE IF NOT EXISTS lake\.silver\.stg_bookings.*?;", ddl, re.S).group(0).rstrip(";"))

booking_days = {p[3:] for p in os.listdir(f"{bronze}/raw_bookings")}
cancel_days = {p[3:] for p in os.listdir(f"{bronze}/raw_cancellations")}
for ds in sorted(booking_days | cancel_days):
    if ds in booking_days:
        merge_new_bookings(spark, bronze, ds)
    if ds in cancel_days:
        merge_cancellations(spark, bronze, ds)
got = spark.table("lake.silver.stg_bookings").select(*SILVER_COLS)
hotels = spark.read.parquet(f"{bronze}/raw_hotels").select("hotel_id", "city", "stars")
want = with_cancellations(spark, bronze, dedup_bookings(read_bookings(spark, f"{bronze}/raw_bookings"))) \
    .join(hotels, "hotel_id").select(*SILVER_COLS)
n, only_merge, only_full = got.count(), got.exceptAll(want).count(), want.exceptAll(got).count()
last = max(booking_days)                                       # chạy lại 1 ngày: không đổi gì
merge_new_bookings(spark, bronze, last)
if last in cancel_days:
    merge_cancellations(spark, bronze, last)
diff = (only_merge, only_full, spark.table("lake.silver.stg_bookings").count() - n)
print(f"RESULT rows={n} only_merge={diff[0]} only_full={diff[1]} rerun_delta={diff[2]}")
assert n > 0 and diff == (0, 0, 0), diff
