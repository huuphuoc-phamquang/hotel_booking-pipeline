"""Check SQL của bước validate DP2 / DP3 (không import Airflow để tests/test_gold_sql.py chạy được trên Postgres thật).
Mỗi check trả về đúng 1 boolean; {ds} thay bằng ngày logic của run. *_BY_TABLE: kết quả gắn vào đúng bảng trên DataHub."""
GOLD_CHECKS = {
    "fact_has_rows_for_ds": "SELECT count(*) > 0 FROM gold.fact_bookings WHERE booking_date = '{ds}'",
    # booking staging mà không vào được fact = thiếu dim (khách hoặc phiên bản khách sạn) -> mất dữ liệu
    "staging_all_loaded": "SELECT NOT EXISTS (SELECT 1 FROM gold.stg_bookings s "
                          "LEFT JOIN gold.fact_bookings f USING (booking_id) WHERE f.booking_id IS NULL)",
    "amount_positive": "SELECT coalesce(bool_and(amount > 0), true) FROM gold.fact_bookings WHERE booking_date = '{ds}'",
    "one_current_version_per_hotel": "SELECT NOT EXISTS (SELECT hotel_id FROM gold.dim_hotel GROUP BY hotel_id "
                                     "HAVING count(*) FILTER (WHERE is_current) <> 1)",
    "cancel_after_create": "SELECT coalesce(bool_and(cancelled_at IS NULL OR cancelled_at::date >= booking_date), true) "
                           "FROM gold.fact_bookings WHERE booking_date = '{ds}'",
}

FEATURE_CHECKS = {
    "customer_rows_for_ds": "SELECT count(*) > 0 FROM gold.feat_customer_booking_stats "
                            "WHERE event_timestamp = DATE '{ds}' + 1",
    "hotel_rows_for_ds": "SELECT count(*) > 0 FROM gold.feat_hotel_demand WHERE event_timestamp = DATE '{ds}' + 1",
    "customer_rate_in_0_1": "SELECT coalesce(bool_and(cancel_rate_90d BETWEEN 0 AND 1), true) "
                            "FROM gold.feat_customer_booking_stats WHERE event_timestamp = DATE '{ds}' + 1",
    "hotel_rate_in_0_1": "SELECT coalesce(bool_and(cancel_rate_30d BETWEEN 0 AND 1), true) "
                         "FROM gold.feat_hotel_demand WHERE event_timestamp = DATE '{ds}' + 1",
    # backfill ghi event_timestamp quá khứ, created = lúc chạy: created < event_timestamp nghĩa là dữ liệu tương lai
    "event_before_created": "SELECT coalesce(bool_and(event_timestamp <= created), true) FROM gold.feat_hotel_demand "
                            "WHERE event_timestamp = DATE '{ds}' + 1",
}

G = "postgres:warehouse.gold."
DIM_HOTEL_CHECKS = ("one_current_version_per_hotel",)       # kiểm SCD2 của dim_hotel, không phải fact
GOLD_CHECKS_BY_TABLE = {
    G + "fact_bookings": {k: v for k, v in GOLD_CHECKS.items() if k not in DIM_HOTEL_CHECKS},
    G + "dim_hotel": {k: GOLD_CHECKS[k] for k in DIM_HOTEL_CHECKS},
}
FEATURE_CHECKS_BY_TABLE = {
    G + "feat_customer_booking_stats": {k: v for k, v in FEATURE_CHECKS.items() if k.startswith("customer")},
    G + "feat_hotel_demand": {k: v for k, v in FEATURE_CHECKS.items() if not k.startswith("customer")},
}
