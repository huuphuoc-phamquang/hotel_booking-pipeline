# Novel ideas (edai-1)

Mỗi ý tưởng: vấn đề, cách làm, bằng chứng đã chạy.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-1-39"></a>
## Idea 1 (edai-1): Data contract + DLQ có lỗi cài sẵn

**Rubric:** edai-1 · dòng 39 · 10 điểm · nhóm *Novel ideas*

**Cần nộp (cả nhóm):** Document idea + proof it worked!

**Cách làm:** Idea 1 - Data contract + DLQ có lỗi cài sẵn: contract JSON Schema schema/contracts/booking_event.json (không Schema Registry); generator thêm 0,5% bản sao lỗi (giá âm / hotel_id = 0 / thiếu event_time, nhãn violation trong event log); Flink ContractCheck route event sai sang topic booking_events_dlq kèm reason = trường vi phạm. Proof: tests/test_stream_gen.py (contract bắt đúng từng bản lỗi, không chặn event thật) + tests/test_stream_e2e.py (số event trên DLQ theo reason = số lỗi cài).

**Kết quả:** chạy cục bộ trên Docker (`tests/test_stream_e2e.py`: replayer → Kafka → Flink → Postgres, 1 ngày replay): số event trên `booking_events_dlq` theo `reason` (price / hotel_id / event_time) bằng đúng số bản lỗi generator cài theo từng loại; `tests/test_stream_gen.py`: contract bắt đúng mọi bản lỗi, không chặn event thật. _Chưa có ảnh chụp trên cluster._

<a id="edai-1-40"></a>
## Idea 2 (edai-1): Đối soát batch–stream có ground truth

**Rubric:** edai-1 · dòng 40 · 10 điểm · nhóm *Novel ideas*

**Cách làm:** Idea 2 - Đối soát batch-stream có ground truth: generator biết đúng mọi event; mỗi phút sum(gold.stream_bookings_1m) (nhánh tumbling 1 phút) + count(gold.stream_late_bookings) (side output) bằng đúng số booking (đúng contract, dedup idempotency_key) có event_time trong phút đó. Proof: tests/test_stream_e2e.py chạy replayer -> Kafka -> Flink (image k8s/flink.Dockerfile) -> Postgres trên Docker, khớp từng phút (919 phút), cùng DLQ theo loại lỗi; test bất biến stream = landing (tests/test_stream_gen.py). [Cần làm] chạy cùng phép đối soát trên GKE, chụp bảng.

**Kết quả:** chạy cục bộ trên Docker (`tests/test_stream_e2e.py`): mọi phút đã đóng (hơn 900 phút), mỗi phút `stream_bookings_1m` + `stream_late_bookings` khớp đúng số booking generator sinh, không lệch phút nào. _Chưa chạy trên GKE, chưa có ảnh chụp._
