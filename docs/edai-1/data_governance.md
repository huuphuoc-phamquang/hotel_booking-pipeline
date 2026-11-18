# Data governance

Lineage và kết quả kiểm tra dữ liệu của DP1–DP3 được ghi lên DataHub.

Mỗi mục ứng với một dòng của rubric, gồm phần **Thực thi** (đã làm gì, chạy ở đâu) và **Kết quả** (ảnh chụp trong
`docs/images/`). Mọi lần chạy dưới đây diễn ra trên GKE ngày 2026-11-18 (Airflow 2.10.5, KubernetesExecutor, image
`airflow-booking:b9cf9a8-1`), backfill ngày `ds` = 2025-01-01.

<a id="edai-1-28"></a>
## Lineage between the pipeline and tables · DP1 linked with related tables

**Thực thi:** `emit_datahub.py` khai báo lineage của DP1 (landing → `raw_bookings`). Schema của 3 zone được ingest lên
DataHub bằng job `k8s/datahub-ingest.yaml`: 8 bảng Bronze, 2 bảng Silver, 16 bảng Gold.

**Kết quả:** lineage trên DataHub nối các task DP1 với các bảng `lake/bronze/raw_*` và đi tiếp qua DP2, DP3.

![Lineage trên DataHub](../images/edai-1/datahub-lineage.png)

<a id="edai-1-29"></a>
## Data validation · DP1 linked with related tables

**Thực thi:** `emit_validation` khai báo `AssertionInfo` trước rồi gửi `AssertionRunEvent`, đưa kết quả Great
Expectations của DP1 lên tab Quality của `raw_bookings`.

**Kết quả:** assertion `gx_bronze_bookings` hiện ở tab Quality của `lake/bronze/raw_bookings` với trạng thái đạt.

![Validation của raw_bookings](../images/edai-1/datahub-validation-bronze.png)

<a id="edai-1-30"></a>
## Lineage between the pipeline and tables · DP2 linked with related tables

**Thực thi:** `PIPELINES` khai báo `dp2_bronze_to_gold` (`silver_bookings`, `stage_gold`, `upsert_gold`), khớp với
inlets và outlets của DAG.

**Kết quả:** lineage đi đúng chuỗi `raw_bookings` → `silver_bookings` → `stg_bookings` (Iceberg) → `stage_gold` → các
bảng staging Gold → `upsert_gold` → `fact_bookings`, kèm nhánh dim (`raw_customers`, `raw_hotels`, `raw_hotel_changes`).

![Lineage trên DataHub](../images/edai-1/datahub-lineage.png)

<a id="edai-1-31"></a>
## Data validation · DP2 linked with related tables

**Thực thi:** `validate_gold` gồm 5 kiểm tra SQL:

- có dòng cho ngày `ds`;
- mọi dòng staging đều vào được fact;
- `amount` > 0;
- mỗi khách sạn có đúng một phiên bản hiện hành;
- thời điểm huỷ sau ngày đặt.

Kết quả được đẩy lên DataHub dưới dạng `AssertionRunEvent` (`governance.validate_sql`).

**Kết quả:** tab Quality của `fact_bookings` có 4 assertion, tất cả đều đạt: `fact_has_rows_for_ds`,
`staging_all_loaded`, `amount_positive`, `cancel_after_create`. Kiểm tra phiên bản hiện hành SCD2 gắn với `dim_hotel`.

![Validation của fact_bookings](../images/edai-1/datahub-validation-gold.png)

<a id="edai-1-32"></a>
## Lineage between the pipeline and tables · DP3 linked with related tables

**Thực thi:** `PIPELINES` khai báo `dp3_offline_features.build_features` với đầu vào `fact_bookings`, `dim_hotel` và
đầu ra `feat_customer_booking_stats`, `feat_hotel_demand`.

**Kết quả:** phía phải ảnh lineage thể hiện `fact_bookings` → task `build_features` → `feat_customer_booking_stats`,
`feat_hotel_demand` (và view `labels_cancel`), cùng Airflow Dataset `postgres:5432/warehouse/gold/feat_hotel_demand`.

![Lineage trên DataHub](../images/edai-1/datahub-lineage.png)

<a id="edai-1-33"></a>
## Data validation · DP3 linked with related tables

**Thực thi:** `validate_features` kiểm có dòng cho ngày `ds`, tỉ lệ nằm trong [0, 1], `event_timestamp` ≤ `created`,
rồi đẩy kết quả lên DataHub.

**Kết quả:** tab Quality của `feat_hotel_demand` có 3 assertion, tất cả đều đạt. `feat_customer_booking_stats` có dấu
đạt trên ảnh lineage.

![Validation của feat_hotel_demand](../images/edai-1/datahub-validation-feature.png)
