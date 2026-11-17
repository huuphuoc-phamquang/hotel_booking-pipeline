# Agent thứ hai: policy-agent

Agent thứ hai dùng tool ML (`predict_cancellation`: Feast online + KServe) và tool RAG (`search_policy`).

Mỗi mục dưới đây ứng với một dòng của rubric. Phần **Cách làm** mô tả giải pháp đã triển khai, đồng bộ từ
cột F của rubric. Phần **Kết quả** ghi test đã chạy, số liệu đo được hoặc ảnh chụp (`docs/images/`).

<a id="edai-2-22"></a>
## Làm tương tự, thêm 1 Agent nhận dữ liệu từ Online Feature Store, và có 2 tools:

**Rubric:** edai-2 · dòng 22 · 8 điểm · nhóm *Làm tương tự, thêm 1 Agent nhận dữ liệu từ Online Feature Store, và có 2 tools:*

**Cần nộp (cả nhóm):** Document tương tự bên trên

**Cách làm:** [Đã có] policy-agent có bốn tool: `predict_cancellation` (ML, Feast online + KServe), `search_policy` (RAG), `propose_overbooking` (K tính từ `gold.booking_risk`, so với số phòng trong `gold.hotel_rooms`) và `apply_overbooking` (ghi K, cần `requireApproval` - Idea 2). [Cần làm] multi-replica, KEDA, Agent Substrate (sandbox), registry; chụp UI chat.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._
