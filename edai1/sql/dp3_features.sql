-- DP3: feature offline cho ngày ds (Jinja của Airflow thay {{ ds }}), ghi thẳng vào gold.feat_* trên PostgreSQL.
-- event_timestamp = hết ngày ds (ds + 1 ngày, 00:00): feature chỉ dùng dữ liệu tới hết ngày ds. score_bookings chấm
-- booking ngày ds sau khi materialize snapshot này, nên training cũng join tại booking_date + 1 (cùng snapshot, gồm
-- chính booking đó ở trạng thái chưa huỷ). Không dùng giờ máy nên backfill sinh đúng lịch sử point-in-time.
-- Chạy lại cùng ds ghi đè (ON CONFLICT), created = now() để Feast chọn bản mới.
-- Huỷ chỉ tính khi cancelled_at <= hết ngày ds: fact có thể đã biết lần huỷ tương lai khi backfill. coalesce: NULL < ngày
-- là NULL, avg bỏ qua NULL nên thiếu coalesce thì tỉ lệ huỷ luôn ra 1.
BEGIN;

-- Khách: ghi dòng cho mọi khách mà feature đổi trong ngày ds: có booking mới, có booking rơi khỏi cửa sổ 90 ngày
-- (booking_date = ds - 90), hoặc có lần huỷ. Khách không có thay đổi giữ snapshot cũ (vẫn đúng) tới khi TTL 90 ngày hết.
-- Cửa sổ rỗng vẫn ghi dòng (bookings_90d = 0) thay vì để snapshot cũ còn đếm booking đã quá 90 ngày.
INSERT INTO gold.feat_customer_booking_stats (customer_id, bookings_90d, cancel_rate_90d, avg_lead_days_90d,
                                              event_timestamp, created)
SELECT c.customer_id,
       count(f.booking_id),
       avg(coalesce(f.cancelled_at < DATE '{{ ds }}' + 1, false)::int) FILTER (WHERE f.booking_id IS NOT NULL),
       avg(f.lead_days),
       DATE '{{ ds }}' + 1, now()
FROM (SELECT DISTINCT customer_key FROM gold.fact_bookings
      WHERE booking_date = DATE '{{ ds }}' OR booking_date = DATE '{{ ds }}' - 90
         OR (cancelled_at >= DATE '{{ ds }}' AND cancelled_at < DATE '{{ ds }}' + 1)) a
JOIN gold.dim_customer c USING (customer_key)
LEFT JOIN gold.fact_bookings f
       ON f.customer_key = a.customer_key AND f.booking_date > DATE '{{ ds }}' - 90 AND f.booking_date <= DATE '{{ ds }}'
GROUP BY c.customer_id
ON CONFLICT (customer_id, event_timestamp) DO UPDATE
SET bookings_90d = EXCLUDED.bookings_90d, cancel_rate_90d = EXCLUDED.cancel_rate_90d,
    avg_lead_days_90d = EXCLUDED.avg_lead_days_90d, created = EXCLUDED.created;

-- Khách sạn: snapshot hằng ngày (TTL 2 ngày) cho mọi khách sạn có booking trong 31 ngày: thêm 1 ngày để khách sạn có
-- booking vừa rơi khỏi cửa sổ 30 ngày nhận dòng bookings_7d = 0, cancel_rate_30d NULL thay vì giữ snapshot cũ.
INSERT INTO gold.feat_hotel_demand (hotel_id, bookings_7d, cancel_rate_30d, event_timestamp, created)
SELECT h.hotel_id,
       count(*) FILTER (WHERE f.booking_date > DATE '{{ ds }}' - 7),
       avg(coalesce(f.cancelled_at < DATE '{{ ds }}' + 1, false)::int) FILTER (WHERE f.booking_date > DATE '{{ ds }}' - 30),
       DATE '{{ ds }}' + 1, now()
FROM gold.fact_bookings f
JOIN gold.dim_hotel h USING (hotel_key)
WHERE f.booking_date > DATE '{{ ds }}' - 31 AND f.booking_date <= DATE '{{ ds }}'
GROUP BY h.hotel_id
ON CONFLICT (hotel_id, event_timestamp) DO UPDATE
SET bookings_7d = EXCLUDED.bookings_7d, cancel_rate_30d = EXCLUDED.cancel_rate_30d, created = EXCLUDED.created;

COMMIT;
