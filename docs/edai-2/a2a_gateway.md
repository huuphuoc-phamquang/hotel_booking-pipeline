# A2A gateway

agentgateway là điểm vào duy nhất cho các agent.

Mỗi mục dưới đây ứng với một dòng của rubric. Phần **Cách làm** mô tả giải pháp đã triển khai, đồng bộ từ
cột F của rubric. Phần **Kết quả** ghi test đã chạy, số liệu đo được hoặc ảnh chụp (`docs/images/`).

<a id="edai-2-24"></a>
## A2A Gateway

**Rubric:** edai-2 · dòng 24 · 2 điểm · nhóm *A2A Gateway (agentgateway as A2A Gateway)*

**Cần nộp (cả nhóm):** Tương tự bên trên

**Cách làm:** [Đã có] `gateway/agentgateway.yaml` có các route `/a2a/data-agent`, `/a2a/policy-agent` (chia 50/50 giữa v1 và v2), `/a2a/coordinator-agent`; `mcpAuthorization` cho phép policy-agent dùng `propose_overbooking` và `apply_overbooking`. [Cần làm] để coordinator gọi agent con qua gateway (kagent v1alpha2 hiện chỉ tham chiếu agent trong cluster); chụp log gateway.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._
