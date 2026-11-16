# Agent thứ hai: policy-agent

Agent có tool ML (`predict_cancellation` qua risk-api) và RAG (`search_policy`).

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-2-22"></a>
## Làm tương tự, thêm 1 Agent nhận dữ liệu từ Online Feature Store, và có 2 tools:

**Rubric:** edai-2 · dòng 22 · 8 điểm · nhóm *Làm tương tự, thêm 1 Agent nhận dữ liệu từ Online Feature Store, và có 2 tools:*

**Cần nộp (cả nhóm):** Document tương tự bên trên

**Cách làm:** [Đã có] policy-agent: predict_cancellation (ML, qua risk-api), search_policy (RAG), propose_overbooking (K từ gold.booking_risk, so với số phòng gold.hotel_rooms) và apply_overbooking (ghi K, requireApproval - Idea 2). [Cần làm] multi-replica, KEDA, Agent Substrate (sandbox), registry, chụp UI chat.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
