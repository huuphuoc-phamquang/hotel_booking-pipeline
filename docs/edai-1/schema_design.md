# Schema design

Bảng theo zone, SCD2, bảng feature, quan hệ dim/fact, naming convention.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-1-34"></a>
## Visualize tables on all zones

**Rubric:** edai-1 · dòng 34 · 2 điểm · nhóm *Documentation* › *Schema design*

**Cần nộp (cả nhóm):** Document capture màn hình thể hiện các bảng và quan hệ giữa chúng trên mỗi zone, giải thích từng bảng có nhiệm vụ gì

**Cách làm:** [Cần làm] docs/edai-1/schema_design.md: ERD từng zone (raw_ / stg_ / gold), mỗi bảng 1 dòng mô tả nhiệm vụ.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-35"></a>
## Dim table with SCD 2

**Rubric:** edai-1 · dòng 35 · 2 điểm · nhóm *Documentation* › *Schema design*

> Dim table with SCD 2 (valid_from_ts, valid_to_ts, is_current)

**Cách làm:** [Đã có] dim_hotel valid_from_ts / valid_to_ts / is_current + sql/dp2_upsert_gold.sql; tests/test_gold_sql.py chạy 40 ngày trên Postgres thật: mỗi khách sạn có 1 + số lần đổi giá phiên bản (có khách sạn >= 3 phiên bản), đúng 1 bản hiện hành, fact trỏ đúng phiên bản lúc đặt, chạy lại cùng ngày không đổi. [Cần làm] chụp 1 khách sạn 3 dòng.

**Kết quả:** chạy cục bộ, pass (2026-11-16): `edai1/tests/test_gold_sql.py`. _Chưa có ảnh chụp trên cluster._

<a id="edai-1-36"></a>
## Feature tables with 2 columns event_timestamp and created

**Rubric:** edai-1 · dòng 36 · 2 điểm · nhóm *Documentation* › *Schema design*

> Feature tables (feat_ tables) with 2 columns event_timestamp and created

**Cách làm:** [Đã có] feat_customer_booking_stats, feat_hotel_demand, feat_hotel_realtime có event_timestamp + created.

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
