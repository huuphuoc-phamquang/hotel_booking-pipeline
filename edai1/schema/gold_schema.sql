-- Schema Gold (PostgreSQL) cho booking app.
-- Rubric edai-1 › Documentation › Schema design:
--   - Visualize tables on all zones  : export ERD bằng DBeaver từ bronze/silver/gold
--   - Dim table with SCD 2           : dim_hotel có valid_from_ts, valid_to_ts, is_current (giá, hạng sao đổi theo thời gian)
--   - Feature tables (feat_)         : có 2 cột event_timestamp và created
--   - Relationship dim & fact        : FOREIGN KEY fact_bookings -> dim_hotel/dim_customer
--   - Naming convention              : bronze raw_*, silver stg_*, gold dim_/fact_/obt_/feat_
-- Proof: docs/SchemaDesign.md chụp ERD + bảng mô tả nhiệm vụ của từng bảng.

CREATE SCHEMA IF NOT EXISTS gold;

-- Dimension SCD Type 2: mỗi lần khách sạn đổi giá/hạng sao -> đóng dòng cũ, mở dòng mới
CREATE TABLE gold.dim_hotel (
    hotel_key      BIGSERIAL PRIMARY KEY,          -- surrogate key, mỗi phiên bản 1 key
    hotel_id       BIGINT        NOT NULL,         -- natural key từ hệ thống nguồn
    city           TEXT,
    stars          SMALLINT,
    price          NUMERIC(12, 0),                 -- giá niêm yết VND/đêm của phiên bản này
    valid_from_ts  TIMESTAMP     NOT NULL,
    valid_to_ts    TIMESTAMP     NOT NULL DEFAULT '9999-12-31',
    is_current     BOOLEAN       NOT NULL DEFAULT TRUE
);

CREATE TABLE gold.dim_customer (
    customer_key  BIGSERIAL PRIMARY KEY,
    customer_id   BIGINT NOT NULL UNIQUE,
    home_city     TEXT,
    loyalty_tier  SMALLINT
);

-- Fact: grain = 1 dòng / booking đã dedup, trỏ tới phiên bản dim_hotel đúng tại created_at
CREATE TABLE gold.fact_bookings (
    booking_id     BIGINT PRIMARY KEY,
    hotel_key      BIGINT NOT NULL REFERENCES gold.dim_hotel (hotel_key),
    customer_key   BIGINT NOT NULL REFERENCES gold.dim_customer (customer_key),
    booking_date   DATE   NOT NULL,
    checkin_date   DATE   NOT NULL,
    lead_days      INT,
    nights         INT,
    amount         NUMERIC(14, 0),
    cancellation_policy TEXT   NOT NULL,          -- flexible / non_refundable
    channel        TEXT,                           -- NULL với booking trước schema v2
    status        TEXT   NOT NULL,                -- confirmed / cancelled tại thời điểm chụp landing (không phải kết cục cuối)
    cancelled_at  TIMESTAMP                       -- NULL nếu chưa huỷ tới lúc chụp; dùng cho feature point-in-time
);

-- Feature table: event_timestamp = thời điểm feature có hiệu lực (Feast dùng cho point-in-time join),
-- created = thời điểm dòng được ghi (Feast dùng để chọn bản mới nhất khi trùng event_timestamp)
CREATE TABLE gold.feat_customer_booking_stats (
    customer_id        BIGINT    NOT NULL,
    bookings_90d       INT,
    cancel_rate_90d    NUMERIC(5, 4),
    avg_lead_days_90d  NUMERIC(6, 1),
    event_timestamp    TIMESTAMP NOT NULL,
    created            TIMESTAMP NOT NULL DEFAULT now(),
    PRIMARY KEY (customer_id, event_timestamp)
);

CREATE TABLE gold.feat_hotel_demand (
    hotel_id          BIGINT    NOT NULL,
    bookings_7d       INT,
    cancel_rate_30d   NUMERIC(5, 4),
    event_timestamp   TIMESTAMP NOT NULL,
    created           TIMESTAMP NOT NULL DEFAULT now(),
    PRIMARY KEY (hotel_id, event_timestamp)
);

-- Feature real-time: Flink booking_events_window upsert theo (hotel_id, event_timestamp = cuối cửa sổ 1 giờ)
CREATE TABLE gold.feat_hotel_realtime (
    hotel_id          BIGINT    NOT NULL,
    bookings_1h       INT       NOT NULL,
    event_timestamp   TIMESTAMP NOT NULL,
    created           TIMESTAMP NOT NULL DEFAULT now(),
    PRIMARY KEY (hotel_id, event_timestamp)
);

-- Đối soát stream (Flink nhánh tumbling 1 phút): số booking từng phút + event rơi ra side output.
-- Mỗi giờ: sum(bookings) + count(late) = số booking (dedup idempotency_key) có created_at trong giờ đó ở Silver.
CREATE TABLE gold.stream_bookings_1m (
    hotel_id    BIGINT    NOT NULL,
    bookings    INT       NOT NULL,
    window_end  TIMESTAMP NOT NULL,
    PRIMARY KEY (hotel_id, window_end)
);

CREATE TABLE gold.stream_late_bookings (
    event_id    BIGINT    PRIMARY KEY,
    hotel_id    BIGINT    NOT NULL,
    event_time  TIMESTAMP NOT NULL,
    logged_at   TIMESTAMP NOT NULL DEFAULT now()
);

-- Xác suất huỷ do DAG score_bookings chấm qua booking-mcp (Feast online + KServe) một lần, ngay sau ngày tạo booking (1 dòng / booking):
-- propose_overbooking cộng các booking còn giữ phòng theo hotel × stay_date; drift_monitor so dự báo với thực tế.
CREATE TABLE gold.booking_risk (
    booking_id   BIGINT        NOT NULL,
    hotel_id     BIGINT        NOT NULL,
    stay_date    DATE          NOT NULL,          -- ngày nhận phòng
    probability  NUMERIC(5, 4) NOT NULL,
    scored_date  DATE          NOT NULL,          -- as_of của run materialize, không phải giờ máy (backfill đúng ngày)
    model_version TEXT,                           -- version MLflow của revision KServe đã chấm (calibration theo bản, A/B)
    PRIMARY KEY (booking_id, scored_date)
);
CREATE INDEX booking_risk_hotel_stay ON gold.booking_risk (hotel_id, stay_date, scored_date);
CREATE INDEX booking_risk_stay ON gold.booking_risk (stay_date);   -- drift_monitor: calibration 7 ngày nhận phòng

-- Số phòng mở bán theo hotel × đêm (stage_gold.py tổng inventory các loại phòng của 30 đêm tới vào stg_hotel_rooms,
-- dp2_upsert_gold.sql upsert vào đây trong 1 transaction): propose_overbooking so số booking đang giữ với rooms + K.
-- Upsert dồn theo ngày nên đêm đã qua vẫn còn, chạy lại ngày cũ không xoá số phòng của các đêm khác.
CREATE TABLE gold.hotel_rooms (
    hotel_id   BIGINT NOT NULL,
    stay_date  DATE   NOT NULL,
    rooms      INT    NOT NULL,
    PRIMARY KEY (hotel_id, stay_date)
);

-- Số phòng bán vượt đã duyệt (tool apply_overbooking, qua requireApproval của kagent)
CREATE TABLE gold.overbooking_limits (
    hotel_id     BIGINT    NOT NULL,
    stay_date    DATE      NOT NULL,
    k            INT       NOT NULL CHECK (k >= 0),
    approved_at  TIMESTAMP NOT NULL DEFAULT now(),
    PRIMARY KEY (hotel_id, stay_date)
);

-- Nhãn huấn luyện dạng 2 cột: huỷ trước ngày nhận phòng. Chỉ dùng cho booking đã qua checkin (kết cục đã chốt).
CREATE VIEW gold.labels_cancel AS
SELECT booking_id, (cancelled_at IS NOT NULL AND cancelled_at <= checkin_date)::int AS is_cancelled
FROM gold.fact_bookings;

-- Mỗi khách sạn đúng 1 phiên bản hiện hành: SCD2 chạy sai sẽ fail ở đây thay vì âm thầm sinh 2 dòng is_current
CREATE UNIQUE INDEX dim_hotel_one_current ON gold.dim_hotel (hotel_id) WHERE is_current;

-- Staging trên Postgres: Postgres không đọc được bảng Iceberg ở Silver, nên job Spark của DP2 ghi các thay đổi
-- giá (landing hotel_changes) vào đây qua JDBC trước khi sql/dp2_upsert_gold.sql chạy SCD2.
CREATE TABLE gold.stg_hotel_changes (
    hotel_id    BIGINT    NOT NULL,
    city        TEXT,
    stars       SMALLINT,
    price       NUMERIC(12, 0),
    valid_from  TIMESTAMP NOT NULL
);

-- Staging của DP2 (spark_jobs/stage_gold.py, ghi đè mỗi lần chạy): booking tạo/huỷ trong ngày ds và khách của chúng
CREATE TABLE gold.stg_bookings (
    booking_id           BIGINT    NOT NULL,
    customer_id          BIGINT    NOT NULL,
    hotel_id             BIGINT    NOT NULL,
    created_at           TIMESTAMP NOT NULL,
    checkin              TIMESTAMP NOT NULL,
    nights               INT,
    price                NUMERIC(12, 0),           -- giá / đêm
    cancellation_policy  TEXT      NOT NULL,
    channel              TEXT,
    status               TEXT      NOT NULL,
    cancelled_at         TIMESTAMP
);

CREATE TABLE gold.stg_customers (
    customer_id   BIGINT NOT NULL,
    home_city     TEXT,
    loyalty_tier  SMALLINT
);

CREATE TABLE gold.stg_hotel_rooms (
    hotel_id   BIGINT NOT NULL,
    stay_date  DATE   NOT NULL,
    rooms      INT    NOT NULL
);

-- Index cho các truy vấn thật: DP3 quét fact theo khách / khách sạn trong cửa sổ ngày, score_bookings lọc theo checkin;
-- DP3, score_bookings, validate_gold lọc booking_date của 1 ngày, DP3 tìm lần huỷ trong ngày theo cancelled_at.
-- shortcut: fact 1 năm ~140 triệu dòng chưa partition theo booking_date; cần PARTITION BY RANGE khi dữ liệu nhiều năm.
-- feat_* đã có PK (entity, event_timestamp) = đúng thứ tự Feast point-in-time join cần.
CREATE INDEX fact_bookings_customer_date ON gold.fact_bookings (customer_key, booking_date);
CREATE INDEX fact_bookings_hotel_date ON gold.fact_bookings (hotel_key, booking_date);
CREATE INDEX fact_bookings_checkin ON gold.fact_bookings (checkin_date);
CREATE INDEX fact_bookings_date ON gold.fact_bookings (booking_date);
CREATE INDEX fact_bookings_cancelled ON gold.fact_bookings (cancelled_at) WHERE cancelled_at IS NOT NULL;
