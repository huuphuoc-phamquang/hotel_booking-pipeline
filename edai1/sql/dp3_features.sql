-- DP3: feature offline cho ngày ds (Jinja của Airflow thay {{ ds }}), ghi thẳng vào gold.feat_* trên PostgreSQL.
-- event_timestamp = hết ngày ds (ds + 1 ngày, 00:00): feature chỉ dùng dữ liệu tới hết ngày ds, và training join tại
-- booking_date 00:00 nên chỉ thấy snapshot của các ngày trước -> không rò dữ liệu trong ngày. Không dùng giờ máy nên
-- backfill sinh đúng lịch sử point-in-time. Chạy lại cùng ds ghi đè (ON CONFLICT), created = now() để Feast chọn bản mới.
-- Huỷ chỉ tính khi cancelled_at <= hết ngày ds: fact có thể đã biết lần huỷ tương lai khi backfill. coalesce: NULL < ngày
-- là NULL, avg bỏ qua NULL nên thiếu coalesce thì tỉ lệ huỷ luôn ra 1.
BEGIN;

-- Khách: chỉ ghi dòng cho khách có hoạt động (đặt hoặc huỷ) trong ngày ds; TTL 90 ngày của Feast lo phần còn lại.
INSERT INTO gold.feat_customer_booking_stats (customer_id, bookings_90d, cancel_rate_90d, avg_lead_days_90d,
                                              event_timestamp, created)
SELECT c.customer_id,
       count(*),
       avg(coalesce(f.cancelled_at < DATE '{{ ds }}' + 1, false)::int),
       avg(f.lead_days),
       DATE '{{ ds }}' + 1, now()
FROM gold.fact_bookings f
JOIN gold.dim_customer c USING (customer_key)
WHERE f.booking_date > DATE '{{ ds }}' - 90 AND f.booking_date <= DATE '{{ ds }}'
  AND f.customer_key IN (SELECT customer_key FROM gold.fact_bookings
                         WHERE booking_date = DATE '{{ ds }}'
                            OR (cancelled_at >= DATE '{{ ds }}' AND cancelled_at < DATE '{{ ds }}' + 1))
GROUP BY c.customer_id
ON CONFLICT (customer_id, event_timestamp) DO UPDATE
SET bookings_90d = EXCLUDED.bookings_90d, cancel_rate_90d = EXCLUDED.cancel_rate_90d,
    avg_lead_days_90d = EXCLUDED.avg_lead_days_90d, created = EXCLUDED.created;

-- Khách sạn: snapshot hằng ngày cho mọi khách sạn có booking trong 30 ngày (TTL 2 ngày).
INSERT INTO gold.feat_hotel_demand (hotel_id, bookings_7d, cancel_rate_30d, event_timestamp, created)
SELECT h.hotel_id,
       count(*) FILTER (WHERE f.booking_date > DATE '{{ ds }}' - 7),
       avg(coalesce(f.cancelled_at < DATE '{{ ds }}' + 1, false)::int),
       DATE '{{ ds }}' + 1, now()
FROM gold.fact_bookings f
JOIN gold.dim_hotel h USING (hotel_key)
WHERE f.booking_date > DATE '{{ ds }}' - 30 AND f.booking_date <= DATE '{{ ds }}'
GROUP BY h.hotel_id
ON CONFLICT (hotel_id, event_timestamp) DO UPDATE
SET bookings_7d = EXCLUDED.bookings_7d, cancel_rate_30d = EXCLUDED.cancel_rate_30d, created = EXCLUDED.created;

COMMIT;
