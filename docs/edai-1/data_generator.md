# Data generator

Generator tái lập: lỗi offline, lỗi streaming, data drift và bảng label.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

## Đặc tính dữ liệu đo được

Sinh bằng `python -m generator.profile_data` (thư mục `edai1/`), mẫu đủ 16 shard của 4 ngày, ngoại suy ra cả năm. Đổi `config.yaml` thì chạy lại và thay bảng này; không ghi số đo vào config hay comment.

Mẫu: ngày [10, 100, 200, 300], đủ 16 shard; số cả năm = mẫu × 91. config_sha256 36e83719aa87

| Bảng | Dòng / ngày | Byte / dòng (Parquet zstd) | Dòng / năm | Dung lượng / năm |
|---|---|---|---|---|
| quotes | 26,812,643 | 10.1 | 9.79 tỉ | 98.6 GB |
| bookings | 343,958 | 24.4 | 0.13 tỉ | 3.1 GB |
| cancellations | 119,119 | 15.2 | 0.04 tỉ | 0.7 GB |
| **tổng** | | | | **102.4 GB** |

| Phễu và lỗi dữ liệu | Giá trị |
|---|---|
| Đặt / lượt xem (look-to-book) | 1.26% |
| Lượt xem gặp hết phòng | 4.59% |
| Double submit (dòng thừa / booking) | 1.99% |
| Tỉ lệ huỷ trước drift | 32.8% |
| Tỉ lệ huỷ sau drift | 43.6% |
| Booking schema v1 / v2 trong mẫu | 686,336 / 689,496 |

| Skew theo khách sạn (mỗi ngày, trung bình mẫu) | Lượt xem | Booking |
|---|---|---|
| Top 1 khách sạn | 2.6% | 2.7% |
| Top 10 khách sạn | 9.1% | 9.1% |
| Top 1% khách sạn | 33.0% | 33.0% |
| Khách sạn trung vị (dòng / ngày) | 208 | 2.8 |

| Khách (1 năm) | Giá trị |
|---|---|
| Booking / khách (trung bình) | 4.1 |
| Khách không đặt trong năm | 24% |
| Khách có đặt: trung vị / p99 | 3 / 38 |

| Trần AUC (điểm = công thức nhãn thật) | Trước drift | Sau drift |
|---|---|---|
| oracle (biết propensity ẩn) | 0.736 | 0.745 |
| lead + policy + loyalty | 0.683 | 0.697 |
| lead + policy (cancel-segment, MODEL_INPUTS không có loyalty) | 0.649 | 0.669 |

| Event trễ (booking_created, 1 shard) | Tỉ lệ |
|---|---|
| Trễ 10–15 phút (vào lại qua allowed lateness) | 5.80% |
| Trễ > 15 phút (side output) | 6.84% |
| Qua channel manager (trễ 1–4 giờ) | 0.99% |

<a id="edai-1-5"></a>
## Simulate skew

**Rubric:** edai-1 · dòng 5 · 2 điểm · nhóm *Implement Data Generator* › *Simulate offline data problems (Tối thiểu 100GB, nếu mọi người cảm thấy chưa đủ để thể hiện rõ các optimization thì mọi người hãy tăng lên nhé. Ví dụ: mọi người cố gắng xử lý data skew, nhưng để data quá bé thì hầu như thời gian xử lý không thay đổi nhiều)*

**Cần nộp (cả nhóm):** Document thể hiện data characteristics sau khi generate - Cột nào skew, tỉ lệ như thế nào - Cột nào có high cardinality (tỉ lệ số unique values/tổng số values trong cột) - Schema trước và sau evolution là gì - Tỉ lệ duplicate - Data volume là bao nhiêu

**Cách làm:** [Đã có] Zipf theo khách sạn (hotel_zipf_a) cho cả quotes và bookings, 70% khách sạn ở 3 thành phố, mùa cao điểm theo stay_date (Tết/30-4/hè, cả 2026), sự kiện có announce_date; lệch nặng ở cặp (hotel_id, stay_date) nóng. Số đo (top 1, top 1%, khách sạn trung vị) in bằng python -m generator.profile_data. [Cần làm] histogram, cardinality từng cột.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-6"></a>
## Simulate schema evolution

**Rubric:** edai-1 · dòng 6 · 2 điểm · nhóm *Implement Data Generator* › *Simulate offline data problems (Tối thiểu 100GB, nếu mọi người cảm thấy chưa đủ để thể hiện rõ các optimization thì mọi người hãy tăng lên nhé. Ví dụ: mọi người cố gắng xử lý data skew, nhưng để data quá bé thì hầu như thời gian xử lý không thay đổi nhiều)*

**Cách làm:** [Đã có] schema v2 từ 2025-07-01: bookings thêm cột channel, đổi room_type -> room_category; cancellation_policy có ở cả v1 và v2 nên lỗi dữ liệu không đụng công thức nhãn. Số dòng v1/v2 in bằng profile_data. [Cần làm] ghi bảng schema v1/v2.

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

**Cách làm:** [Đã có] Parquet zstd lên MinIO landing dt=/shard= + manifest sha256: quotes, bookings, cancellations, payments (append-only). Quote là gốc nên >= 100GB đến từ quotes (demand.quotes_per_cell), không tăng số booking. profile_data ước tính dung lượng/năm. [Cần làm] sinh đủ 365 × 16 partition (song song nhiều container theo khoảng ngày), chụp `mc du`.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-9"></a>
## Simulate late arrivals

**Rubric:** edai-1 · dòng 9 · 2 điểm · nhóm *Implement Data Generator* › *Simulate online data problems*

**Cần nộp (cả nhóm):** Tương tự cái trên: - Dữ liệu nào late, late bao lâu - Tỷ lệ duplicate như nào...

**Cách làm:** [Đã có] mobile offline 30% trễ 5-20 phút (một phần vượt watermark 10' + lateness 5' -> side output), payment webhook trễ 1-15 phút, 1% booking đến qua channel manager trễ 1-4 giờ. Replay chỉ phát event có ingest_time trong cửa sổ; lùi 150 ngày để có event huỷ của booking tạo trước cửa sổ; mỗi idempotency_key huỷ 1 lần. Stream dựng event từ chính các booking của gen_bookings ngày 365–394 (cùng booking_id, giá, checkin, nhãn huỷ); các ngày này cũng có trên landing như lô batch của ngày hôm sau. [Cần làm] bảng late theo nguồn + histogram (ingest_time - event_time).

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

**Cách làm:** [Đã có] nhãn huỷ = bảng cancellations(booking_id, cancelled_at) trên landing, nhãn = left join + checkin < ngày chạy; nhãn đặt phòng = quotes.booked (quote_id, booked). [Cần làm] chụp bảng sau khi join với feature (get_historical_features).

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
