-- DP2: staging (spark_jobs/stage_gold.py) -> dim_customer, dim_hotel (SCD2), fact_bookings. 1 transaction: lỗi giữa chừng
-- không để fact trỏ tới phiên bản dim chưa có. Chạy lại cùng ngày không đổi gì (upsert theo khoá tự nhiên).
BEGIN;

INSERT INTO gold.dim_customer (customer_id, home_city, loyalty_tier)
SELECT customer_id, home_city, loyalty_tier FROM gold.stg_customers
ON CONFLICT (customer_id) DO UPDATE SET home_city = EXCLUDED.home_city, loyalty_tier = EXCLUDED.loyalty_tier;

-- Cập nhật SCD2 từ gold.stg_hotel_changes (change feed: mỗi dòng là 1 lần đổi thật, có thể nhiều lần / khách sạn).
-- Chạy lại cùng batch không đổi gì: chỉ áp các thay đổi mới hơn phiên bản mới nhất đã có của khách sạn đó.
CREATE TEMP TABLE new_versions ON COMMIT DROP AS
SELECT s.hotel_id, s.city, s.stars, s.price, s.valid_from,
       LEAD(s.valid_from, 1, TIMESTAMP '9999-12-31') OVER (PARTITION BY s.hotel_id ORDER BY s.valid_from) AS valid_to
FROM (SELECT DISTINCT ON (hotel_id, valid_from) * FROM gold.stg_hotel_changes ORDER BY hotel_id, valid_from) s
WHERE s.valid_from > COALESCE((SELECT max(d.valid_from_ts) FROM gold.dim_hotel d WHERE d.hotel_id = s.hotel_id),
                              TIMESTAMP '-infinity');

-- Bước 1: đóng phiên bản hiện hành tại lần đổi sớm nhất của batch
UPDATE gold.dim_hotel d
SET valid_to_ts = n.first_from, is_current = FALSE
FROM (SELECT hotel_id, min(valid_from) AS first_from FROM new_versions GROUP BY hotel_id) n
WHERE d.hotel_id = n.hotel_id AND d.is_current;

-- Bước 2: chèn mọi phiên bản của batch, nối liền nhau bằng LEAD; chỉ bản cuối là hiện hành
INSERT INTO gold.dim_hotel (hotel_id, city, stars, price, valid_from_ts, valid_to_ts, is_current)
SELECT hotel_id, city, stars, price, valid_from, valid_to, valid_to = TIMESTAMP '9999-12-31'
FROM new_versions;

-- Fact: hotel_key = phiên bản dim_hotel có hiệu lực lúc đặt (join khoảng). Booking cũ bị huỷ hôm nay chỉ cập nhật status.
-- lead_days lấy phần ngày nguyên của checkin - created_at, giống generator/profile_data.
INSERT INTO gold.fact_bookings (booking_id, hotel_key, customer_key, booking_date, checkin_date, lead_days, nights,
                                amount, cancellation_policy, channel, status, cancelled_at)
SELECT b.booking_id, h.hotel_key, c.customer_key, b.created_at::date, b.checkin::date,
       GREATEST(EXTRACT(DAY FROM b.checkin - b.created_at)::int, 0), b.nights, b.price * b.nights,
       b.cancellation_policy, b.channel, b.status, b.cancelled_at
FROM gold.stg_bookings b
JOIN gold.dim_customer c USING (customer_id)
JOIN gold.dim_hotel h ON h.hotel_id = b.hotel_id AND b.created_at >= h.valid_from_ts AND b.created_at < h.valid_to_ts
ON CONFLICT (booking_id) DO UPDATE SET status = EXCLUDED.status, cancelled_at = EXCLUDED.cancelled_at;

COMMIT;
