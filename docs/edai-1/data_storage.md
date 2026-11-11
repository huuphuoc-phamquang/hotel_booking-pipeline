# Tối ưu lưu trữ

Lakehouse (Iceberg) và data warehouse (PostgreSQL Gold).

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-1-20"></a>
## Lakehouse

**Rubric:** edai-1 · dòng 20 · 3 điểm · nhóm *Data Storage* › *How to optimize your data storage*

> Lakehouse (ví dụ compaction để gom nhiều file nhỏ thành file lớn, z-order hoặc partitioning)

**Cần nộp (cả nhóm):** Document show đoạn code và phân tích đã optimize được những gì so với chưa optimize

**Cách làm:** [Đã có] optimize.sql: compaction (rewrite_data_files), sort order, expire snapshots. [Thiết kế] catalog lake = Iceberg JDBC catalog trên PostgreSQL (không thêm service). [Cần làm] số file / kích thước / thời gian query trước-sau; sửa mốc ngày viết cứng.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-21"></a>
## Datawarehouse

**Rubric:** edai-1 · dòng 21 · 3 điểm · nhóm *Data Storage* › *How to optimize your data storage*

> Datawarehouse (ví dụ indexing)

**Cách làm:** [Cần làm] chưa có index: thêm index fact_bookings(hotel_key, booking_date), feat_* (entity, event_timestamp), fact_quotes(hotel_id, stay_date); EXPLAIN ANALYZE trước/sau.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
