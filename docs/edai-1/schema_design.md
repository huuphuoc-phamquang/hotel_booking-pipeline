# Schema design

Thiết kế bảng theo zone, dimension SCD2, bảng feature, quan hệ dim–fact và quy ước đặt tên.

Mỗi mục dưới đây ứng với một dòng của rubric. Phần **Cách làm** mô tả giải pháp đã triển khai, đồng bộ từ
cột F của rubric. Phần **Kết quả** ghi test đã chạy, số liệu đo được hoặc ảnh chụp (`docs/images/`).

<a id="edai-1-34"></a>
## Visualize tables on all zones

**Rubric:** edai-1 · dòng 34 · 2 điểm · nhóm *Documentation* › *Schema design*

**Cần nộp (cả nhóm):** Document capture màn hình thể hiện các bảng và quan hệ giữa chúng trên mỗi zone, giải thích từng bảng có nhiệm vụ gì

**Cách làm:** [Cần làm] Viết `docs/edai-1/schema_design.md`: ERD cho từng zone (`raw_`, `stg_`, gold), mỗi bảng một dòng mô tả vai trò.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-1-35"></a>
## Dim table with SCD 2

**Rubric:** edai-1 · dòng 35 · 2 điểm · nhóm *Documentation* › *Schema design*

> Dim table with SCD 2 (valid_from_ts, valid_to_ts, is_current)

**Cách làm:** [Đã có] `dim_hotel` có `valid_from_ts`, `valid_to_ts`, `is_current`, cập nhật bằng `sql/dp2_upsert_gold.sql`. `tests/test_gold_sql.py` chạy 40 ngày trên Postgres thật. Kết quả: mỗi khách sạn có số phiên bản bằng 1 cộng số lần đổi giá (có khách sạn từ 3 phiên bản trở lên), đúng một bản hiện hành, fact trỏ đúng phiên bản tại thời điểm đặt, chạy lại cùng ngày không làm thay đổi dữ liệu. [Cần làm] chụp một khách sạn có 3 dòng phiên bản.

**Kết quả:** các test `edai1/tests/test_gold_sql.py` chạy cục bộ và đạt (2026-11-16). Chưa có ảnh chụp trên cluster.

<a id="edai-1-36"></a>
## Feature tables with 2 columns event_timestamp and created

**Rubric:** edai-1 · dòng 36 · 2 điểm · nhóm *Documentation* › *Schema design*

> Feature tables (feat_ tables) with 2 columns event_timestamp and created

**Cách làm:** [Đã có] `feat_customer_booking_stats`, `feat_hotel_demand`, `feat_hotel_realtime` đều có `event_timestamp` và `created`.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-1-37"></a>
## Relationship between dim & fact tables

**Rubric:** edai-1 · dòng 37 · 2 điểm · nhóm *Documentation* › *Schema design*

> Relationship between dim & fact tables (You can simply export via DBeaver or similar tools)

**Cách làm:** [Cần làm] Xuất ERD bằng DBeaver: `fact_bookings`, `fact_quotes` nối với `dim_hotel`, `dim_customer`, `dim_event`.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-1-38"></a>
## Naming convention

**Rubric:** edai-1 · dòng 38 · 2 điểm · nhóm *Documentation* › *Schema design*

> Naming convention (- Gold layer: `dim_`, `fact_`, `obt_`, `feat_`, `raw`, prefix or similar) (- Bronze & Silver layer: `raw_`, `stg_` prefix or similar)

**Cách làm:** [Đã có] Quy ước tiền tố `raw_`, `stg_`, `dim_`, `fact_`, `feat_`. [Cần làm] áp dụng cho các bảng mới (`raw_quotes`, `stg_quotes`, `fact_quotes`, `dim_event`).

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._
