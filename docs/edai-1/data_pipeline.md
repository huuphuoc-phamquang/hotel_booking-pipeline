# Data pipeline orchestration

DP1–DP3 trên Airflow: ingest và validate.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-1-22"></a>
## Ingest stage · Pipeline to ingest raw data into bronze zone (DP1)

**Rubric:** edai-1 · dòng 22 · 2 điểm · nhóm *Data Pipeline Orchestration* › *Pipeline to ingest raw data into bronze zone (DP1)*

**Cần nộp (cả nhóm):** Document show hình ảnh 3 pipelines trên Airflow, giải thích từng pipeline làm gì, từng component trong pipeline làm gì

**Cách làm:** [Đã có] dp1_ingest_bronze (check_landing -> ingest), Connection/Variable để trong Airflow. [Cần sửa] catchup=False làm DAG không nạp 2025 -> bật catchup hoặc backfill.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-23"></a>
## Validate stage · Pipeline to ingest raw data into bronze zone (DP1)

**Rubric:** edai-1 · dòng 23 · 2 điểm · nhóm *Data Pipeline Orchestration* › *Pipeline to ingest raw data into bronze zone (DP1)*

**Cách làm:** [Đã có] validate_bronze bằng Great Expectations. [Cần sửa] run_checkpoint là API GX 0.x -> viết theo version GX đã cài; chụp kết quả.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-24"></a>
## Ingest stage · Pipeline to ingest data from bronze zone into silver and gol

**Rubric:** edai-1 · dòng 24 · 2 điểm · nhóm *Data Pipeline Orchestration* › *Pipeline to ingest data from bronze zone into silver and gold zone (or bronze -> gold only) (DP2)*

**Cách làm:** [Cần làm] DAG dp2: Bronze -> Silver (Spark) -> Gold (SQL SCD2 dim_hotel, fact_bookings, fact_quotes).

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-25"></a>
## Validate stage · Pipeline to ingest data from bronze zone into silver and gol

**Rubric:** edai-1 · dòng 25 · 2 điểm · nhóm *Data Pipeline Orchestration* › *Pipeline to ingest data from bronze zone into silver and gold zone (or bronze -> gold only) (DP2)*

**Cách làm:** [Cần làm] GX cho Silver/Gold: idempotency_key unique, price > 0, mỗi hotel đúng 1 dòng is_current, FK fact -> dim không null.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-26"></a>
## Ingest stage · Pipeline to compute offline feature table (DP3)

**Rubric:** edai-1 · dòng 26 · 2 điểm · nhóm *Data Pipeline Orchestration* › *Pipeline to compute offline feature table (DP3) (Ví dụ: f_customer_total_orders_90d)*

**Cách làm:** [Cần làm] DAG dp3 chạy Spark job: feat_customer_booking_stats, feat_hotel_demand; [Pricing] feat_hotel_occupancy, feat_hotel_conversion_7d, rate_calendar. Ghi qua bảng staging rồi đổi tên trong 1 transaction; event_timestamp = thời điểm tính; outlets Airflow Dataset đặt ở task validate để kích hoạt materialize.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-27"></a>
## Validate stage · Pipeline to compute offline feature table (DP3)

**Rubric:** edai-1 · dòng 27 · 2 điểm · nhóm *Data Pipeline Orchestration* › *Pipeline to compute offline feature table (DP3) (Ví dụ: f_customer_total_orders_90d)*

**Cách làm:** [Cần làm] GX cho feat_*: entity không null, event_timestamp <= created, tỉ lệ trong [0,1], occupancy <= sức chứa.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
