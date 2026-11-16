"""Check SQL của bước validate DP2 / DP3 (không import Airflow để tests/test_gold_sql.py chạy được trên Postgres thật).
Mỗi check trả về đúng 1 boolean; {ds} thay bằng ngày logic của run."""
GOLD_CHECKS = {
    "fact_has_rows_for_ds": "SELECT count(*) > 0 FROM gold.fact_bookings WHERE booking_date = '{ds}'",
    # booking staging mà không vào được fact = thiếu dim (khách hoặc phiên bản khách sạn) -> mất dữ liệu
    "staging_all_loaded": "SELECT NOT EXISTS (SELECT 1 FROM gold.stg_bookings s "
                          "LEFT JOIN gold.fact_bookings f USING (booking_id) WHERE f.booking_id IS NULL)",
    "amount_positive": "SELECT bool_and(amount > 0) FROM gold.fact_bookings WHERE booking_date = '{ds}'",
    "one_current_version_per_hotel": "SELECT NOT EXISTS (SELECT hotel_id FROM gold.dim_hotel GROUP BY hotel_id "
                                     "HAVING count(*) FILTER (WHERE is_current) <> 1)",
    "cancel_after_create": "SELECT bool_and(cancelled_at IS NULL OR cancelled_at::date >= booking_date) "
                           "FROM gold.fact_bookings WHERE booking_date = '{ds}'",
}

FEATURE_CHECKS = {
    "customer_rows_for_ds": "SELECT count(*) > 0 FROM gold.feat_customer_booking_stats "
                            "WHERE event_timestamp = DATE '{ds}' + 1",
    "hotel_rows_for_ds": "SELECT count(*) > 0 FROM gold.feat_hotel_demand WHERE event_timestamp = DATE '{ds}' + 1",
    "rates_in_0_1": "SELECT bool_and(cancel_rate_90d BETWEEN 0 AND 1) AND (SELECT bool_and(cancel_rate_30d BETWEEN 0 AND 1) "
                    "FROM gold.feat_hotel_demand WHERE event_timestamp = DATE '{ds}' + 1) "
                    "FROM gold.feat_customer_booking_stats WHERE event_timestamp = DATE '{ds}' + 1",
    # backfill ghi event_timestamp quá khứ, created = lúc chạy: created < event_timestamp nghĩa là dữ liệu tương lai
    "event_before_created": "SELECT bool_and(event_timestamp <= created) FROM gold.feat_hotel_demand "
                            "WHERE event_timestamp = DATE '{ds}' + 1",
}
