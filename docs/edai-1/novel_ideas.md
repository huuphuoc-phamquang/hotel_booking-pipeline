# Novel ideas (edai-1)

Mỗi ý tưởng gồm vấn đề, cách làm và minh chứng đã chạy.

Mỗi mục dưới đây ứng với một dòng của rubric. Phần **Cách làm** mô tả giải pháp đã triển khai, đồng bộ từ
cột F của rubric. Phần **Kết quả** ghi test đã chạy, số liệu đo được hoặc ảnh chụp (`docs/images/`).

<a id="edai-1-39"></a>
## Idea 1 (edai-1): Data contract + DLQ có lỗi cài sẵn

**Rubric:** edai-1 · dòng 39 · 10 điểm · nhóm *Novel ideas*

**Cần nộp (cả nhóm):** Document idea + proof it worked!

**Cách làm:** Idea 1 - Data contract và DLQ với lỗi cài sẵn. Contract viết bằng JSON Schema (`schema/contracts/booking_event.json`), không dùng Schema Registry. Generator thêm 0,5% bản sao lỗi (giá âm, `hotel_id` = 0, thiếu `event_time`) và gắn nhãn `violation` trong event log. `ContractCheck` của Flink chuyển event sai sang topic `booking_events_dlq`, kèm `reason` là trường vi phạm. Minh chứng: `tests/test_stream_gen.py` (contract bắt đúng từng bản lỗi, không chặn event hợp lệ) và `tests/test_stream_e2e.py` (số event trên DLQ theo từng `reason` bằng số lỗi đã cài).

**Kết quả:** `tests/test_stream_e2e.py` chạy cục bộ trên Docker chuỗi replayer → Kafka → Flink → Postgres cho một ngày replay. Số event trên `booking_events_dlq` theo từng `reason` (price, hotel_id, event_time) khớp đúng số bản lỗi generator đã cài. Bên cạnh đó, `tests/test_stream_gen.py` cho thấy contract bắt được mọi bản lỗi và không chặn event hợp lệ. _Chưa có ảnh chụp trên cluster._

<a id="edai-1-40"></a>
## Idea 2 (edai-1): Đối soát batch–stream có ground truth

**Rubric:** edai-1 · dòng 40 · 10 điểm · nhóm *Novel ideas*

**Cách làm:** Idea 2 - Đối soát batch và stream có ground truth. Generator biết chính xác mọi event, nên với mỗi phút, `sum(gold.stream_bookings_1m)` (nhánh tumbling 1 phút) cộng `count(gold.stream_late_bookings)` (side output) phải bằng số booking hợp lệ, đã khử trùng theo `idempotency_key`, có `event_time` trong phút đó. Minh chứng: `tests/test_stream_e2e.py` chạy replayer → Kafka → Flink (image `k8s/flink.Dockerfile`) → Postgres trên Docker, khớp từng phút trên 919 phút và khớp DLQ theo loại lỗi; `tests/test_stream_gen.py` kiểm tính bất biến stream = landing. [Cần làm] chạy cùng phép đối soát trên GKE, chụp bảng kết quả.

**Kết quả:** `tests/test_stream_e2e.py` chạy cục bộ trên Docker. Với mọi phút đã đóng (hơn 900 phút), `stream_bookings_1m` cộng `stream_late_bookings` khớp đúng số booking do generator sinh; không phút nào lệch. _Chưa chạy trên GKE, chưa có ảnh chụp._
