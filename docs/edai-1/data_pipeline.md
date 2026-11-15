# Data pipeline orchestration

DP1–DP3 trên Airflow: ingest và validate.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-1-22"></a>
## Ingest stage · Pipeline to ingest raw data into bronze zone (DP1)

**Rubric:** edai-1 · dòng 22 · 2 điểm · nhóm *Data Pipeline Orchestration* › *Pipeline to ingest raw data into bronze zone (DP1)*

**Cần nộp (cả nhóm):** Document show hình ảnh 3 pipelines trên Airflow, giải thích từng pipeline làm gì, từng component trong pipeline làm gì

**Cách làm:** [Đã có] dp1_ingest_bronze (check_landing -> ingest -> validate) + dp1_load_dims; Connection/Variable trong Airflow; image Spark qua Variable spark_image. Backfill bằng airflow dags backfill (catchup=False để không tự chạy 600 ngày khi bật DAG). tests/test_dag_integrity.py kiểm cấu trúc trong image apache/airflow:2.10.5.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-23"></a>
## Validate stage · Pipeline to ingest raw data into bronze zone (DP1)

**Rubric:** edai-1 · dòng 23 · 2 điểm · nhóm *Data Pipeline Orchestration* › *Pipeline to ingest raw data into bronze zone (DP1)*

**Cách làm:** [Đã có] validate_bronze dùng Great Expectations 1.x (governance/bronze_checks.py, context ephemeral, chỉ đọc cột cần kiểm); tests/test_bronze_checks.py: landing generator qua hết, lỗi cài vào (giá âm, quote_id trùng, partition rỗng) bị fail. [Cần làm] chụp kết quả trên Airflow.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-24"></a>
## Ingest stage · Pipeline to ingest data from bronze zone into silver and gol

**Rubric:** edai-1 · dòng 24 · 2 điểm · nhóm *Data Pipeline Orchestration* › *Pipeline to ingest data from bronze zone into silver and gold zone (or bronze -> gold only) (DP2)*

**Cách làm:** [Đã có] DAG dp2_bronze_to_gold: đợi DP1 cùng ngày (ExternalTaskSensor) -> silver_bookings (Spark) -> stage_gold (Spark -> staging) -> upsert_gold (sql/dp2_upsert_gold.sql, 1 transaction: dim_customer, dim_hotel SCD2, fact_bookings join khoảng theo phiên bản dim). [Cần làm] fact_quotes; chụp graph + run.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-25"></a>
## Validate stage · Pipeline to ingest data from bronze zone into silver and gol

**Rubric:** edai-1 · dòng 25 · 2 điểm · nhóm *Data Pipeline Orchestration* › *Pipeline to ingest data from bronze zone into silver and gold zone (or bronze -> gold only) (DP2)*

**Cách làm:** [Đã có] validate_gold: 5 check SQL (dags/gold_checks.py) chạy trên Postgres thật trong tests/test_gold_sql.py; mỗi check đẩy AssertionRunEvent lên DataHub. Dùng SQL thay GX cho Gold vì dữ liệu nằm sẵn trong PostgreSQL. [Cần làm] chụp tab Validation.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-26"></a>
## Ingest stage · Pipeline to compute offline feature table (DP3)

**Rubric:** edai-1 · dòng 26 · 2 điểm · nhóm *Data Pipeline Orchestration* › *Pipeline to compute offline feature table (DP3) (Ví dụ: f_customer_total_orders_90d)*

**Cách làm:** [Đã có] DAG dp3_offline_features: sql/dp3_features.sql ghi feat_customer_booking_stats, feat_hotel_demand thẳng trên Gold (upsert, 1 transaction); event_timestamp = hết ngày ds, không phải giờ máy, nên backfill sinh đủ lịch sử point-in-time cho training; task validate bắn Airflow Dataset kích hoạt materialize. [Cần làm] chụp graph + run.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-27"></a>
## Validate stage · Pipeline to compute offline feature table (DP3)

**Rubric:** edai-1 · dòng 27 · 2 điểm · nhóm *Data Pipeline Orchestration* › *Pipeline to compute offline feature table (DP3) (Ví dụ: f_customer_total_orders_90d)*

**Cách làm:** [Đã có] validate_features: có dòng cho ngày ds, tỉ lệ trong [0, 1], event_timestamp <= created (dags/gold_checks.py, chạy thật trong tests/test_gold_sql.py). [Cần làm] chụp tab Validation.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
