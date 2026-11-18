-- Tối ưu lưu trữ cho lakehouse (Iceberg trên MinIO, chạy bằng Spark SQL) và data warehouse (PostgreSQL).
-- Rubric edai-1 › Data Storage › How to optimize your data storage:
--   - Lakehouse     : partitioning + compaction (gom file nhỏ) + z-order
--   - Datawarehouse : indexing
-- Proof: docs/edai-1/data_storage.md ghi số file / kích thước file trung bình / thời gian query TRƯỚC và SAU,
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

-- 2) Compaction + z-order trong 1 lần ghi lại: mỗi ngày 16 shard + các lần chạy lại sinh nhiều file nhỏ -> gom thành
--    file ~512MB, đồng thời sắp theo z-order (hotel_id, checkin) vì query hay lọc cùng lúc khách sạn và ngày nhận phòng
--    -> min/max stats chặt hơn, bỏ được nhiều file hơn. Chạy riêng binpack rồi sort thì dữ liệu bị ghi lại 2 lần.
CALL lake.system.rewrite_data_files(
    table      => 'silver.stg_bookings',
    strategy   => 'sort',
    sort_order => 'zorder(hotel_id, checkin)',
    options    => map('target-file-size-bytes', '536870912', 'min-input-files', '5')
);

-- Bảng lớn nhất (stg_quotes ~104GB/năm): gom file theo partition ngày, sắp theo khoá join của bài skew
CALL lake.system.rewrite_data_files(
    table      => 'silver.stg_quotes',
    strategy   => 'sort',
    sort_order => 'zorder(hotel_id, stay_date)',
    options    => map('target-file-size-bytes', '536870912', 'min-input-files', '5')
);

-- 3) Dọn snapshot cũ để không giữ file rác sau compaction: giữ 7 ngày gần nhất (mốc tính lúc chạy, không viết cứng)
CALL lake.system.expire_snapshots(table => 'silver.stg_bookings', older_than => current_timestamp() - INTERVAL 7 DAYS);
CALL lake.system.expire_snapshots(table => 'silver.stg_quotes', older_than => current_timestamp() - INTERVAL 7 DAYS);

-- Kiểm tra hiệu quả: số file và kích thước trung bình
SELECT count(*) AS num_files, avg(file_size_in_bytes) / 1024 / 1024 AS avg_mb
FROM lake.silver.stg_bookings.files;

-- ===== Data warehouse (PostgreSQL, schema gold) =====

-- Query hay chạy: số đêm đã bán của 1 khách sạn trong tháng (dashboard revenue management). Lọc theo hotel_id qua
-- dim_hotel: SCD2 cho mỗi lần đổi giá 1 hotel_key, lọc 1 hotel_key sẽ bỏ sót booking của các phiên bản khác.
EXPLAIN ANALYZE
SELECT h.hotel_id, sum(f.nights) AS room_nights, sum(f.amount) AS revenue
FROM gold.fact_bookings f JOIN gold.dim_hotel h USING (hotel_key)
WHERE h.hotel_id = 1024 AND f.checkin_date BETWEEN '2025-03-01' AND '2025-03-31' AND f.status = 'confirmed'
GROUP BY h.hotel_id;

-- B-tree composite index: cột lọc bằng (=) đặt trước, cột lọc khoảng đặt sau
CREATE INDEX IF NOT EXISTS idx_fact_bookings_hotel_checkin
    ON gold.fact_bookings (hotel_key, checkin_date);

-- Index hotel_key -> hotel_id của dim (join ở query trên); partial unique index dòng hiện hành đã có ở gold_schema.sql
CREATE INDEX IF NOT EXISTS idx_dim_hotel_id ON gold.dim_hotel (hotel_id, hotel_key);

ANALYZE gold.fact_bookings;
