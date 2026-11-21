# Coordinator agent

Coordinator điều phối các agent con; tài liệu gồm số replica, autoscale và registry.

<a id="edai-2-25"></a>
## Triển khai Coordinator Agent với multi-replica và auto-scale

coordinator-agent ([`agents/agents-gke.yaml`](../../edai2/agents/agents-gke.yaml)) có hai tool kiểu `Agent` là
data-agent và policy-agent. Với câu hỏi gồm số liệu của khách 18766768 tại khách sạn 8528 và xác suất huỷ của booking
90000919211, coordinator tách thành hai yêu cầu, giao cho từng agent con rồi tổng hợp: khách có 1 booking 90 ngày,
tỉ lệ huỷ 0%, lead time trung bình 6 ngày; booking có xác suất huỷ 13,14% (model v1). Coordinator đã có trên
agentregistry (dòng 26, ảnh catalog bên dưới).

Coordinator chạy 2 replica và autoscale 2–4 bằng KEDA ScaledObject `coordinator-agent` trong
[`k8s/keda.yaml`](../../edai2/k8s/keda.yaml), với hai trigger: request/giây của route `/a2a/coordinator-agent` trên
agentgateway (ngưỡng 1) và CPU 60%; KEDA lấy số replica lớn hơn của hai trigger. Agent không đặt
`deployment.replicas` để kagent không ghi đè replica do KEDA chọn. Phép thử tải và scale chạy trên data-agent với
cùng cơ chế (dòng 19: 2 → 4 replica khi vượt ngưỡng, về 2 sau 5 phút).

![kagent UI: coordinator-agent gọi data-agent và policy-agent](../images/edai-2/kagent-coordinator.png)

![agentregistry: catalog có coordinator-agent](../images/edai-2/registry-agents.png)

![KEDA scale data-agent 2 → 4 replica](../images/edai-2/keda-scale.png)

<a id="edai-2-26"></a>
## Đăng ký Coordinator Agent lên agentregistry

Script [`ci/publish_agent_card.py`](../../edai2/ci/publish_agent_card.py) đăng agent lên agentregistry (dòng 8):
lấy agent card A2A từ kagent controller, dựng resource `ar.dev/v1alpha1` gồm `MCPServer` `booking-tools` (route `/mcp`
của agentgateway) và `Agent` (tiêu đề, mô tả, model, MCP server, repository và commit), rồi gửi `POST /v0/apply`.
Tag là commit đang deploy, nên mỗi lần deploy để lại một phiên bản; apply lại cùng tag thì cập nhật. Card lấy từ
controller chứ không qua `/a2a/policy-agent` của gateway, vì route đó chia 50/50 và có lúc trả card của v2; script
dừng nếu tên trong card không khớp agent. Stage `Deploy agents` của [`ci/Jenkinsfile`](../../edai2/ci/Jenkinsfile)
gọi script này cho cả 4 agent sau khi rollout.

Script được chạy từ máy của nhóm (port-forward tới controller và registry) với tag `f808e37`:
`coordinator-agent` cùng hai agent con và `policy-agent-v2` có trên registry kèm MCP server `booking-tools`. Stage Jenkins chưa chạy vì tham số `WITH_AGENTS` còn tắt.

![agentregistry: catalog 4 agent](../images/edai-2/registry-agents.png)
