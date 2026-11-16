# Data generator

Generator tái lập được (cùng seed cho cùng dữ liệu), sinh lỗi dữ liệu offline, lỗi streaming, data drift và
bảng nhãn.

Mỗi mục dưới đây ứng với một dòng của rubric. Phần **Cách làm** mô tả giải pháp đã triển khai, đồng bộ từ
cột F của rubric. Phần **Kết quả** ghi test đã chạy, số liệu đo được hoặc ảnh chụp (`docs/images/`).

## Đặc tính dữ liệu đo được

Các bảng dưới đây do `python -m generator.profile_data` (chạy trong thư mục `edai1/`) in ra. Mẫu gồm đủ 16 shard của
12 ngày cách nhau 30 ngày, rải đều các mùa trong năm, rồi ngoại suy ra cả năm. Với `quotes_per_cell` 580 và `conversion`
0,01267, dữ liệu đạt khoảng 108GB, cao hơn mốc 100GB khoảng 8%; tích hai tham số được giữ nguyên nên số booking không
đổi. Khi sửa `config.yaml`, cần chạy lại lệnh và thay các bảng này. Số đo không được ghi vào config hay comment.

Mẫu: ngày [15, 45, 75, 105, 135, 165, 195, 225, 255, 285, 315, 345], đủ 16 shard; số cả năm = mẫu × 30. config_sha256 94e5c466f09d

| Bảng | Dòng / ngày | Byte / dòng (Parquet zstd) | Dòng / năm | Dung lượng / năm |
|---|---|---|---|---|
| quotes | 33,771,299 | 8.4 | 12.33 tỉ | 103.9 GB |
| bookings | 387,034 | 24.3 | 0.14 tỉ | 3.4 GB |
| cancellations | 156,979 | 15.3 | 0.06 tỉ | 0.9 GB |
| **tổng** | | | | **108.2 GB** |

| Phễu và lỗi dữ liệu | Giá trị |
|---|---|
| Đặt / lượt xem (look-to-book) | 1.12% |
| Lượt xem gặp hết phòng | 3.73% |
| Double submit (dòng thừa / booking) | 1.99% |
| Tỉ lệ huỷ trước drift | 32.9% |
| Lead time trung bình trước drift (covariate drift) | 18.6 ngày |
| Tỉ lệ huỷ sau drift | 47.4% |
| Lead time trung bình sau drift (covariate drift) | 28.3 ngày |
| Booking schema v1 / v2 trong mẫu | 2,359,953 / 2,284,456 |

| Skew theo khách sạn (mỗi ngày, trung bình mẫu) | Lượt xem | Booking |
|---|---|---|
| Top 1 khách sạn | 2.6% | 2.7% |
| Top 10 khách sạn | 9.1% | 9.1% |
| Top 1% khách sạn | 33.0% | 33.0% |
| Khách sạn trung vị (dòng / ngày) | 262 | 3.0 |

| Khách (1 năm) | Giá trị |
|---|---|
| Booking / khách (trung bình) | 4.6 |
| Khách không đặt trong năm | 21% |
| Khách có đặt: trung vị / p99 | 3 / 42 |

| Trần AUC (điểm = công thức nhãn thật) | Trước drift | Sau drift |
|---|---|---|
| oracle (biết propensity ẩn) | 0.734 | 0.745 |
| lead + policy + loyalty (input của cancel-risk, chưa tính lịch sử khách) | 0.681 | 0.698 |
| lead + policy (bỏ loyalty) | 0.648 | 0.669 |

| Event trễ (booking_created, 1 shard) | Tỉ lệ |
|---|---|
| Trễ 10–15 phút (vào lại qua allowed lateness) | 5.68% |
| Trễ > 15 phút (side output nhánh tumbling 1 phút) | 6.83% |
| Trễ > 75 phút (side output nhánh trượt 1 giờ) | 0.88% |
| Qua channel manager (trễ 1–4 giờ) | 0.97% |

<a id="edai-1-5"></a>
## Simulate skew

**Rubric:** edai-1 · dòng 5 · 2 điểm · nhóm *Implement Data Generator* › *Simulate offline data problems (Tối thiểu 100GB, nếu mọi người cảm thấy chưa đủ để thể hiện rõ các optimization thì mọi người hãy tăng lên nhé. Ví dụ: mọi người cố gắng xử lý data skew, nhưng để data quá bé thì hầu như thời gian xử lý không thay đổi nhiều)*

**Cần nộp (cả nhóm):** Document thể hiện data characteristics sau khi generate - Cột nào skew, tỉ lệ như thế nào - Cột nào có high cardinality (tỉ lệ số unique values/tổng số values trong cột) - Schema trước và sau evolution là gì - Tỉ lệ duplicate - Data volume là bao nhiêu

**Cách làm:** [Đã có] Lượt xem và booking lệch theo phân phối Zipf của khách sạn (`hotel_zipf_a`). 70% khách sạn tập trung ở 3 thành phố. Mùa cao điểm tính theo `stay_date` (Tết, 30/4, hè, cả năm 2026), sự kiện chỉ tác động từ `announce_date`. Độ lệch nặng nhất nằm ở các cặp (`hotel_id`, `stay_date`) nóng. Lệnh `python -m generator.profile_data` in các số đo top 1, top 1% và khách sạn trung vị. [Cần làm] vẽ histogram và tính cardinality từng cột.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-1-6"></a>
## Simulate schema evolution

**Rubric:** edai-1 · dòng 6 · 2 điểm · nhóm *Implement Data Generator* › *Simulate offline data problems (Tối thiểu 100GB, nếu mọi người cảm thấy chưa đủ để thể hiện rõ các optimization thì mọi người hãy tăng lên nhé. Ví dụ: mọi người cố gắng xử lý data skew, nhưng để data quá bé thì hầu như thời gian xử lý không thay đổi nhiều)*

**Cách làm:** [Đã có] Từ 2025-07-01, bảng bookings chuyển sang schema v2: thêm cột `channel`, đổi `room_type` thành `room_category`. Cột `cancellation_policy` có ở cả hai phiên bản, nên thay đổi schema không ảnh hưởng tới công thức nhãn. `profile_data` in số dòng của từng phiên bản. [Cần làm] ghi bảng so sánh schema v1 và v2.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-1-7"></a>
## Simulate another offline data problem

**Rubric:** edai-1 · dòng 7 · 2 điểm · nhóm *Implement Data Generator* › *Simulate offline data problems (Tối thiểu 100GB, nếu mọi người cảm thấy chưa đủ để thể hiện rõ các optimization thì mọi người hãy tăng lên nhé. Ví dụ: mọi người cố gắng xử lý data skew, nhưng để data quá bé thì hầu như thời gian xử lý không thay đổi nhiều)*

> Simulate another offline data problem (Ví dụ: 2% duplicate rate)

**Cách làm:** [Đã có] 2% booking bị gửi hai lần với cùng `idempotency_key`. [Thêm cho novelty] Khoảng 0,5% bản ghi vi phạm data contract (giá âm, `hotel_id` không tồn tại, thiếu `event_time`); ghi lại tỉ lệ đo được.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-1-8"></a>
## Store data after generating so that we can ingest to Bronze zone later

**Rubric:** edai-1 · dòng 8 · 2 điểm · nhóm *Implement Data Generator* › *Simulate offline data problems (Tối thiểu 100GB, nếu mọi người cảm thấy chưa đủ để thể hiện rõ các optimization thì mọi người hãy tăng lên nhé. Ví dụ: mọi người cố gắng xử lý data skew, nhưng để data quá bé thì hầu như thời gian xử lý không thay đổi nhiều)*

> Store data after generating so that we can ingest to Bronze zone later (Ví dụ: Dùng MinIO/PostgreSQL để mô phỏng data đang ở department khác và mình cần kéo về)

**Cách làm:** [Đã có] Generator ghi Parquet nén zstd lên MinIO landing theo `dt=`/`shard=`, kèm manifest sha256, cho các bảng append-only: quotes, bookings, cancellations, payments. Xác suất huỷ thật `p_cancel_true` nằm ở bucket riêng `truth/p_cancel/`, ngoài landing, pipeline không đọc. Quote là dữ liệu gốc, nên dung lượng ≥ 100GB đến từ quotes (`demand.quotes_per_cell`) thay vì tăng số booking. `profile_data` ước tính dung lượng một năm từ 12 ngày rải đều trong năm. [Cần làm] chạy sinh đủ 365 × 16 partition (song song nhiều container theo khoảng ngày), chụp `mc du`.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-1-9"></a>
## Simulate late arrivals

**Rubric:** edai-1 · dòng 9 · 2 điểm · nhóm *Implement Data Generator* › *Simulate online data problems*

**Cần nộp (cả nhóm):** Tương tự cái trên: - Dữ liệu nào late, late bao lâu - Tỷ lệ duplicate như nào...

**Cách làm:** [Đã có] Ba nguồn event trễ: 30% booking từ mobile offline trễ 5–20 phút (một phần vượt watermark 10 phút cộng lateness 5 phút nên rơi ra side output), webhook thanh toán trễ 1–15 phút, 1% booking qua channel manager trễ 1–4 giờ. Replay chỉ phát event có `ingest_time` trong cửa sổ. Generator lùi 150 ngày để có event huỷ của booking tạo trước cửa sổ, mỗi `idempotency_key` huỷ đúng một lần. Event log gom mỗi ngày ingest thành một file đã sắp theo `ingest_time`, nên replay chỉ mở vài file cùng lúc. Lần chạy đầu sinh khoảng 2.900 partition song song bằng `GEN_WORKERS` process, thay cho cách sinh tuần tự mất khoảng 3 giờ. [Cần làm] lập bảng event trễ theo nguồn và histogram của (`ingest_time` − `event_time`).

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-1-10"></a>
## Simulate another streaming data problem

**Rubric:** edai-1 · dòng 10 · 2 điểm · nhóm *Implement Data Generator* › *Simulate online data problems*

> Simulate another streaming data problem (Ví dụ: 1.5% duplicate rate)

**Cách làm:** [Đã có] 1,5% callback thanh toán bị gửi lặp (at-least-once); Flink khử trùng theo `event_id`. `generator/profile_data` in tỉ lệ đo được.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

## Bổ sung final-coursework

<a id="final-16"></a>
### Simulate data drift

**Rubric:** final · dòng 16 · 2 điểm · nhóm *Improve the Data Generator* › *Simulate data drift*

**Cần nộp (cả nhóm):** Capture màn hình thể hiện generator configuration và bảng sau khi merge id và label

**Cách làm:** [Đã có] Concept drift (`label.drift`: hệ số `lead_time` tăng từ 0,8 lên 1,4) và covariate drift (`covariate_drift`: lead time ×1,5) cùng bắt đầu từ 2025-06-01. Mốc giữa năm để nhãn của booking sau drift kịp chín trong phạm vi 365 ngày dữ liệu. `profile_data` in lead time và tỉ lệ huỷ trước, sau drift. [Cần làm] chụp bảng số đo.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="final-17"></a>
### Using generator configuration

**Rubric:** final · dòng 17 · 2 điểm · nhóm *Improve the Data Generator* › *Simulate data drift*

**Cách làm:** [Đã có] `edai1/generator/config.yaml` chứa seed, cấu hình skew, lỗi dữ liệu và nhãn. [Cần làm] chụp config và khối drift.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="final-18"></a>
### Tạo bảng label có 2 cột id và label

**Rubric:** final · dòng 18 · 2 điểm · nhóm *Improve the Data Generator*

**Cách làm:** [Đã có] View Gold `labels_cancel(booking_id, is_cancelled)` đánh dấu booking huỷ trước ngày nhận phòng, dựa trên cancellations của landing. Training join view này và chỉ lấy booking đã chín nhãn. [Cần làm] chụp bảng sau khi join với feature (`get_historical_features`).

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._
