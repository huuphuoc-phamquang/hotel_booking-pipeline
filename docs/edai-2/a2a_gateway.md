# A2A gateway

agentgateway làm entrypoint cho agent.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-2-24"></a>
## A2A Gateway

**Rubric:** edai-2 · dòng 24 · 2 điểm · nhóm *A2A Gateway (agentgateway as A2A Gateway)*

**Cần nộp (cả nhóm):** Tương tự bên trên

**Cách làm:** [Đã có] gateway/agentgateway.yaml: route /a2a/data-agent, /a2a/policy-agent (chia 50/50 v1/v2), /a2a/coordinator-agent; mcpAuthorization thêm propose_overbooking, apply_overbooking cho policy-agent. [Cần làm] coordinator gọi agent con qua gateway (kagent v1alpha2 chỉ tham chiếu agent trong cluster); chụp log gateway.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
