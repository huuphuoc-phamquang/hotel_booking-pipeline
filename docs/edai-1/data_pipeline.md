# Data pipeline orchestration

Ba pipeline DP1–DP3 chạy trên Airflow, mỗi pipeline gồm bước ingest và bước validate.

Mỗi mục dưới đây ứng với một dòng của rubric. Phần **Cách làm** mô tả giải pháp đã triển khai, đồng bộ từ
cột F của rubric. Phần **Kết quả** ghi test đã chạy, số liệu đo được hoặc ảnh chụp (`docs/images/`).

<a id="edai-1-22"></a>
## Ingest stage · Pipeline to ingest raw data into bronze zone (DP1)

**Rubric:** edai-1 · dòng 22 · 2 điểm · nhóm *Data Pipeline Orchestration* › *Pipeline to ingest raw data into bronze zone (DP1)*

**Cần nộp (cả nhóm):** Document show hình ảnh 3 pipelines trên Airflow, giải thích từng pipeline làm gì, từng component trong pipeline làm gì

**Cách làm:** [Đã có] DAG `dp1_ingest_bronze` (`check_landing` → ingest → validate) và `dp1_load_dims`. Connection, Variable đặt trong Airflow; image Spark lấy từ Variable `spark_image`. Backfill bằng `airflow dags backfill`; `catchup=False` để DAG không tự chạy 600 ngày khi bật. `tests/test_dag_integrity.py` kiểm cấu trúc DAG trong image `apache/airflow:2.10.5`.

**Kết quả:** các test `tests/test_dag_integrity.py` chạy cục bộ và đạt (2026-11-16). Chưa có ảnh chụp trên cluster.

<a id="edai-1-23"></a>
## Validate stage · Pipeline to ingest raw data into bronze zone (DP1)

**Rubric:** edai-1 · dòng 23 · 2 điểm · nhóm *Data Pipeline Orchestration* › *Pipeline to ingest raw data into bronze zone (DP1)*

**Cách làm:** [Đã có] `validate_bronze` dùng Great Expectations 1.x (`governance/bronze_checks.py`, context ephemeral, chỉ đọc các cột cần kiểm). `tests/test_bronze_checks.py` cho thấy landing của generator qua hết các kiểm tra, còn lỗi cài vào (giá âm, `quote_id` trùng, partition rỗng) đều bị bắt. [Cần làm] chụp kết quả trên Airflow.

**Kết quả:** các test `edai1/tests/test_bronze_checks.py` chạy cục bộ và đạt (2026-11-16). Chưa có ảnh chụp trên cluster.

<a id="edai-1-24"></a>
## Ingest stage · Pipeline to ingest data from bronze zone into silver and gol

**Rubric:** edai-1 · dòng 24 · 2 điểm · nhóm *Data Pipeline Orchestration* › *Pipeline to ingest data from bronze zone into silver and gold zone (or bronze -> gold only) (DP2)*

**Cách làm:** [Đã có] DAG `dp2_bronze_to_gold` đợi DP1 cùng ngày (`ExternalTaskSensor`), chạy `silver_bookings` (Spark, `incr` theo `dt=ds`), `stage_gold` (Spark ghi staging và `gold.hotel_rooms`), rồi `upsert_gold`. Bước cuối dùng `sql/dp2_upsert_gold.sql` trong một transaction: `dim_customer`, `dim_hotel` SCD2 và `fact_bookings` join theo khoảng hiệu lực của phiên bản dim. [Cần làm] thêm `fact_quotes`; chụp graph và lần chạy.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-1-25"></a>
## Validate stage · Pipeline to ingest data from bronze zone into silver and gol

**Rubric:** edai-1 · dòng 25 · 2 điểm · nhóm *Data Pipeline Orchestration* › *Pipeline to ingest data from bronze zone into silver and gold zone (or bronze -> gold only) (DP2)*

**Cách làm:** [Đã có] `validate_gold` gồm 5 kiểm tra SQL (`dags/gold_checks.py`), chạy trên Postgres thật trong `tests/test_gold_sql.py`; mỗi kiểm tra đẩy `AssertionRunEvent` lên DataHub. Gold dùng SQL thay cho Great Expectations vì dữ liệu đã nằm sẵn trong PostgreSQL. [Cần làm] chụp tab Validation.

**Kết quả:** các test `edai1/tests/test_gold_sql.py` chạy cục bộ và đạt (2026-11-16). Chưa có ảnh chụp trên cluster.

<a id="edai-1-26"></a>
## Ingest stage · Pipeline to compute offline feature table (DP3)

**Rubric:** edai-1 · dòng 26 · 2 điểm · nhóm *Data Pipeline Orchestration* › *Pipeline to compute offline feature table (DP3) (Ví dụ: f_customer_total_orders_90d)*

**Cách làm:** [Đã có] DAG `dp3_offline_features` chạy `sql/dp3_features.sql`, ghi `feat_customer_booking_stats` và `feat_hotel_demand` trực tiếp trên Gold (upsert trong một transaction). `event_timestamp` là cuối ngày `ds` chứ không phải giờ máy, nhờ đó backfill sinh đủ lịch sử point-in-time cho training. Task validate phát Airflow Dataset để kích hoạt materialize. [Cần làm] chụp graph và lần chạy.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-1-27"></a>
## Validate stage · Pipeline to compute offline feature table (DP3)

**Rubric:** edai-1 · dòng 27 · 2 điểm · nhóm *Data Pipeline Orchestration* › *Pipeline to compute offline feature table (DP3) (Ví dụ: f_customer_total_orders_90d)*

**Cách làm:** [Đã có] `validate_features` kiểm có dòng cho ngày `ds`, tỉ lệ nằm trong [0, 1] và `event_timestamp` ≤ `created` (`dags/gold_checks.py`, chạy thật trong `tests/test_gold_sql.py`). [Cần làm] chụp tab Validation.

**Kết quả:** các test `edai1/tests/test_gold_sql.py` chạy cục bộ và đạt (2026-11-16). Chưa có ảnh chụp trên cluster.
