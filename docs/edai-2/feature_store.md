# Feature store

Materialize feature từ offline sang online, đẩy stream feature và chọn TTL cho từng bảng.

Mỗi mục dưới đây ứng với một dòng của rubric. Phần **Cách làm** mô tả giải pháp đã triển khai, đồng bộ từ
cột F của rubric. Phần **Kết quả** ghi test đã chạy, số liệu đo được hoặc ảnh chụp (`docs/images/`).

<a id="edai-2-11"></a>
## Build data pipeline để incremental materialize dữ liệu mới nhất từ OFFLINE qua ONLINE…

**Rubric:** edai-2 · dòng 11 · 2 điểm · nhóm *Feature Store* › *Build materialize pipeline & jobs for push streaming data into feature stores*

> Build data pipeline (ví dụ với Airflow) để incremental materialize dữ liệu mới nhất từ OFFLINE qua ONLINE store

**Cần nộp (cả nhóm):** Document show ảnh pipeline đã chạy thành công trên Airflow + link tới code pipeline

**Cách làm:** [Đã có] [`feast_materialize_incremental`](../../edai2/dags/rag_pipeline.py) chạy theo Airflow Dataset của DP3 (sau bước validate), materialize đúng cửa sổ ngày logic với `max_active_runs=1`, rồi phát Dataset kích hoạt `score_bookings`.

**Kết quả:** Ngày 2026-11-19 trên Airflow 2.10.5 (GKE namespace `data`), DAG `dp3_offline_features` cho ngày logic `2025-01-13` chạy thành công và phát Airflow Dataset `FEAT_BATCH` (`postgres://postgres:5432/warehouse/gold/feat_hotel_demand`), tự động kích hoạt DAG `feast_materialize_incremental` ([`edai2/dags/rag_pipeline.py`](../../edai2/dags/rag_pipeline.py)). Các lần thử đầu với pod worker mặc định (2Gi RAM) bị `OOMKilled` khi Feast kéo toàn bộ cửa sổ ngày vào pandas; sau khi cấu hình `MATERIALIZE_POD` (request 2Gi, limit 8Gi), task `materialize` chạy thành công trong khoảng 20 phút (dùng ~3,8 GB RAM), ghi 1,27 triệu dòng feature của cửa sổ ngày `2025-01-13` (401.782 khách hàng × 3 feature = 1.205.346 dòng trong `feast_online.booking_customer_booking_stats` với `event_ts = 2025-01-14 00:00:00+00`, cùng `booking_attributes` và `hotel_demand`) lên PostgreSQL online store và phát tiếp Dataset `feast://online/batch`.

Tổng cộng sau materialize, online store `feast_online` có 1.584.578 booking (`booking_attributes`), 1.973.203 khách (`customer_booking_stats`), 50.000 khách sạn (`hotel_demand`) và 49.596 khách sạn (`hotel_realtime`). booking-mcp đọc được các feature này (dòng 46, 49).

![DAG feast_materialize_incremental tự kích hoạt qua Dataset trên Airflow](../images/edai-2/airflow-materialize-graph.png)

![Log task materialize trên Airflow](../images/edai-2/airflow-materialize-log.png)

![Dữ liệu customer_booking_stats đã materialize lên online store](../images/edai-2/feast-online-customer-stats.png)

![Schema 5 bảng Feast Online Store (feast_online) xuất từ DBeaver](../images/edai-2/schema-feast-online.png)

<a id="edai-2-12"></a>
## Deploy các jobs chịu trách nhiệm push streaming feature vào OFFLINE & ONLINE store

**Rubric:** edai-2 · dòng 12 · 2 điểm · nhóm *Feature Store* › *Build materialize pipeline & jobs for push streaming data into feature stores*

> Deploy các jobs chịu trách nhiệm push streaming feature (ở mini-coursework) vào OFFLINE & ONLINE store

**Cần nộp (cả nhóm):** Document show ảnh các jobs đã chạy thành công, dữ liệu đã có + link tới code của các jobs

**Cách làm:** [Đã có] Job 1: Flink ([`edai1/flink_jobs/`](../../edai1/flink_jobs/), [`edai1/k8s/flink.yaml`](../../edai1/k8s/flink.yaml)) tính cửa sổ trượt 1 giờ, bước 5 phút, upsert `gold.feat_hotel_realtime` (offline). Job 2: DAG [`feast_materialize_realtime`](../../edai2/dags/rag_pipeline.py) chạy mỗi 5 phút, đưa `hotel_realtime` lên online với cửa sổ [`max(event_timestamp)` − 2 giờ, `max`] theo giờ dữ liệu.

**Kết quả:** Cả 2 job đã chạy thành công trên GKE:
- **Job 1 (Flink → Offline Store):** FlinkDeployment trên GKE tiêu thụ stream từ Kafka (`booking_events`), tính cửa sổ trượt 1 giờ (bước 5 phút) và upsert 5.083.405 dòng (`2025-12-31 20:10:00` → `2026-01-03 01:15:00`) vào bảng offline `gold.feat_hotel_realtime`.
- **Job 2 (Airflow `feast_materialize_realtime` → Online Store):** Ngày 2026-11-20 trên Airflow 2.10.5 (GKE namespace `data`), DAG `feast_materialize_realtime` chạy thành công (`scheduled` 27 s, `manual` 32 s), truy vấn `max(event_timestamp)` từ `gold.feat_hotel_realtime` rồi materialize feature view `hotel_realtime` trong cửa sổ 2 giờ `[2026-01-02 23:15:00+00, 2026-01-03 01:15:00+00]` lên `feast_online.booking_hotel_realtime` (49.596 khách sạn có `bookings_1h`, mốc mới nhất `2026-01-03 01:15:00+00`).

![Job 1: Flink job graph đẩy streaming feature vào offline store](../images/edai-1/flink-job-graph.png)

![Job 2: DAG feast_materialize_realtime chạy thành công trên Airflow](../images/edai-2/airflow-materialize-realtime-graph.png)

![Log task materialize của feast_materialize_realtime](../images/edai-2/airflow-materialize-realtime-log.png)

![Dữ liệu hotel_realtime trên cả Offline Store và Online Store](../images/edai-2/feast-realtime-offline-online.png)
