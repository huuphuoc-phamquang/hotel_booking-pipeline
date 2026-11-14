# Data governance

Lineage và data validation DP1–DP3 trên DataHub.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-1-28"></a>
## Lineage between the pipeline and tables · DP1 linked with related tables

**Rubric:** edai-1 · dòng 28 · 2 điểm · nhóm *Data Governance* › *DP1 linked with related tables*

**Cần nộp (cả nhóm):** Document + thể hiện được các bảng trên DataHub, + thể hiện được các bảng sinh ra từ Airflow pipeline nào + thể hiện được data validation cho các bảng trên DataHub

**Cách làm:** [Đã có] emit_datahub.py khai báo lineage DP1 (landing -> raw_bookings). [Cần làm] chạy, chụp lineage graph trên DataHub.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-29"></a>
## Data validation · DP1 linked with related tables

**Rubric:** edai-1 · dòng 29 · 2 điểm · nhóm *Data Governance* › *DP1 linked with related tables*

**Cách làm:** [Đã có] emit_validation (AssertionRunEvent). [Cần làm] đẩy kết quả GX của DP1; chụp tab Validation của raw_bookings (kiểm tra cần AssertionInfo).

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-30"></a>
## Lineage between the pipeline and tables · DP2 linked with related tables

**Rubric:** edai-1 · dòng 30 · 2 điểm · nhóm *Data Governance* › *DP2 linked with related tables*

**Cách làm:** [Đã có] PIPELINES khai báo dp2_bronze_to_gold (silver_bookings, stage_gold, upsert_gold) khớp inlets/outlets của DAG. [Cần làm] chụp lineage raw_bookings -> stg_bookings -> fact_bookings.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-31"></a>
## Data validation · DP2 linked with related tables

**Rubric:** edai-1 · dòng 31 · 2 điểm · nhóm *Data Governance* › *DP2 linked with related tables*

**Cách làm:** [Đã có] validate_gold: 5 check SQL (có dòng cho ngày ds, staging nào cũng vào được fact, amount > 0, mỗi khách sạn đúng 1 phiên bản hiện hành, huỷ sau ngày đặt) đẩy AssertionRunEvent lên DataHub (governance.validate_sql). [Cần làm] chụp tab Validation.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-32"></a>
## Lineage between the pipeline and tables · DP3 linked with related tables

**Rubric:** edai-1 · dòng 32 · 2 điểm · nhóm *Data Governance* › *DP3 linked with related tables*

**Cách làm:** [Đã có] PIPELINES khai báo dp3_offline_features.build_features: fact_bookings, dim_hotel -> feat_customer_booking_stats, feat_hotel_demand. [Cần làm] chụp lineage.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-33"></a>
## Data validation · DP3 linked with related tables

**Rubric:** edai-1 · dòng 33 · 2 điểm · nhóm *Data Governance* › *DP3 linked with related tables*

**Cách làm:** [Đã có] validate_features: có dòng cho ngày ds, tỉ lệ trong [0, 1], event_timestamp <= created; đẩy lên DataHub. [Cần làm] chụp tab Validation của từng feat_.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
