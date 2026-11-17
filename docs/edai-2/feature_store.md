# Feature store

Materialize feature từ offline sang online, đẩy stream feature và chọn TTL cho từng bảng.

Mỗi mục dưới đây ứng với một dòng của rubric. Phần **Cách làm** mô tả giải pháp đã triển khai, đồng bộ từ
cột F của rubric. Phần **Kết quả** ghi test đã chạy, số liệu đo được hoặc ảnh chụp (`docs/images/`).

<a id="edai-2-11"></a>
## Build data pipeline để incremental materialize dữ liệu mới nhất từ OFFLINE qua ONLINE…

**Rubric:** edai-2 · dòng 11 · 2 điểm · nhóm *Feature Store* › *Build materialize pipeline & jobs for push streaming data into feature stores*

> Build data pipeline (ví dụ với Airflow) để incremental materialize dữ liệu mới nhất từ OFFLINE qua ONLINE store

**Cần nộp (cả nhóm):** Document show ảnh pipeline đã chạy thành công trên Airflow + link tới code pipeline

**Cách làm:** [Đã có] `feast_materialize_incremental` chạy theo Airflow Dataset của DP3 (sau bước validate), materialize đúng cửa sổ ngày logic với `max_active_runs=1`, rồi phát Dataset kích hoạt `score_bookings`. [Cần làm] chụp lần chạy thành công và dữ liệu trên online store.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-2-12"></a>
## Deploy các jobs chịu trách nhiệm push streaming feature vào OFFLINE & ONLINE store

**Rubric:** edai-2 · dòng 12 · 2 điểm · nhóm *Feature Store* › *Build materialize pipeline & jobs for push streaming data into feature stores*

> Deploy các jobs chịu trách nhiệm push streaming feature (ở mini-coursework) vào OFFLINE & ONLINE store

**Cần nộp (cả nhóm):** Document show ảnh các jobs đã chạy thành công, dữ liệu đã có + link tới code của các jobs

**Cách làm:** [Đã có] Job 1: Flink tính cửa sổ trượt 1 giờ, bước 5 phút, upsert `gold.feat_hotel_realtime` (offline). Job 2: DAG `feast_materialize_realtime` chạy mỗi 5 phút, đưa `hotel_realtime` lên online với cửa sổ [`max(event_timestamp)` − 2 giờ, `max`] theo giờ dữ liệu. [Cần làm] chụp 2 job đang chạy và feature có dữ liệu ở cả online lẫn offline.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._
