"""Số đo cho rubric edai-1 dòng 13 (schema evolution) và 14 (double submit) trên toàn bộ bookings, dùng đúng
read_bookings / dedup_bookings của silver_bookings.py.
Chạy: spark-submit --py-files silver_bookings.py bookings_quality.py s3a://landing/bookings"""
import sys

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

from silver_bookings import dedup_bookings, read_bookings

V2 = "2025-07-01"   # anomalies.schema_v2_date trong generator/config.yaml

if __name__ == "__main__":
    spark = SparkSession.builder.appName("bookings_quality").getOrCreate()
    path = sys.argv[1]
    raw = spark.read.option("mergeSchema", "true").parquet(path)
    print("raw columns:", sorted(raw.columns))
    print("rows by schema version (theo dt):")
    raw.groupBy(F.when(F.col("dt") < V2, "v1").otherwise("v2").alias("v")).agg(
        F.count("*").alias("rows"),
        F.count("room_type").alias("room_type_not_null"),
        F.count("room_category").alias("room_category_not_null"),
        F.count("channel").alias("channel_not_null")).orderBy("v").show()

    df = read_bookings(spark, path).cache()
    print("sau read_bookings:")
    df.groupBy(F.when(F.col("dt") < V2, "v1").otherwise("v2").alias("v")).agg(
        F.count("*").alias("rows"),
        F.sum(F.col("room_category").isNull().cast("int")).alias("room_category_null"),
        F.sum(F.col("channel").isNull().cast("int")).alias("channel_null")).orderBy("v").show()

    n, keys = df.count(), df.select("idempotency_key").distinct().count()
    deduped = dedup_bookings(df).count()
    print(f"double submit: rows={n} distinct_idempotency_key={keys} after_dedup={deduped} "
          f"removed={n - deduped} ({(n - deduped) / n:.3%})")
