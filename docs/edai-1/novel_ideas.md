# Novel ideas (edai-1)

Mỗi ý tưởng: vấn đề, cách làm, bằng chứng đã chạy.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-1-39"></a>
## Idea 1 (edai-1): Data contract + DLQ có lỗi cài sẵn

**Rubric:** edai-1 · dòng 39 · 10 điểm · nhóm *Novel ideas*

**Cần nộp (cả nhóm):** Document idea + proof it worked!

**Cách làm:** Idea 1 - Data contract + DLQ có lỗi cài sẵn: contract JSON Schema trong repo (không Schema Registry), Flink kiểm từng event và route bản ghi sai sang topic booking_events_dlq kèm lý do. Proof: số bản ghi DLQ khớp đúng số lỗi generator cài (~0,5%), pipeline không sập.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-40"></a>
## Idea 2 (edai-1): Độ trễ phản ứng giá khi sự kiện được công bố

**Rubric:** edai-1 · dòng 40 · 10 điểm · nhóm *Novel ideas*

**Cách làm:** Idea 2 - Đối soát batch-stream có ground truth: generator biết đúng mọi event; mỗi giờ sum(gold.stream_bookings_1m) (nhánh tumbling 1 phút) + count(gold.stream_late_bookings) (side output) bằng đúng số booking landing (dedup idempotency_key), tách theo loại trễ (mobile, channel manager). Proof: bảng đối soát Flink / landing / Silver; test bất biến stream = landing.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
