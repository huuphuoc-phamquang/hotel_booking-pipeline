# A2A gateway

agentgateway là điểm vào duy nhất cho các agent.

Mỗi mục dưới đây ứng với một dòng của rubric. Phần **Cách làm** mô tả giải pháp đã triển khai, đồng bộ từ
cột F của rubric. Phần **Kết quả** ghi test đã chạy, số liệu đo được hoặc ảnh chụp (`docs/images/`).

<a id="edai-2-24"></a>
## A2A Gateway

**Rubric:** edai-2 · dòng 24 · 2 điểm · nhóm *A2A Gateway (agentgateway as A2A Gateway)*

**Cần nộp (cả nhóm):** Tương tự bên trên

**Cách làm:** [Đã có] `gateway/agentgateway.yaml` có các route `/a2a/data-agent`, `/a2a/policy-agent` (chia 50/50 giữa v1 và v2), `/a2a/coordinator-agent`; `mcpAuthorization` cho phép policy-agent dùng `propose_overbooking` và `apply_overbooking`. [Cần làm] để coordinator gọi agent con qua gateway (kagent v1alpha2 hiện chỉ tham chiếu agent trong cluster); chụp log gateway.

**Kết quả:** A2A từ bên ngoài đã đi qua gateway; coordinator gọi agent con vẫn đi thẳng trong cluster. Route
`/a2a/data-agent`, `/a2a/policy-agent`, `/a2a/coordinator-agent` trong
[`gateway/agentgateway.yaml`](../../edai2/gateway/agentgateway.yaml) có policy `a2a` (gateway nhận diện lưu lượng A2A),
`jwtAuth` strict và `urlRewrite` về `/` của pod agent; `/a2a/policy-agent` hiện trỏ 100% về policy-agent vì chưa có
policy-agent-v2. Kiểm ngày 2026-11-19 bằng [`gateway/check.sh`](../../edai2/gateway/check.sh): agent card của cả ba agent
trả 401 khi không có token, 200 với token client `coordinator-agent`. Gửi `message/send` tới `/a2a/coordinator-agent/`
kèm token đó, coordinator giao việc cho data-agent và policy-agent rồi trả lời đủ số liệu (task `completed`, 17,9 s).
Phần còn thiếu: kagent v1alpha2 chỉ tham chiếu agent con theo tên trong cluster, nên lời gọi coordinator → agent con
chưa qua gateway.

![Kiểm security & policy của agentgateway](../images/edai-2/agentgateway-check.png)
