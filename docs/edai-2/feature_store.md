# Feature store

Materialize offline -> online, push stream feature, TTL.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-2-11"></a>
## Build data pipeline để incremental materialize dữ liệu mới nhất từ OFFLINE qua ONLINE…

**Rubric:** edai-2 · dòng 11 · 2 điểm · nhóm *Feature Store* › *Build materialize pipeline & jobs for push streaming data into feature stores*

> Build data pipeline (ví dụ với Airflow) để incremental materialize dữ liệu mới nhất từ OFFLINE qua ONLINE store

**Cần nộp (cả nhóm):** Document show ảnh pipeline đã chạy thành công trên Airflow + link tới code pipeline

**Cách làm:** [Đã có] feast_materialize_incremental chạy theo Airflow Dataset của DP3 (sau validate), materialize đúng cửa sổ ngày logic, max_active_runs=1, bắn Dataset kích hoạt score_bookings. [Cần làm] chụp run thành công + dữ liệu trên online store.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-12"></a>
## Deploy các jobs chịu trách nhiệm push streaming feature vào OFFLINE & ONLINE store

**Rubric:** edai-2 · dòng 12 · 2 điểm · nhóm *Feature Store* › *Build materialize pipeline & jobs for push streaming data into feature stores*

> Deploy các jobs chịu trách nhiệm push streaming feature (ở mini-coursework) vào OFFLINE & ONLINE store

**Cần nộp (cả nhóm):** Document show ảnh các jobs đã chạy thành công, dữ liệu đã có + link tới code của các jobs

**Cách làm:** [Đã có] Job 1: Flink sliding window 1 giờ trượt 5 phút upsert gold.feat_hotel_realtime (offline); Job 2: DAG feast_materialize_realtime mỗi 5 phút đưa hotel_realtime lên online. [Cần làm] chụp 2 job chạy + feature online/offline có dữ liệu.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

## Bổ sung final-coursework

<a id="final-19"></a>
### Build data pipeline để incremental materialize dữ liệu mới nhất từ offline qua online…

**Rubric:** final · dòng 19 · 2 điểm · nhóm *Feature Store* › *Build materialize pipeline & jobs for push streaming data into feature stores*

> Build data pipeline (ví dụ Airflow) để incremental materialize dữ liệu mới nhất từ offline qua online store

**Cần nộp (cả nhóm):** + Capture màn hình thể hiện các data pipeline và thứ tự các stage trên Airflow + Capture màn hình thể hiện 2 job đang chạy, và thể hiện output đã chạy thành công + Document tại sao chọn TTL như thế

**Cách làm:** [Đã có] feast_materialize_incremental chạy theo Airflow Dataset của task validate DP3, materialize đúng cửa sổ ngày logic của run DP3 (backfill được), max_active_runs=1, bắn Dataset cho score_bookings; feast_materialize_realtime mỗi 5 phút cho hotel_realtime. [Cần làm] chụp DAG + run.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-20"></a>
### Deploy job chịu trách nhiệm push streaming feature vào OFFLINE store

**Rubric:** final · dòng 20 · 1 điểm · nhóm *Feature Store* › *Build materialize pipeline & jobs for push streaming data into feature stores*

> Deploy job chịu trách nhiệm push streaming feature (ở mini-coursework) vào OFFLINE store

**Cách làm:** [Thiết kế] Job 1: Flink sink JDBC vào gold.feat_hotel_realtime (offline store PostgreSQL). Tách khỏi push vì Feast push offline sang PostgreSQL chưa kiểm.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-21"></a>
### Deploy job chịu trách nhiệm push streaming feature vào ONLINE store

**Rubric:** final · dòng 21 · 1 điểm · nhóm *Feature Store* › *Build materialize pipeline & jobs for push streaming data into feature stores*

> Deploy job chịu trách nhiệm push streaming feature (ở mini-coursework) vào ONLINE store

**Cách làm:** [Đã có] Job 1: Flink sliding window 1 giờ trượt 5 phút upsert gold.feat_hotel_realtime (offline); Job 2: DAG feast_materialize_realtime mỗi 5 phút đưa hotel_realtime lên online. PushSource hotel_realtime_push để sẵn cho store.push(ONLINE) khi cần độ tươi tính bằng giây. [Cần làm] chụp 2 job chạy + feature online có dữ liệu.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-22"></a>
### Define TTL cho từng bảng feature, giải thích tại sao chọn TTL như thế

**Rubric:** final · dòng 22 · 2 điểm · nhóm *Feature Store* › *Build materialize pipeline & jobs for push streaming data into feature stores*

**Cách làm:** [Đã có] features.py: booking_attributes 365 ngày (chấm điểm tới ngày nhận phòng); customer_booking_stats 90 ngày (khách thường chỉ đặt 1-2 lần/năm, quá 90 ngày thì bookings_90d chắc chắn về 0); hotel_demand 2 ngày (DP3 ghi mỗi ngày, chịu trễ 1 lần chạy); hotel_realtime 2 giờ; policy_chunks 365 ngày. [Cần làm] lý do ghi trong docs/edai-2/feature_store.md.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
