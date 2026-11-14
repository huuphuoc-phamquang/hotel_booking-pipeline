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

**Cách làm:** [Đã có] DAG dp2_bronze_to_gold: đợi DP1 cùng ngày (ExternalTaskSensor) -> silver_bookings (Spark) -> stage_gold (Spark -> staging) -> upsert_gold (sql/dp2_upsert_gold.sql, 1 transaction: dim_customer, dim_hotel SCD2, fact_bookings join khoảng theo phiên bản dim). [Cần làm] fact_quotes; chụp graph + run.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-25"></a>
## Validate stage · Pipeline to ingest data from bronze zone into silver and gol

**Rubric:** edai-1 · dòng 25 · 2 điểm · nhóm *Data Pipeline Orchestration* › *Pipeline to ingest data from bronze zone into silver and gold zone (or bronze -> gold only) (DP2)*

**Cách làm:** [Cần làm] GX cho Silver/Gold: idempotency_key unique, price > 0, mỗi hotel đúng 1 dòng is_current, FK fact -> dim không null.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-26"></a>
## Ingest stage · Pipeline to compute offline feature table (DP3)

**Rubric:** edai-1 · dòng 26 · 2 điểm · nhóm *Data Pipeline Orchestration* › *Pipeline to compute offline feature table (DP3) (Ví dụ: f_customer_total_orders_90d)*

**Cách làm:** [Đã có] DAG dp3_offline_features: sql/dp3_features.sql ghi feat_customer_booking_stats, feat_hotel_demand thẳng trên Gold (upsert, 1 transaction); event_timestamp = hết ngày ds, không phải giờ máy, nên backfill sinh đủ lịch sử point-in-time cho training; task validate bắn Airflow Dataset kích hoạt materialize. [Cần làm] chụp graph + run.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-27"></a>
## Validate stage · Pipeline to compute offline feature table (DP3)

**Rubric:** edai-1 · dòng 27 · 2 điểm · nhóm *Data Pipeline Orchestration* › *Pipeline to compute offline feature table (DP3) (Ví dụ: f_customer_total_orders_90d)*

**Cách làm:** [Cần làm] GX cho feat_*: entity không null, event_timestamp <= created, tỉ lệ trong [0,1], occupancy <= sức chứa.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
