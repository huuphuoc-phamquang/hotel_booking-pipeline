# Data governance

Lineage và kết quả kiểm tra dữ liệu của DP1–DP3 được ghi lên DataHub.

Mọi lần chạy dưới đây diễn ra trên GKE (Airflow 2.10.5), dữ liệu minh họa ngày 2025-01-01.

<a id="edai-1-28"></a>
## Lineage của pipeline DP1 (Landing → Bronze)

`emit_datahub.py` khai báo lineage của DP1 (landing → `raw_bookings`). Schema của 3 zone được ingest lên
DataHub bằng job `k8s/datahub-ingest.yaml`: 8 bảng Bronze, 2 bảng Silver, 16 bảng Gold.

Ảnh dưới là lineage của cả ba pipeline, đọc từ trái sang phải: bên trái là task DP1 → các bảng `lake/bronze/raw_*`,
ở giữa là DP2 → Silver → staging Gold → `fact_bookings`, bên phải là DP3 → bảng `feat_*`.

![Lineage trên DataHub](../images/edai-1/datahub-lineage.png)

*Chú thích: Bản đồ Data Lineage tổng thể trên DataHub từ trái sang phải: DP1 (`landing` → `raw_*`), DP2 (`raw_*` → `stg_bookings` → `fact_bookings`) và DP3 (`fact_bookings` → `feat_*`).*

<a id="edai-1-29"></a>
## Kiểm tra chất lượng dữ liệu DP1

`emit_validation` khai báo `AssertionInfo` trước rồi gửi `AssertionRunEvent`, đưa kết quả Great
Expectations của DP1 lên tab Quality của `raw_bookings`.

Assertion `gx_bronze_bookings` hiện ở tab Quality của `lake/bronze/raw_bookings` với trạng thái đạt.

![Validation của raw_bookings](../images/edai-1/datahub-validation-bronze.png)

*Chú thích: Tab Quality trên DataHub của `lake/bronze/raw_bookings` hiển thị assertion `gx_bronze_bookings` đạt trạng thái xanh (Passing).*

<a id="edai-1-30"></a>
## Lineage của pipeline DP2 (Bronze → Silver → Gold)

`PIPELINES` khai báo `dp2_bronze_to_gold` (`silver_bookings`, `stage_gold`, `upsert_gold`), khớp với
inlets và outlets của DAG.

Lineage đi đúng chuỗi `raw_bookings` → `silver_bookings` → `stg_bookings` (Iceberg) → `stage_gold` → các
bảng staging Gold → `upsert_gold` → `fact_bookings`, kèm nhánh dim (`raw_customers`, `raw_hotels`, `raw_hotel_changes`)
(phần giữa ảnh lineage ở mục DP1).

<a id="edai-1-31"></a>
## Kiểm tra chất lượng dữ liệu DP2

`validate_gold` gồm 5 kiểm tra SQL:

- có dữ liệu cho ngày chạy;
- mọi dòng staging đều vào được fact;
- `amount` > 0;
- mỗi khách sạn có đúng một phiên bản hiện hành;
- thời điểm huỷ sau ngày đặt.

Kết quả được đẩy lên DataHub dưới dạng `AssertionRunEvent` (`governance.validate_sql`).

Tab Quality của `fact_bookings` có 4 assertion, tất cả đều đạt: `fact_has_rows_for_ds`,
`staging_all_loaded`, `amount_positive`, `cancel_after_create`. Kiểm tra phiên bản hiện hành SCD2 gắn với `dim_hotel`.

![Validation của fact_bookings](../images/edai-1/datahub-validation-gold.png)

*Chú thích: Tab Quality trên DataHub của `gold.fact_bookings` ghi nhận cả 4 assertion SQL (`fact_has_rows_for_ds`, `staging_all_loaded`, `amount_positive`, `cancel_after_create`) đều Passing.*

<a id="edai-1-32"></a>
## Lineage của pipeline DP3 (Gold → Offline Feature Store)

`PIPELINES` khai báo `dp3_offline_features.build_features` với đầu vào `fact_bookings`, `dim_hotel` và
đầu ra `feat_customer_booking_stats`, `feat_hotel_demand`.

Phía phải ảnh lineage ở mục DP1 thể hiện `fact_bookings` → task `build_features` → `feat_customer_booking_stats`,
`feat_hotel_demand` (và view `labels_cancel`), cùng Airflow Dataset `postgres:5432/warehouse/gold/feat_hotel_demand`.

<a id="edai-1-33"></a>
## Kiểm tra chất lượng dữ liệu DP3

`validate_features` kiểm tra có dữ liệu cho ngày chạy, tỉ lệ nằm trong [0, 1], `event_timestamp` ≤ `created`,
rồi đẩy kết quả lên DataHub.

Tab Quality của `feat_hotel_demand` có 3 assertion, tất cả đều đạt. `feat_customer_booking_stats` có dấu
đạt trên ảnh lineage.

![Validation của feat_hotel_demand](../images/edai-1/datahub-validation-feature.png)

*Chú thích: Tab Quality trên DataHub của `gold.feat_hotel_demand` hiển thị 3/3 assertion (`hotel_rows_for_ds`, `hotel_rate_in_0_1`, `event_before_created`) đều đạt màu xanh.*
