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

**Cách làm:** [Đã có] PIPELINES khai báo DP2. [Cần làm] sau khi có DAG dp2, tên dataset phải khớp inlets/outlets; chụp lineage stg_bookings -> fact_bookings.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-31"></a>
## Data validation · DP2 linked with related tables

**Rubric:** edai-1 · dòng 31 · 2 điểm · nhóm *Data Governance* › *DP2 linked with related tables*

**Cách làm:** [Cần làm] đẩy kết quả GX của DP2 (idempotency_key unique...) lên tab Validation của Silver/Gold.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-32"></a>
## Lineage between the pipeline and tables · DP3 linked with related tables

**Rubric:** edai-1 · dòng 32 · 2 điểm · nhóm *Data Governance* › *DP3 linked with related tables*

**Cách làm:** [Đã có] PIPELINES khai báo DP3 (feat_customer_booking_stats). [Cần làm] thêm feat_hotel_demand; chụp lineage.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-33"></a>
## Data validation · DP3 linked with related tables

**Rubric:** edai-1 · dòng 33 · 2 điểm · nhóm *Data Governance* › *DP3 linked with related tables*

**Cách làm:** [Cần làm] đẩy kết quả GX của DP3 lên tab Validation của từng feat_.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
