# Agent thứ hai: pricing-agent

Agent có tool ML và RAG.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-2-22"></a>
## Làm tương tự, thêm 1 Agent nhận dữ liệu từ Online Feature Store, và có 2 tools:

**Rubric:** edai-2 · dòng 22 · 8 điểm · nhóm *Làm tương tự, thêm 1 Agent nhận dữ liệu từ Online Feature Store, và có 2 tools:*

**Cần nộp (cả nhóm):** Document tương tự bên trên

**Cách làm:** [Đã có] policy-agent: predict_cancellation (ML) + search_policy (RAG). [Pricing] pricing-agent thay policy-agent: quote_price / explain_price / overbooking_limit (ML) + search_policy (RAG) + propose_price_change (requireApproval); bỏ quyết định cọc theo khách; làm đủ multi-replica, KEDA, Agent Substrate (sandbox), registry, chụp UI chat.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
