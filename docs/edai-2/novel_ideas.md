# Novel ideas (edai-2)

Mỗi ý tưởng gồm vấn đề, cách làm và minh chứng đã chạy.

Mỗi mục dưới đây ứng với một dòng của rubric. Phần **Cách làm** mô tả giải pháp đã triển khai, đồng bộ từ
cột F của rubric. Phần **Kết quả** ghi test đã chạy, số liệu đo được hoặc ảnh chụp (`docs/images/`).

<a id="edai-2-56"></a>
## Idea 1 (edai-2): Calibration so với xác suất thật

**Rubric:** edai-2 · dòng 56 · 2 điểm · nhóm *Novel ideas*

**Cần nộp (cả nhóm):** Document idea + proof it worked!

**Cách làm:** Idea 1 - Calibration so với xác suất thật. Generator ghi xác suất huỷ thật p của từng booking vào bucket truth, nằm ngoài landing. Phép join với `gold.booking_risk` cho phép đo Brier, reliability so với p thật và sai số số phòng bán vượt K (K từ xác suất model so với K từ p thật), trước và sau retrain. Minh chứng: `notebooks/cancel_risk.ipynb` đã chạy; reliability theo decile khớp p thật; sau drift, độ lệch calibration của v1 là 0,127, của v2 là 0,0008; sai số K giảm từ 1,62 xuống 0,36. [Cần làm] chạy cùng phép đo trên `gold.booking_risk` của cluster.

**Kết quả:** `notebooks/cancel_risk.ipynb` chạy cục bộ trên bộ dims thu nhỏ:

| | Lệch calibration | Brier vs p thật | \|K model − K thật\| TB |
|---|---|---|---|
| v1, validation trước drift | 0,0009 | 0,016 | 0,30 |
| v1, sau drift 2025-06-01 | 0,127 | 0,040 | 1,62 |
| v2 (retrain trên dữ liệu sau drift) | 0,0008 | 0,019 | 0,36 |

Trước drift, xác suất dự báo lệch xác suất thật dưới 0,05 ở mọi decile của biểu đồ reliability. _Phép đo này chưa chạy trên `gold.booking_risk` của cluster._

<a id="edai-2-57"></a>
## Idea 2 (edai-2): HITL cho bán vượt

Tool `propose_overbooking` tính K cho từng khách sạn × đêm bằng phân phối Poisson-binomial chính xác trên xác suất
huỷ trong `gold.booking_risk`, với ngưỡng c_spoil / (c_spoil + c_walk), rồi so với số phòng trong `gold.hotel_rooms`.
Tool này chỉ đề xuất. Việc ghi K bằng `apply_overbooking` nằm trong `requireApproval` của policy-agent
([`agents/agents-direct.yaml`](../../edai2/agents/agents-direct.yaml)), nên kagent dừng lời gọi cho tới khi người
duyệt bấm Approve hoặc Reject.

Thử trên cluster thứ hai ngày 2026-11-19: policy-agent đề xuất K cho khách sạn 8528 đêm 2025-01-29, người dùng đồng ý
K = 1, lời gọi `apply_overbooking(8528, 2025-01-29, 1)` chuyển sang trạng thái *Approval required*. Chỉ sau khi bấm
Approve, `gold.overbooking_limits` mới có dòng `8528 | 2025-01-29 | 1`. Qua A2A, cùng lời gọi đó trả task ở trạng thái
`input-required`. Logic K được kiểm bằng `tests/test_overbooking.py` (chạy trong build #7 của Jenkins): giá trị biên
p = 0 và p = 1, không có booking, chi phí không dương, xác suất ngoài [0, 1]; phân phối so với liệt kê đủ 2^n trường
hợp; và tính chất K không giảm khi chi phí chuyển khách giảm.

![Approval required cho apply_overbooking](../images/edai-2/kagent-hitl-approval.png)

![Sau khi Approve, K được ghi](../images/edai-2/kagent-hitl-approved.png)
