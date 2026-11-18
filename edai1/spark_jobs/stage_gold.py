"""DP2 Silver -> staging Gold (PostgreSQL): chỉ những gì ngày ds làm thay đổi, rồi sql/dp2_upsert_gold.sql upsert vào dim/fact.

Gọi từ dags/dp2_bronze_to_gold.py: spark-submit stage_gold.py --ds 2025-03-01
  - gold.stg_bookings      : booking tạo trong ngày ds + booking huỷ trong ngày ds (cập nhật status của booking cũ)
  - gold.stg_customers     : khách của các booking trên (dim_customer chỉ nạp khách đã từng đặt, không nạp cả 30 triệu)
  - gold.stg_hotel_changes : mọi lần đổi giá có hiệu lực tới hết ngày ds; SCD2 chỉ áp lần đổi mới hơn bản đã có
  - gold.stg_hotel_rooms   : số phòng mở bán (tổng các loại phòng) của 30 đêm sau ds; SQL upsert vào gold.hotel_rooms
Postgres không đọc được Iceberg nên Spark ghi qua JDBC vào bảng staging (truncate giữ nguyên DDL ở gold_schema.sql);
bảng thật chỉ đổi trong transaction của dp2_upsert_gold.sql, không bị truncate khi tool đang đọc.
JDBC lấy từ biến môi trường WAREHOUSE_JDBC_* (Secret của Spark job).
"""
import argparse
import os

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

ROOM_HORIZON_DAYS = 30                       # = cửa sổ đêm revenue manager xét bán vượt
MAX_LEAD_DAYS = 240                       # = MAX_LEAD_DAYS của silver_bookings.py (mỗi job submit riêng, không import chéo)
BOOKING_COLS = ["booking_id", "customer_id", "hotel_id", "created_at", "checkin", "nights", "price",
                "cancellation_policy", "channel", "status", "cancelled_at"]


def to_postgres(df: DataFrame, table: str) -> None:
    (df.write.mode("overwrite").option("truncate", "true").format("jdbc")
     .option("url", os.environ["WAREHOUSE_JDBC_URL"]).option("dbtable", table)
     .option("user", os.environ["WAREHOUSE_JDBC_USER"]).option("password", os.environ["WAREHOUSE_JDBC_PASSWORD"])
     .option("driver", "org.postgresql.Driver").save())


def rooms_ahead(inventory: DataFrame, ds: str) -> DataFrame:
    """Tổng phòng mở bán theo hotel × đêm cho các đêm (ds, ds + ROOM_HORIZON_DAYS]."""
    stay = F.to_date("stay_date")
    day = F.to_date(F.lit(ds))
    return (inventory.filter((stay > day) & (stay <= F.date_add(day, ROOM_HORIZON_DAYS)))
            .groupBy("hotel_id", stay.alias("stay_date")).agg(F.sum("rooms").cast("int").alias("rooms")))


def changed_bookings(silver: DataFrame, ds: str) -> DataFrame:
    """Booking tạo hoặc huỷ trong ngày ds, ở trạng thái lúc hết ngày ds. Silver có thể đã biết lần huỷ sau ds (chạy lại
    ngày cũ, rebuild chế độ opt) nên lần huỷ muộn hơn bị bỏ, không lọt vào Gold.
    Hai vế lọc theo khoảng thời gian trên cột gốc (không bọc to_date): vế tạo mới khớp partition days(created_at) nên
    Iceberg chỉ đọc 1 partition; vế huỷ trong ngày dựa vào min/max cancelled_at của từng file để bỏ file."""
    start = F.to_timestamp(F.lit(ds))
    end = start + F.expr("INTERVAL 1 DAY")
    created = silver.filter((F.col("created_at") >= start) & (F.col("created_at") < end))
    # cận dưới created_at: Iceberg chỉ mở MAX_LEAD_DAYS partition gần nhất thay vì mọi partition lịch sử
    cancelled = silver.filter((F.col("cancelled_at") >= start) & (F.col("cancelled_at") < end)
                              & (F.col("created_at") < start)
                              & (F.col("created_at") >= start - F.expr(f"INTERVAL {MAX_LEAD_DAYS} DAYS")))
    known = F.when(F.col("cancelled_at") < end, F.col("cancelled_at"))
    return (created.unionByName(cancelled).withColumn("cancelled_at", known)
            .withColumn("status", F.when(F.col("cancelled_at").isNotNull(), "cancelled").otherwise("confirmed"))
            .select(*BOOKING_COLS))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ds", required=True)
    ap.add_argument("--bronze", default="s3a://lake/bronze")
    a = ap.parse_args()
    spark = SparkSession.builder.appName(f"stage_gold_{a.ds}").getOrCreate()
    bookings = changed_bookings(spark.table("lake.silver.stg_bookings"), a.ds).cache()
    to_postgres(bookings, "gold.stg_bookings")
    customers = spark.read.parquet(f"{a.bronze}/raw_customers").select("customer_id", "home_city", "loyalty_tier")
    to_postgres(customers.join(bookings.select("customer_id").distinct(), "customer_id"), "gold.stg_customers")
    hotels = spark.read.parquet(f"{a.bronze}/raw_hotels").select("hotel_id", "city", "stars")
    changes = spark.read.parquet(f"{a.bronze}/raw_hotel_changes") \
                   .filter(F.to_date("valid_from") <= F.to_date(F.lit(a.ds)))   # lần đổi tương lai chưa xảy ra
    to_postgres(changes.join(hotels, "hotel_id").select("hotel_id", "city", "stars", "price", "valid_from"),
                "gold.stg_hotel_changes")
    to_postgres(rooms_ahead(spark.read.parquet(f"{a.bronze}/raw_inventory"), a.ds), "gold.stg_hotel_rooms")
