# Feature store

Materialize offline -> online, push stream feature, TTL.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-2-11"></a>
## Build data pipeline để incremental materialize dữ liệu mới nhất từ OFFLINE qua ONLINE…

**Rubric:** edai-2 · dòng 11 · 2 điểm · nhóm *Feature Store* › *Build materialize pipeline & jobs for push streaming data into feature stores*

> Build data pipeline (ví dụ với Airflow) để incremental materialize dữ liệu mới nhất từ OFFLINE qua ONLINE store

**Cần nộp (cả nhóm):** Document show ảnh pipeline đã chạy thành công trên Airflow + link tới code pipeline

**Cách làm:** [Đã có] feast_materialize_incremental. [Cần sửa] lên lịch theo Airflow Dataset của DP3 (sau validate) thay vì mỗi giờ, max_active_runs=1. [Cần làm] chụp run thành công + dữ liệu trên online store.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-12"></a>
## Deploy các jobs chịu trách nhiệm push streaming feature vào OFFLINE & ONLINE store

**Rubric:** edai-2 · dòng 12 · 2 điểm · nhóm *Feature Store* › *Build materialize pipeline & jobs for push streaming data into feature stores*

> Deploy các jobs chịu trách nhiệm push streaming feature (ở mini-coursework) vào OFFLINE & ONLINE store

**Cần nộp (cả nhóm):** Document show ảnh các jobs đã chạy thành công, dữ liệu đã có + link tới code của các jobs

**Cách làm:** [Cần làm] Flink chưa push vào Feast. [Thiết kế] sliding window 1 giờ trượt 1 phút ra bookings_1h; Job 1 sink JDBC vào gold.feat_hotel_realtime (offline), Job 2 feature-pusher store.push(..., to=PushMode.ONLINE) (online); tách 2 job vì chưa kiểm Feast push offline sang PostgreSQL. [Pricing] window 5 phút theo hotel x stay_date. [Cần làm] chụp 2 job chạy + feature online/offline có dữ liệu.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

## Bổ sung final-coursework

<a id="final-19"></a>
### Build data pipeline để incremental materialize dữ liệu mới nhất từ offline qua online…

**Rubric:** final · dòng 19 · 2 điểm · nhóm *Feature Store* › *Build materialize pipeline & jobs for push streaming data into feature stores*

> Build data pipeline (ví dụ Airflow) để incremental materialize dữ liệu mới nhất từ offline qua online store

**Cần nộp (cả nhóm):** + Capture màn hình thể hiện các data pipeline và thứ tự các stage trên Airflow + Capture màn hình thể hiện 2 job đang chạy, và thể hiện output đã chạy thành công + Document tại sao chọn TTL như thế

**Cách làm:** [Đã có] DAG feast_materialize_incremental (mỗi giờ). [Thiết kế] lên lịch theo Airflow Dataset của task validate DP3. [Cần làm] chụp DAG + 2 job chạy.

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

**Cách làm:** [Đã có] PushSource hotel_realtime_push. [Thiết kế] Job 2 feature-pusher: store.push(..., to=PushMode.ONLINE), bookings_1h thay đếm 1 phút.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-22"></a>
### Define TTL cho từng bảng feature, giải thích tại sao chọn TTL như thế

**Rubric:** final · dòng 22 · 2 điểm · nhóm *Feature Store* › *Build materialize pipeline & jobs for push streaming data into feature stores*

**Cách làm:** [Đã có] features.py: customer_booking_stats, hotel_demand 2 ngày (DP3 ghi mỗi ngày, chịu trễ 1 lần chạy); hotel_realtime 2 giờ; policy_chunks 365 ngày. [Thiết kế] hotel_occupancy 1 ngày. Lý do ghi trong docs/Feature_store.md.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
