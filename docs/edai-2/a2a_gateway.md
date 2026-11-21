# A2A gateway

`agentgateway` là điểm vào duy nhất cho các agent theo giao thức A2A.

<a id="edai-2-24"></a>
## Cấu hình A2A Gateway

Các route `/a2a/data-agent`, `/a2a/policy-agent`, `/a2a/policy-agent-v2` và `/a2a/coordinator-agent` trong [`gateway/agentgateway.yaml`](../../edai2/gateway/agentgateway.yaml) được cấu hình với policy `a2a` (nhận diện lưu lượng A2A), `jwtAuth` (`mode: strict`) và `urlRewrite` về `/` của từng pod agent. Riêng `/a2a/policy-agent` chia tải 50/50 giữa `policy-agent` (v1) và `policy-agent-v2` để phục vụ A/B testing, còn `/a2a/policy-agent-v2` gọi thẳng bản v2.

Kiểm thử bằng [`gateway/check.sh`](../../edai2/gateway/check.sh): agent card của cả 3 agent trả về `401` khi thiếu token và `200` khi dùng token của client `coordinator-agent`. Khi gửi `message/send` tới `/a2a/coordinator-agent/` kèm JWT, coordinator điều phối thành công `data-agent` và `policy-agent` để trả về đủ số liệu (`completed`, 17,9 giây).

![Kiểm security & policy của agentgateway](../images/edai-2/agentgateway-check.png)

**[update sau]:** Hiện tại luồng gọi từ bên ngoài vào các agent đã đi qua `agentgateway`, nhưng lời gọi nội bộ từ `coordinator-agent` tới các agent con vẫn đi thẳng trong cluster do `kagent v1alpha2` chỉ tham chiếu agent con theo tên Kubernetes. Hướng tiếp theo là cấu hình để lời gọi A2A giữa các agent cũng định tuyến qua `agentgateway` nhằm tập trung telemetry và kiểm soát quyền.
