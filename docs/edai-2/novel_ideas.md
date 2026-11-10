# Novel ideas (edai-2 & final)

Mỗi ý tưởng: vấn đề, cách làm, bằng chứng đã chạy.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-2-56"></a>
## Idea 1 (edai-2): Regret so với giá tối ưu thật P*

**Rubric:** edai-2 · dòng 56 · 2 điểm · nhóm *Novel ideas*

**Cần nộp (cả nhóm):** Document idea + proof it worked!

**Cách làm:** Idea 1 - Regret so với giá tối ưu thật P*: so giá cố định / giá policy lịch sử / model ngây thơ (β lệch về 0 do confounding) / XGBoost cả đường cầu / GLM có kiểm soát policy_price (prototype: 15,3% / 12,7% / 37,1% / 32,6% / 0,1%). Proof: bảng regret + assert optimizer lưới ~ nghiệm KKT beta/(beta-1)*(c + lambda), c = chi phí biên, lambda = giá bóng của phòng; IPS (propensity 1/5) để đánh giá off-policy. Thêm nếu còn thời gian: overbooking regret (K model vs K thật từ hàm huỷ của generator).

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-57"></a>
## Idea 2 (edai-2): Định giá công bằng có kiểm chứng + HITL

**Rubric:** edai-2 · dòng 57 · 2 điểm · nhóm *Novel ideas*

**Cách làm:** Idea 2 - Định giá công bằng có kiểm chứng + HITL: quote_price không nhận customer_id; model huỷ trong công thức giá ở cấp ô giá (cancel-segment); property test đổi customer_id giá và rate fence không đổi; đổi giá > 15% hoặc số phòng bán vượt quá ngưỡng đi qua tool propose_price_change có requireApproval (kagent HITL: Approve/Reject trên UI). Proof: test trong CI + trace phê duyệt; đối chiếu Luật 91/2025.

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

**Cách làm:** Idea 2 - A/B có doanh thu thật: so dashboard proxy (giá, guardrail, drift) với doanh thu thật generator tính cho từng version trên cùng ô.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
