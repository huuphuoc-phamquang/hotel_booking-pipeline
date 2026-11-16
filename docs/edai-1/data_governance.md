# Data governance

Lineage và kết quả kiểm tra dữ liệu của DP1–DP3 được ghi lên DataHub.

Mỗi mục dưới đây ứng với một dòng của rubric. Phần **Cách làm** mô tả giải pháp đã triển khai, đồng bộ từ
cột F của rubric. Phần **Kết quả** ghi test đã chạy, số liệu đo được hoặc ảnh chụp (`docs/images/`).

<a id="edai-1-28"></a>
## Lineage between the pipeline and tables · DP1 linked with related tables

**Rubric:** edai-1 · dòng 28 · 2 điểm · nhóm *Data Governance* › *DP1 linked with related tables*

**Cần nộp (cả nhóm):** Document + thể hiện được các bảng trên DataHub, + thể hiện được các bảng sinh ra từ Airflow pipeline nào + thể hiện được data validation cho các bảng trên DataHub

**Cách làm:** [Đã có] `emit_datahub.py` khai báo lineage của DP1 (landing → `raw_bookings`). [Cần làm] chạy và chụp lineage graph trên DataHub.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-1-29"></a>
## Data validation · DP1 linked with related tables

**Rubric:** edai-1 · dòng 29 · 2 điểm · nhóm *Data Governance* › *DP1 linked with related tables*

**Cách làm:** [Đã có] `emit_validation` gửi `AssertionRunEvent`. [Cần làm] đẩy kết quả Great Expectations của DP1; chụp tab Validation của `raw_bookings` (cần kiểm xem có phải tạo `AssertionInfo` trước không).

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-1-30"></a>
## Lineage between the pipeline and tables · DP2 linked with related tables

**Rubric:** edai-1 · dòng 30 · 2 điểm · nhóm *Data Governance* › *DP2 linked with related tables*

**Cách làm:** [Đã có] `PIPELINES` khai báo `dp2_bronze_to_gold` (`silver_bookings`, `stage_gold`, `upsert_gold`), khớp inlets, outlets của DAG. [Cần làm] chụp lineage `raw_bookings` → `stg_bookings` → `fact_bookings`.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-1-31"></a>
## Data validation · DP2 linked with related tables

**Rubric:** edai-1 · dòng 31 · 2 điểm · nhóm *Data Governance* › *DP2 linked with related tables*

**Cách làm:** [Đã có] `validate_gold` gồm 5 kiểm tra SQL: có dòng cho ngày `ds`, mọi dòng staging đều vào được fact, `amount` > 0, mỗi khách sạn có đúng một phiên bản hiện hành, thời điểm huỷ sau ngày đặt. Kết quả được đẩy lên DataHub dưới dạng `AssertionRunEvent` (`governance.validate_sql`). [Cần làm] chụp tab Validation.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-1-32"></a>
## Lineage between the pipeline and tables · DP3 linked with related tables

**Rubric:** edai-1 · dòng 32 · 2 điểm · nhóm *Data Governance* › *DP3 linked with related tables*

**Cách làm:** [Đã có] `PIPELINES` khai báo `dp3_offline_features.build_features`: `fact_bookings`, `dim_hotel` → `feat_customer_booking_stats`, `feat_hotel_demand`. [Cần làm] chụp lineage.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-1-33"></a>
## Data validation · DP3 linked with related tables

**Rubric:** edai-1 · dòng 33 · 2 điểm · nhóm *Data Governance* › *DP3 linked with related tables*

**Cách làm:** [Đã có] `validate_features` kiểm có dòng cho ngày `ds`, tỉ lệ nằm trong [0, 1], `event_timestamp` ≤ `created`, rồi đẩy kết quả lên DataHub. [Cần làm] chụp tab Validation của từng bảng `feat_`.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._
