-- Tối ưu lưu trữ cho lakehouse (Iceberg trên MinIO, chạy bằng Spark SQL) và data warehouse (PostgreSQL).
-- Rubric edai-1 › Data Storage › How to optimize your data storage:
--   - Lakehouse     : partitioning + compaction (gom file nhỏ) + z-order
--   - Datawarehouse : indexing
-- Proof: docs/Storage.md ghi số file / kích thước file trung bình / thời gian query TRƯỚC và SAU,
--        kèm EXPLAIN ANALYZE của PostgreSQL trước và sau khi tạo index.

-- ===== Lakehouse (Spark SQL + Iceberg) =====

-- 1) Partitioning: Silver phân vùng theo ngày tạo booking -> query lọc theo ngày chỉ đọc vài partition
CREATE TABLE IF NOT EXISTS lake.silver.stg_bookings (
    booking_id           BIGINT,
    idempotency_key      BIGINT,
    customer_id          BIGINT,
    hotel_id             BIGINT,
    city                 STRING,
    stars                BIGINT,
    room_category        STRING,
    cancellation_policy  STRING,
    channel              STRING,
    created_at           TIMESTAMP,
    checkin              TIMESTAMP,
    nights               BIGINT,
    price                DOUBLE,
    status               STRING,
    cancelled_at         TIMESTAMP
) USING iceberg
PARTITIONED BY (days(created_at));

-- Silver quotes (bảng >= 100GB, spark_jobs/silver_quotes.py): lượt xem giá + số phòng mở bán của ô
CREATE TABLE IF NOT EXISTS lake.silver.stg_quotes (
    quote_id      BIGINT,
    quoted_at     TIMESTAMP,
    hotel_id      BIGINT,
    room_type     STRING,
    stay_date     TIMESTAMP,
    nights        BIGINT,
    rate_plan     STRING,
    price         DOUBLE,
    available     BOOLEAN,
    booked        BOOLEAN,
    rooms         INT
) USING iceberg
PARTITIONED BY (days(quoted_at));

-- 2) Compaction: mỗi ngày 16 shard + các lần chạy lại sinh nhiều file nhỏ -> gom thành file ~512MB
CALL lake.system.rewrite_data_files(
    table   => 'silver.stg_bookings',
    options => map('target-file-size-bytes', '536870912', 'min-input-files', '5')
);

-- 3) Z-order: query hay lọc cùng lúc theo khách sạn và ngày nhận phòng -> min/max stats chặt hơn, skip nhiều file hơn
CALL lake.system.rewrite_data_files(
    table      => 'silver.stg_bookings',
    strategy   => 'sort',
    sort_order => 'zorder(hotel_id, checkin)'
);

-- 4) Dọn snapshot cũ để không giữ file rác sau compaction
CALL lake.system.expire_snapshots(table => 'silver.stg_bookings', older_than => TIMESTAMP '2025-06-01 00:00:00');

-- Kiểm tra hiệu quả: số file và kích thước trung bình
SELECT count(*) AS num_files, avg(file_size_in_bytes) / 1024 / 1024 AS avg_mb
FROM lake.silver.stg_bookings.files;

-- ===== Data warehouse (PostgreSQL, schema gold) =====

-- Query hay chạy: số đêm đã bán của 1 khách sạn trong tháng (dashboard revenue management)
EXPLAIN ANALYZE
SELECT hotel_key, sum(nights) AS room_nights, sum(amount) AS revenue
FROM gold.fact_bookings
WHERE hotel_key = 1024 AND checkin_date BETWEEN '2025-03-01' AND '2025-03-31' AND status = 'confirmed'
GROUP BY hotel_key;

-- B-tree composite index: cột lọc bằng (=) đặt trước, cột lọc khoảng đặt sau
CREATE INDEX IF NOT EXISTS idx_fact_bookings_hotel_checkin
    ON gold.fact_bookings (hotel_key, checkin_date);

-- BRIN index: bảng fact rất lớn, booking_date tăng dần theo thứ tự ghi -> index rất nhỏ
CREATE INDEX IF NOT EXISTS brin_fact_bookings_date
    ON gold.fact_bookings USING brin (booking_date);

-- Partial index: chỉ index dòng hiện hành của dim SCD2
CREATE INDEX IF NOT EXISTS idx_dim_hotel_current
    ON gold.dim_hotel (hotel_id) WHERE is_current;

ANALYZE gold.fact_bookings;
