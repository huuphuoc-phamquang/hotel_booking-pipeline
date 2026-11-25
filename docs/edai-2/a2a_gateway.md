# A2A gateway

`agentgateway` là điểm vào duy nhất cho các agent theo giao thức A2A.

<a id="edai-2-24"></a>
## Cấu hình A2A Gateway

[`gateway/agentgateway.yaml`](../../edai2/gateway/agentgateway.yaml) mở các route `/a2a/*` cho cả 4 agent, áp dụng policy `a2a` và xác thực JWT (`strict`); riêng `/a2a/policy-agent` chia tải 50/50 giữa v1 và v2 cho A/B testing.

Kiểm thử bằng [`gateway/check.sh`](../../edai2/gateway/check.sh): thiếu token trả về `401`, có JWT hợp lệ trả về `200`; gửi yêu cầu tới `/a2a/coordinator-agent/` điều phối thành công `data-agent` và `policy-agent` (`completed`, 17,9 giây).

![Kiểm security & policy của agentgateway](../images/edai-2/agentgateway-check.png)

*Chú thích: Kết quả chạy `gateway/check.sh`: gọi không token hoặc token giả bị trả `401`; `data-agent` chỉ thấy `get_booking_features` và bị chặn `Unknown tool` khi gọi `predict_cancellation`; route `/a2a` trả `200` khi có JWT.*

Để mọi lời gọi nội bộ từ `coordinator-agent` tới `data-agent` và `policy-agent` đều đi qua `agentgateway` (thay vì gọi thẳng trong cluster), hệ thống triển khai cầu nối [`a2a-bridge`](../../edai2/gateway/a2a_bridge.py) với 2 tool `delegate_data_agent` và `delegate_policy_agent` sau route `/mcp-a2a` (xác thực JWT và quyền `jwt.role == "coordinator-agent"`).

Luồng điều phối đi theo chuỗi: `coordinator-agent` → `agentgateway (/mcp-a2a)` → `a2a-bridge` → `agentgateway (/a2a/<agent>/)` → sub-agent đích, giữ nguyên `trace.id` xuyên suốt trên Jaeger và trả về `HTTP 200`.

![Luồng điều phối A2A từ coordinator-agent qua agentgateway trên Jaeger](../images/edai-2/a2a-coordinator-via-gateway.png)

*Chú thích: Trace phân tán trên Jaeger chứng minh lời gọi A2A đi vòng đúng qua gateway: `coordinator-agent` → `agentgateway (/mcp-a2a)` → `a2a-bridge` → `agentgateway (/a2a/*)` → sub-agent (`HTTP 200`, giữ nguyên `trace.id`).*
