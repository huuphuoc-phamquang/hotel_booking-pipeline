# Novel ideas (edai-2 & final)

Mỗi ý tưởng: vấn đề, cách làm, bằng chứng đã chạy.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-2-56"></a>
## Idea 1 (edai-2): Regret so với giá tối ưu thật P*

**Rubric:** edai-2 · dòng 56 · 2 điểm · nhóm *Novel ideas*

**Cần nộp (cả nhóm):** Document idea + proof it worked!

**Cách làm:** Idea 1 - Calibration so với xác suất thật: generator ghi xác suất huỷ thật p của từng booking vào bucket truth (ngoài landing); join với gold.booking_risk để đo Brier / reliability so với p thật và sai số K bán vượt (K từ xác suất model so với K từ p thật), trước và sau retrain. Proof: reliability diagram + bảng sai số K.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-57"></a>
## Idea 2 (edai-2): Định giá công bằng có kiểm chứng + HITL

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
### Idea 2 (final): A/B có doanh thu thật

**Rubric:** final · dòng 59 · 2 điểm · nhóm *Novel ideas*

**Cách làm:** Idea 2 - A/B có Brier thật: generator biết xác suất huỷ thật p của từng booking; so v1 và v2 bằng Brier / log-loss so với p thật ngay khi có dự báo, không chờ nhãn sau ngày nhận phòng.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
