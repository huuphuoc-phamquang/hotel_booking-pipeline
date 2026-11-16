"""Spark job Bronze -> Silver cho bookings: xử lý skew, schema evolution và double submit.

Rubric edai-1 › Processing Jobs › Spark job to handle offline data problems:
  - Baseline (without optimization) : run_baseline() — join thẳng với hotels, AQE tắt, không dedup
  - Handle skew with explanation    : bài skew chính ở silver_quotes.py (quotes ⋈ inventory, 4 cấu hình); ở đây hotels
                                      nhỏ (~1-2 MB) nên Spark tự broadcast, salting chỉ để so với broadcast
  - Handle schema evolution         : mergeSchema + gộp room_type/room_category, thêm channel null cho dữ liệu v1
  - Handle other offline problem    : dedup theo idempotency_key, giữ bản created_at sớm nhất
  - Tích hợp vào data pipeline      : DAG dp2_bronze_to_gold gọi chế độ incr mỗi ngày (chỉ đọc partition dt=ds);
                                      chế độ opt dựng lại cả bảng từ Bronze (backfill, đo skew)
Bronze là Parquet (copy nguyên từ landing), Silver là bảng Iceberg lake.silver.stg_bookings
(tạo bởi storage/optimize.sql); catalog `lake` cấu hình qua --conf của Connection spark_default.
Proof: docs/Spark.md chụp Spark UI (1 task chạy rất lâu ở baseline vs các task đều nhau sau salting).
"""
import sys
from datetime import date, timedelta

from pyspark.sql import DataFrame, SparkSession, Window
from pyspark.sql import functions as F

SALT_BUCKETS = 16
HOT_TOP_N = 20
MAX_LEAD_DAYS = 240                       # = HORIZON_DAYS của generator/offline_gen.py: lead time dài nhất
SILVER_COLS = ["booking_id", "idempotency_key", "customer_id", "hotel_id", "city", "stars", "room_category",
               "cancellation_policy", "channel", "created_at", "checkin", "nights", "price", "status", "cancelled_at"]


def build_spark(optimized: bool) -> SparkSession:
    """Tạo SparkSession; bật/tắt AQE để so sánh baseline với bản tối ưu. Giữ ngưỡng broadcast mặc định: dimension
    nhỏ (hotels) thì broadcast là cách xử lý skew rẻ nhất; bài cần tắt broadcast tự đặt (silver_quotes baseline)."""
    return (
        SparkSession.builder.appName(f"silver_bookings_{'opt' if optimized else 'baseline'}")
        .config("spark.sql.adaptive.enabled", str(optimized).lower())
        .config("spark.sql.adaptive.skewJoin.enabled", str(optimized).lower())
        .getOrCreate()
    )


def read_bookings(spark: SparkSession, path: str, ds: str | None = None) -> DataFrame:
    """Đọc bookings có 2 phiên bản schema và đưa về một schema chung; ds thì chỉ đọc partition dt=ds (giữ cột dt)."""
    reader = spark.read.option("mergeSchema", "true")
    df = reader.option("basePath", path).parquet(f"{path}/dt={ds}") if ds else reader.parquet(path)
    if "room_category" not in df.columns:                   # chỉ có file v1
        df = df.withColumnRenamed("room_type", "room_category")
    elif "room_type" in df.columns:                         # có cả v1 và v2: cột cũ null ở file mới và ngược lại
        df = df.withColumn("room_category", F.coalesce("room_category", "room_type")).drop("room_type")
    if "channel" not in df.columns:                          # cột mới của v2
        df = df.withColumn("channel", F.lit(None).cast("string"))
    return df


def dedup_bookings(bookings: DataFrame) -> DataFrame:
    """Bỏ bản gửi trùng: cùng idempotency_key, giữ dòng created_at nhỏ nhất (hoà thì booking_id nhỏ nhất)."""
    w = Window.partitionBy("idempotency_key").orderBy(F.col("created_at").asc(), F.col("booking_id").asc())
    return bookings.withColumn("rn", F.row_number().over(w)).filter("rn = 1").drop("rn")


def hot_keys(df: DataFrame, keys: tuple, top_n: int = HOT_TOP_N) -> DataFrame:
    """top_n giá trị khoá nóng nhất (đầu phân phối Zipf / mùa cao điểm), cột hot = True, để salting."""
    return df.groupBy(*keys).count().orderBy(F.desc("count")).limit(top_n).drop("count").withColumn("hot", F.lit(True))


def salted_join(left: DataFrame, right: DataFrame, hot: DataFrame, keys: tuple = ("hotel_id",)) -> DataFrame:
    """Rải mỗi khoá nóng bên trái ra SALT_BUCKETS partition, nhân bản dòng bên phải tương ứng; join theo keys + salt.
    Danh sách khoá nóng nhỏ nên broadcast để đánh dấu (silver_quotes dùng keys = hotel_id, room_type, stay_date)."""
    mark = lambda df: df.join(F.broadcast(hot), list(keys), "left")
    l = mark(left).withColumn("salt", F.when(F.col("hot"), (F.rand(seed=7) * SALT_BUCKETS).cast("int"))
                                       .otherwise(F.lit(0))).drop("hot")
    r = mark(right).withColumn("salt", F.explode(F.when(F.col("hot"), F.sequence(F.lit(0), F.lit(SALT_BUCKETS - 1)))
                                                  .otherwise(F.array(F.lit(0))))).drop("hot")
    return l.join(r, [*keys, "salt"]).drop("salt")


def run_baseline(spark: SparkSession, bronze: str) -> DataFrame:
    """Baseline: không dedup, không salting — dùng để đo trên Spark UI."""
    bookings = read_bookings(spark, f"{bronze}/raw_bookings")
    hotels = spark.read.parquet(f"{bronze}/raw_hotels").select("hotel_id", "city", "stars")
    return bookings.join(hotels, "hotel_id")


def with_cancellations(spark: SparkSession, bronze: str, bookings: DataFrame) -> DataFrame:
    """status/cancelled_at lấy từ bảng cancellations (theo ngày huỷ): landing bookings chỉ là bản ghi lúc đặt.
    Dùng khi dựng lại cả bảng; chạy hằng ngày thì run_incremental MERGE lần huỷ của ngày ds."""
    c = spark.read.parquet(f"{bronze}/raw_cancellations").select("booking_id", "cancelled_at")
    return (bookings.join(c, "booking_id", "left")
            .withColumn("status", F.when(F.col("cancelled_at").isNotNull(), "cancelled").otherwise("confirmed")))


def run_optimized(spark: SparkSession, bronze: str) -> None:
    """Bản tối ưu: schema chung + dedup + gộp lần huỷ + salted join, ghi đè đúng các partition ngày có trong input."""
    bookings = with_cancellations(spark, bronze, dedup_bookings(read_bookings(spark, f"{bronze}/raw_bookings"))).cache()
    hotels = spark.read.parquet(f"{bronze}/raw_hotels").select("hotel_id", "city", "stars")
    silver = salted_join(bookings, hotels, hot_keys(bookings, ("hotel_id",))).select(*SILVER_COLS)
    silver.writeTo("lake.silver.stg_bookings").overwritePartitions()   # chạy lại không sinh duplicate


def new_bookings(spark: SparkSession, bronze: str, ds: str) -> DataFrame:
    """Booking tạo trong ngày ds: dedup, enrich hotels, status confirmed (lần huỷ áp sau theo ngày huỷ)."""
    new = dedup_bookings(read_bookings(spark, f"{bronze}/raw_bookings", ds)) \
        .withColumn("status", F.lit("confirmed")).withColumn("cancelled_at", F.lit(None).cast("timestamp"))
    hotels = spark.read.parquet(f"{bronze}/raw_hotels").select("hotel_id", "city", "stars")
    return salted_join(new, hotels, hot_keys(new, ("hotel_id",))).select(*SILVER_COLS)


def merge_new_bookings(spark: SparkSession, bronze: str, ds: str) -> None:
    """Chèn booking tạo trong ngày ds theo idempotency_key (bản gửi trùng lấn sang ngày sau bị bỏ, giữ bản sớm nhất
    như dedup_bookings). Bản gửi trùng chỉ có thể nằm ở ngày ds - 1, nên điều kiện created_at trên bảng đích để
    Iceberg chỉ quét 2 partition days(created_at) thay vì cả bảng."""
    since = date.fromisoformat(ds) - timedelta(days=1)       # fromisoformat cũng chặn chuỗi lạ chèn vào SQL
    new_bookings(spark, bronze, ds).createOrReplaceTempView("new_bookings")
    spark.sql(f"""MERGE INTO lake.silver.stg_bookings t USING new_bookings s
                  ON t.idempotency_key = s.idempotency_key AND t.created_at >= TIMESTAMP '{since}'
                  WHEN NOT MATCHED THEN INSERT *""")


def merge_cancellations(spark: SparkSession, bronze: str, ds: str) -> None:
    """Áp các lần huỷ xảy ra trong ngày ds; booking bị huỷ hôm nay tạo không quá MAX_LEAD_DAYS trước đó."""
    since = date.fromisoformat(ds) - timedelta(days=MAX_LEAD_DAYS)
    spark.read.parquet(f"{bronze}/raw_cancellations/dt={ds}").select("booking_id", "cancelled_at") \
        .createOrReplaceTempView("new_cancels")
    spark.sql(f"""MERGE INTO lake.silver.stg_bookings t USING new_cancels s
                  ON t.booking_id = s.booking_id AND t.created_at >= TIMESTAMP '{since}'
                  WHEN MATCHED THEN UPDATE SET status = 'cancelled', cancelled_at = s.cancelled_at""")


def run_incremental(spark: SparkSession, bronze: str, ds: str) -> None:
    """Chỉ đọc partition dt=ds: chèn booking mới rồi áp lần huỷ trong ngày. Chạy lại cùng ds không đổi gì."""
    merge_new_bookings(spark, bronze, ds)
    merge_cancellations(spark, bronze, ds)


if __name__ == "__main__":
    mode, bronze_path = sys.argv[1], sys.argv[2]
    session = build_spark(optimized=(mode != "baseline"))
    if mode == "incr":
        run_incremental(session, bronze_path, sys.argv[3])
    elif mode == "opt":
        run_optimized(session, bronze_path)
    else:
        run_baseline(session, bronze_path).write.mode("overwrite").format("noop").save()
