# Data generator

Generator tái lập: lỗi offline, lỗi streaming, data drift và bảng label.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-1-5"></a>
## Simulate skew

**Rubric:** edai-1 · dòng 5 · 2 điểm · nhóm *Implement Data Generator* › *Simulate offline data problems (Tối thiểu 100GB, nếu mọi người cảm thấy chưa đủ để thể hiện rõ các optimization thì mọi người hãy tăng lên nhé. Ví dụ: mọi người cố gắng xử lý data skew, nhưng để data quá bé thì hầu như thời gian xử lý không thay đổi nhiều)*

**Cần nộp (cả nhóm):** Document thể hiện data characteristics sau khi generate - Cột nào skew, tỉ lệ như thế nào - Cột nào có high cardinality (tỉ lệ số unique values/tổng số values trong cột) - Schema trước và sau evolution là gì - Tỉ lệ duplicate - Data volume là bao nhiêu

**Cách làm:** [Đã có] Zipf hotel_zipf_a=1.2, 70% khách sạn ở 3 thành phố, peak Tết/30-4/hè. [Thiết kế] quotes và raw_inventory kế thừa skew này, lệch nặng ở cặp (hotel_id, stay_date) nóng. [Cần làm] docs/Data.md: tỉ trọng top 1% khách sạn và top cặp (hotel_id, stay_date) đo từ dữ liệu sinh, histogram, cardinality từng cột.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-6"></a>
## Simulate schema evolution

**Rubric:** edai-1 · dòng 6 · 2 điểm · nhóm *Implement Data Generator* › *Simulate offline data problems (Tối thiểu 100GB, nếu mọi người cảm thấy chưa đủ để thể hiện rõ các optimization thì mọi người hãy tăng lên nhé. Ví dụ: mọi người cố gắng xử lý data skew, nhưng để data quá bé thì hầu như thời gian xử lý không thay đổi nhiều)*

**Cách làm:** [Đã có] schema v2 từ 2025-07-01: thêm cancellation_policy, đổi room_type -> room_category. [Cần làm] ghi bảng schema v1/v2 + số dòng mỗi version.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-7"></a>
## Simulate another offline data problem

**Rubric:** edai-1 · dòng 7 · 2 điểm · nhóm *Implement Data Generator* › *Simulate offline data problems (Tối thiểu 100GB, nếu mọi người cảm thấy chưa đủ để thể hiện rõ các optimization thì mọi người hãy tăng lên nhé. Ví dụ: mọi người cố gắng xử lý data skew, nhưng để data quá bé thì hầu như thời gian xử lý không thay đổi nhiều)*

> Simulate another offline data problem (Ví dụ: 2% duplicate rate)

**Cách làm:** [Đã có] double submit 2% cùng idempotency_key. [Thêm cho novelty] ~0,5% bản ghi vi phạm data contract (giá âm, hotel_id lạ, thiếu event_time); ghi tỉ lệ đo được.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-8"></a>
## Store data after generating so that we can ingest to Bronze zone later

**Rubric:** edai-1 · dòng 8 · 2 điểm · nhóm *Implement Data Generator* › *Simulate offline data problems (Tối thiểu 100GB, nếu mọi người cảm thấy chưa đủ để thể hiện rõ các optimization thì mọi người hãy tăng lên nhé. Ví dụ: mọi người cố gắng xử lý data skew, nhưng để data quá bé thì hầu như thời gian xử lý không thay đổi nhiều)*

> Store data after generating so that we can ingest to Bronze zone later (Ví dụ: Dùng MinIO/PostgreSQL để mô phỏng data đang ở department khác và mình cần kéo về)

**Cách làm:** [Đã có] Parquet zstd lên MinIO landing dt=/shard= + manifest sha256. [Cần làm] config hiện ~25-30GB: thêm bảng quotes (10-30x bookings) hoặc tăng bookings_per_shard để >= 100GB; chụp `mc du`.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-9"></a>
## Simulate late arrivals

**Rubric:** edai-1 · dòng 9 · 2 điểm · nhóm *Implement Data Generator* › *Simulate online data problems*

**Cần nộp (cả nhóm):** Tương tự cái trên: - Dữ liệu nào late, late bao lâu - Tỷ lệ duplicate như nào...

**Cách làm:** [Đã có] mobile offline 30% trễ 5-10 phút, payment webhook trễ 1-15 phút, channel manager 1% trễ 1-4 giờ. [Cần làm] bảng late theo nguồn + histogram (ingest_time - event_time).

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-10"></a>
## Simulate another streaming data problem

**Rubric:** edai-1 · dòng 10 · 2 điểm · nhóm *Implement Data Generator* › *Simulate online data problems*

> Simulate another streaming data problem (Ví dụ: 1.5% duplicate rate)

**Cách làm:** [Đã có] callback thanh toán trùng 1,5% (at-least-once). [Pricing] thêm event search/quote để Flink tính cầu realtime; ghi tỉ lệ trùng đo được.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

## Bổ sung final-coursework

<a id="final-16"></a>
### Simulate data drift

**Rubric:** final · dòng 16 · 2 điểm · nhóm *Improve the Data Generator* › *Simulate data drift*

**Cần nộp (cả nhóm):** Capture màn hình thể hiện generator configuration và bảng sau khi merge id và label

**Cách làm:** [Đã có] concept drift: label.drift lead_time 0,8 -> 1,4 từ 2025-10-01. [Thiết kế] covariate drift trong config.yaml drift.scenarios (lead time ×1,5, mobile 0,6, giá đối thủ −8%; start + ramp_days).

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-17"></a>
### Using generator configuration

**Rubric:** final · dòng 17 · 2 điểm · nhóm *Improve the Data Generator* › *Simulate data drift*

**Cách làm:** [Đã có] edai1/generator/config.yaml (seed, skew, lỗi, nhãn). [Cần làm] chụp config + khối drift.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-18"></a>
### Tạo bảng label có 2 cột id và label

**Rubric:** final · dòng 18 · 2 điểm · nhóm *Improve the Data Generator*

**Cách làm:** [Thiết kế] generator ghi labels_cancel(booking_id, is_cancelled) và labels_quote(quote_id, booked); chỉ booking đã qua check-in mới có nhãn huỷ. [Cần làm] chụp bảng sau khi join với feature (get_historical_features).

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
