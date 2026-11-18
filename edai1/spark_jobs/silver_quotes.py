"""Spark job Bronze -> Silver cho quotes (bảng >= 100GB): quotes ⋈ inventory theo (hotel_id, room_type, stay_date).

Rubric edai-1 › Processing Jobs › Spark job to handle offline data problems (bài skew chạy trên volume thật):
  - quotes lệch theo Zipf của khách sạn + mùa cao điểm của stay_date; inventory ~50k × 3 × 665 đêm ≈ 100 triệu
    dòng nên không broadcast được -> sort-merge join, vài ô (khách sạn nóng) dồn vào 1 task (straggler trên Spark UI)
  - So sánh công bằng: cùng input, cùng sink, mỗi chế độ chỉ đổi 1 yếu tố so với baseline
      baseline  : AQE tắt, broadcast tắt (không tối ưu)
      aqe       : mặc định Spark (AQE + skewJoin, ngưỡng mặc định: partition > 5 × median và > 256MB)
      aqe_tuned : AQE skewJoin hạ ngưỡng theo dữ liệu (> 2 × median và > 64MB) + advisory partition 64MB
      salt      : AQE tắt, salting HOT_CELLS ô (hotel_id, room_type, stay_date) nóng nhất
    Chỉ cần salting khi aqe_tuned vẫn còn task chậm hơn hẳn median.
  - sink noop để đo thời gian xử lý; sink iceberg để ghi lake.silver.stg_quotes (DDL ở storage/optimize.sql)
Chạy: spark-submit --py-files silver_bookings.py silver_quotes.py <baseline|aqe|salt> <bronze_path> <noop|iceberg>
Proof: docs/edai-1/processing_jobs.md ghi thời gian, max/median task time, shuffle read của 3 chế độ + ảnh Spark UI.
"""
import sys

from pyspark.sql import DataFrame, SparkSession

from silver_bookings import build_spark, hot_keys, salted_join

KEYS = ("hotel_id", "room_type", "stay_date")
QUOTE_COLS = ["quote_id", "quoted_at", "hotel_id", "room_type", "stay_date", "nights", "rate_plan", "price",
              "available", "booked"]
MODES = ("baseline", "aqe", "aqe_tuned", "salt")
HOT_CELLS = 200
TUNED = {"spark.sql.adaptive.skewJoin.skewedPartitionFactor": "2",
         "spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes": "64MB",
         "spark.sql.adaptive.advisoryPartitionSizeInBytes": "64MB"}


def spark_for(mode: str) -> SparkSession:
    """SparkSession đúng cấu hình của chế độ (session có sẵn được cấu hình lại, test chạy nhiều chế độ liên tiếp)."""
    spark = build_spark(optimized=mode in ("aqe", "aqe_tuned"))
    spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1" if mode == "baseline" else "10MB")
    for k, v in TUNED.items():
        if mode == "aqe_tuned":
            spark.conf.set(k, v)
        else:
            spark.conf.unset(k)
    return spark


def enrich_quotes(quotes: DataFrame, inventory: DataFrame, mode: str) -> DataFrame:
    """Gắn số phòng mở bán của ô (hotel, room_type, đêm) vào từng lượt xem giá."""
    q, inv = quotes.select(*QUOTE_COLS), inventory.select(*KEYS, "rooms")
    if mode == "salt":
        # shortcut: hot_keys quét quotes thêm 1 lần trước join (không cache được ~104GB); dùng mẫu vài ngày để tìm
        # khoá nóng nếu salting trở thành chế độ chạy thật thay vì chế độ so sánh
        return salted_join(q, inv, hot_keys(q, KEYS, HOT_CELLS), keys=KEYS)
    return q.join(inv, list(KEYS))


if __name__ == "__main__":
    mode, bronze, sink = sys.argv[1:4]
    assert mode in MODES and sink in ("noop", "iceberg"), sys.argv
    spark = spark_for(mode)
    out = enrich_quotes(spark.read.parquet(f"{bronze}/raw_quotes"), spark.read.parquet(f"{bronze}/raw_inventory"), mode)
    if sink == "iceberg":
        out.writeTo("lake.silver.stg_quotes").overwritePartitions()      # chạy lại không sinh duplicate
    else:
        out.write.mode("overwrite").format("noop").save()
