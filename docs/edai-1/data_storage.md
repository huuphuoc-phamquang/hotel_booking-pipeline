# Tối ưu lưu trữ

Lakehouse dùng Iceberg, data warehouse là tầng Gold trên PostgreSQL.

Mỗi mục dưới đây ứng với một dòng của rubric. Phần **Cách làm** mô tả giải pháp đã triển khai, đồng bộ từ
cột F của rubric. Phần **Kết quả** ghi test đã chạy, số liệu đo được hoặc ảnh chụp (`docs/images/`).

<a id="edai-1-20"></a>
## Lakehouse

**Rubric:** edai-1 · dòng 20 · 3 điểm · nhóm *Data Storage* › *How to optimize your data storage*

> Lakehouse (ví dụ compaction để gom nhiều file nhỏ thành file lớn, z-order hoặc partitioning)

**Cần nộp (cả nhóm):** Document show đoạn code và phân tích đã optimize được những gì so với chưa optimize

**Cách làm:** [Đã có] `optimize.sql` gồm compaction (`rewrite_data_files`), sort order và expire snapshots. [Thiết kế] Catalog `lake` là Iceberg JDBC catalog đặt trên chính PostgreSQL, không thêm service. [Cần làm] đo số file, kích thước file và thời gian query trước, sau; bỏ mốc ngày viết cứng.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-1-21"></a>
## Datawarehouse

**Rubric:** edai-1 · dòng 21 · 3 điểm · nhóm *Data Storage* › *How to optimize your data storage*

> Datawarehouse (ví dụ indexing)

**Cách làm:** [Đã có] `schema/gold_schema.sql` tạo index `fact_bookings(customer_key, booking_date)`, `(hotel_key, booking_date)`, `(checkin_date)`, `booking_risk(hotel_id, stay_date, scored_date)` và partial unique `dim_hotel(hotel_id) WHERE is_current`; các bảng `feat_*` dùng khoá chính (entity, `event_timestamp`). [Cần làm] index `fact_quotes(hotel_id, stay_date)`; so `EXPLAIN ANALYZE` trước và sau.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._
