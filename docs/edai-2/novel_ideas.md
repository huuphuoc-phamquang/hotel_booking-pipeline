# Novel ideas (edai-2 & final)

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

**Rubric:** edai-2 · dòng 57 · 2 điểm · nhóm *Novel ideas*

**Cách làm:** Idea 2 - Human-in-the-loop cho bán vượt. Tool `propose_overbooking` tính K cho từng khách sạn × đêm bằng phân phối Poisson-binomial chính xác trên xác suất trong `gold.booking_risk`, với ngưỡng c_spoil / (c_spoil + c_walk). Việc ghi K bằng `apply_overbooking` phải qua `requireApproval` của kagent (Approve hoặc Reject trên UI). Minh chứng: trace phê duyệt và test giá trị biên.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

## Bổ sung final-coursework

<a id="final-58"></a>
### Idea 1 (final): Đo drift detector bằng drift biết trước

**Rubric:** final · dòng 58 · 2 điểm · nhóm *Novel ideas*

**Cần nộp (cả nhóm):** Document idea + proof it worked!

**Cách làm:** Idea 1 - Đo drift detector bằng drift biết trước. Generator cài drift vào một ngày đã biết, nhờ đó đo được độ trễ phát hiện và tỉ lệ báo nhầm, đồng thời so sánh KS với PSI.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="final-59"></a>
### Idea 2 (final): A/B có Brier thật

**Rubric:** final · dòng 59 · 2 điểm · nhóm *Novel ideas*

**Cách làm:** Idea 2 - A/B có Brier thật. Generator biết xác suất huỷ thật p của từng booking, nên có thể so v1 và v2 bằng Brier và log-loss so với p thật ngay khi có dự báo, không phải chờ nhãn sau ngày nhận phòng.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._
