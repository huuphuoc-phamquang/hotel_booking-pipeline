"""DP1 ingest: copy nguyên 1 ngày của 1 bảng từ landing sang Bronze (Parquet, không biến đổi).

Gọi từ dags/dp1_ingest_bronze.py: spark-submit landing_to_bronze.py --table bookings --ds 2025-03-01
Ghi đè đúng thư mục dt=ds nên chạy lại cùng ngày không sinh duplicate. s3a endpoint/khoá lấy từ Connection spark_default.
Dim (hotels, hotel_changes, customers, inventory) không chia theo ngày: bỏ --ds thì copy cả bảng (DAG dp1_load_dims).
"""
import argparse

from pyspark.sql import SparkSession

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", required=True)
    ap.add_argument("--ds")
    a = ap.parse_args()
    spark = SparkSession.builder.appName(f"landing_to_bronze_{a.table}_{a.ds or 'dim'}").getOrCreate()
    if a.ds is None:
        # inventory có thư mục stay_date= trùng tên cột trong file: tắt partition discovery để không báo trùng cột
        df = spark.read.option("recursiveFileLookup", "true").parquet(f"s3a://landing/{a.table}/")
        df.write.mode("overwrite").parquet(f"s3a://lake/bronze/raw_{a.table}")
    else:
        # shard=XX trong đường dẫn thành cột shard; dt nằm ở thư mục đích nên Spark đọc Bronze vẫn thấy cột dt
        df = spark.read.parquet(f"s3a://landing/{a.table}/dt={a.ds}/")
        df.write.mode("overwrite").parquet(f"s3a://lake/bronze/raw_{a.table}/dt={a.ds}")
