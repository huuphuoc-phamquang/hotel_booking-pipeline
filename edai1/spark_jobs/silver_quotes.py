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
  - Join theo cả 3 cột băm ô nóng ra 1.500 partition nên lệch bị dàn đều (đo trên GKE: partition lớn nhất 1,15 ×
    trung vị, AQE không tách). Bài skew thật: quotes ⋈ hotels chỉ theo hotel_id, khách sạn nóng nhất (~2,6% lượt
    xem, Zipf a = 0,8) dồn vào 1 partition ~40 × trung vị:
      hotel_baseline  : AQE tắt, broadcast tắt -> sort-merge join, 1 task straggler
      hotel_aqe       : AQE skewJoin mặc định, broadcast tắt -> AQE tách partition lệch
      hotel_broadcast : broadcast hotels (50k dòng) -> không shuffle quotes
  - sink noop để đo thời gian xử lý; sink iceberg để ghi lake.silver.stg_quotes (DDL ở storage/optimize.sql)
Chạy: spark-submit --py-files silver_bookings.py silver_quotes.py <mode|hotel_mode> <bronze_path> <noop|iceberg> [quotes_path]
Proof: docs/edai-1/processing_jobs.md ghi thời gian, max/median task time, shuffle read của 3 chế độ + ảnh Spark UI.
"""
import sys

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from silver_bookings import build_spark, hot_keys, salted_join

KEYS = ("hotel_id", "room_type", "stay_date")
QUOTE_COLS = ["quote_id", "quoted_at", "hotel_id", "room_type", "stay_date", "nights", "rate_plan", "price",
              "available", "booked"]
MODES = ("baseline", "aqe", "aqe_tuned", "salt")
HOTEL_MODES = ("hotel_baseline", "hotel_aqe", "hotel_broadcast")
HOT_CELLS = 200
TUNED = {"spark.sql.adaptive.skewJoin.skewedPartitionFactor": "2",
         "spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes": "64MB",
         "spark.sql.adaptive.advisoryPartitionSizeInBytes": "64MB"}


def spark_for(mode: str) -> SparkSession:
    """SparkSession đúng cấu hình của chế độ (session có sẵn được cấu hình lại, test chạy nhiều chế độ liên tiếp)."""
    spark = build_spark(optimized=mode in ("aqe", "aqe_tuned", "hotel_aqe", "hotel_broadcast"))
    # bài hotel_* tắt broadcast tự động để AQE phải xử lý skew; hotel_broadcast dùng hint F.broadcast
    no_bc = mode == "baseline" or mode in HOTEL_MODES
    spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1" if no_bc else "10MB")
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


def enrich_hotels(quotes: DataFrame, hotels: DataFrame, mode: str) -> DataFrame:
    """Gắn thành phố, hạng sao của khách sạn vào lượt xem giá; khoá join chỉ là hotel_id (skew theo Zipf)."""
    h = hotels.select("hotel_id", "city", "stars")
    return quotes.select(*QUOTE_COLS).join(F.broadcast(h) if mode == "hotel_broadcast" else h, "hotel_id")


if __name__ == "__main__":
    mode, bronze, sink = sys.argv[1:4]
    assert (mode in MODES and sink in ("noop", "iceberg")) or (mode in HOTEL_MODES and sink == "noop"), sys.argv
    # tham số 4 (tuỳ chọn): đọc quotes thẳng từ landing (cùng file Parquet DP1 chép sang Bronze) khi Bronze chưa đủ năm
    quotes_path = sys.argv[4] if len(sys.argv) > 4 else f"{bronze}/raw_quotes"
    spark = spark_for(mode)
    quotes = spark.read.parquet(quotes_path)
    if mode in HOTEL_MODES:
        out = enrich_hotels(quotes, spark.read.parquet(f"{bronze}/raw_hotels"), mode)
    else:
        out = enrich_quotes(quotes, spark.read.parquet(f"{bronze}/raw_inventory"), mode)
    if sink == "iceberg":
        out.writeTo("lake.silver.stg_quotes").overwritePartitions()      # chạy lại không sinh duplicate
    else:
        out.write.mode("overwrite").format("noop").save()
