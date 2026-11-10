# Schema design

Bảng theo zone, SCD2, bảng feature, quan hệ dim/fact, naming convention.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-1-34"></a>
## Visualize tables on all zones

**Rubric:** edai-1 · dòng 34 · 2 điểm · nhóm *Documentation* › *Schema design*

**Cần nộp (cả nhóm):** Document capture màn hình thể hiện các bảng và quan hệ giữa chúng trên mỗi zone, giải thích từng bảng có nhiệm vụ gì

**Cách làm:** [Cần làm] docs/Schema.md: ERD từng zone (raw_ / stg_ / gold), mỗi bảng 1 dòng mô tả nhiệm vụ.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-35"></a>
## Dim table with SCD 2

**Rubric:** edai-1 · dòng 35 · 2 điểm · nhóm *Documentation* › *Schema design*

> Dim table with SCD 2 (valid_from_ts, valid_to_ts, is_current)

**Cách làm:** [Đã có] dim_hotel valid_from_ts / valid_to_ts / is_current + SQL đóng-mở dòng. [Cần làm] demo 1 khách sạn đổi giá 2 lần -> 3 dòng.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-36"></a>
## Feature tables with 2 columns event_timestamp and created

**Rubric:** edai-1 · dòng 36 · 2 điểm · nhóm *Documentation* › *Schema design*

> Feature tables (feat_ tables) with 2 columns event_timestamp and created

**Cách làm:** [Đã có] feat_customer_booking_stats, feat_hotel_demand có event_timestamp + created. [Pricing] thêm feat_hotel_occupancy cùng 2 cột này.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-37"></a>
## Relationship between dim & fact tables

**Rubric:** edai-1 · dòng 37 · 2 điểm · nhóm *Documentation* › *Schema design*

> Relationship between dim & fact tables (You can simply export via DBeaver or similar tools)

**Cách làm:** [Cần làm] export ERD bằng DBeaver: fact_bookings / fact_quotes <-> dim_hotel, dim_customer, dim_event.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-38"></a>
## Naming convention

**Rubric:** edai-1 · dòng 38 · 2 điểm · nhóm *Documentation* › *Schema design*

> Naming convention (- Gold layer: `dim_`, `fact_`, `obt_`, `feat_`, `raw`, prefix or similar) (- Bronze & Silver layer: `raw_`, `stg_` prefix or similar)

**Cách làm:** [Đã có] raw_ / stg_ / dim_ / fact_ / feat_. [Cần làm] giữ cho bảng mới (raw_quotes, stg_quotes, fact_quotes, dim_event).

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
