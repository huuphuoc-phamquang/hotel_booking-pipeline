# Novel ideas (edai-2 & final)

Mỗi ý tưởng: vấn đề, cách làm, bằng chứng đã chạy.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-2-56"></a>
## Idea 1 (edai-2): Calibration so với xác suất thật

**Rubric:** edai-2 · dòng 56 · 2 điểm · nhóm *Novel ideas*

**Cần nộp (cả nhóm):** Document idea + proof it worked!

**Cách làm:** Idea 1 - Calibration so với xác suất thật: generator ghi xác suất huỷ thật p của từng booking vào bucket truth (ngoài landing); join với gold.booking_risk để đo Brier / reliability so với p thật và sai số K bán vượt (K từ xác suất model so với K từ p thật), trước và sau retrain. Proof: notebooks/cancel_risk.ipynb đã chạy: reliability theo decile khớp p thật, sau drift v1 lệch calibration 0,127, v2 0,0008, sai số K 1,62 -> 0,36. [Cần làm] cùng phép đo trên gold.booking_risk của cluster.

**Kết quả:** `notebooks/cancel_risk.ipynb` (chạy cục bộ, dims thu nhỏ):

| | Lệch calibration | Brier vs p thật | \|K model − K thật\| TB |
|---|---|---|---|
| v1, validation trước drift | 0,0009 | 0,016 | 0,30 |
| v1, sau drift 2025-06-01 | 0,127 | 0,040 | 1,62 |
| v2 (retrain trên dữ liệu sau drift) | 0,0008 | 0,019 | 0,36 |

Reliability theo decile trước drift: xác suất dự báo lệch xác suất thật dưới 0,05 ở mọi decile. _Chưa đo trên `gold.booking_risk` của cluster._

<a id="edai-2-57"></a>
## Idea 2 (edai-2): HITL cho bán vượt

**Rubric:** edai-2 · dòng 57 · 2 điểm · nhóm *Novel ideas*

**Cách làm:** Idea 2 - HITL cho bán vượt: tool propose_overbooking tính K cho hotel × stay_date (Poisson-binomial chính xác trên xác suất trong gold.booking_risk, ngưỡng c_spoil/(c_spoil+c_walk)); ghi K bằng apply_overbooking phải qua requireApproval của kagent (Approve/Reject trên UI). Proof: trace phê duyệt + test biên.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

## Bổ sung final-coursework

<a id="final-58"></a>
### Idea 1 (final): Đo drift detector bằng drift biết trước

**Rubric:** final · dòng 58 · 2 điểm · nhóm *Novel ideas*

**Cần nộp (cả nhóm):** Document idea + proof it worked!

**Cách làm:** Idea 1 - Đo drift detector bằng drift biết trước: generator cài drift ở ngày đã biết; đo độ trễ phát hiện và tỉ lệ báo nhầm, so KS vs PSI.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-59"></a>
### Idea 2 (final): A/B có Brier thật

**Rubric:** final · dòng 59 · 2 điểm · nhóm *Novel ideas*

**Cách làm:** Idea 2 - A/B có Brier thật: generator biết xác suất huỷ thật p của từng booking; so v1 và v2 bằng Brier / log-loss so với p thật ngay khi có dự báo, không chờ nhãn sau ngày nhận phòng.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
