# MCP gateway

`agentgateway` là điểm vào duy nhất cho MCP server.

<a id="edai-2-23"></a>
## Cấu hình MCP Gateway

Route `/mcp` (cấu hình trong [`gateway/agentgateway.yaml`](../../edai2/gateway/agentgateway.yaml)) đặt MCP server `booking-tools` phía sau `agentgateway` v1.6.0. Các agent trong [`agents/agents-gke.yaml`](../../edai2/agents/agents-gke.yaml) không gọi thẳng `booking-mcp` mà đi qua gateway kèm JWT riêng của từng agent.

Gateway áp dụng hai lớp bảo vệ (chi tiết policy xem trong `gateway/agentgateway.yaml`):

- **Xác thực (`jwtAuth`):** bắt buộc có JWT hợp lệ do Keycloak ký; request thiếu token bị chặn ngay tại gateway.
- **Phân quyền tool (`mcpAuthorization`):** áp dụng nguyên tắc quyền tối thiểu theo `role` trong token — `data-agent` chỉ dùng được `get_booking_features`, còn `policy-agent` dùng 4 tool còn lại (bao gồm `apply_overbooking` có bước duyệt HITL).

Kiểm bằng [`gateway/check.sh`](../../edai2/gateway/check.sh): `/mcp` không token
trả 401; `tools/list` với token data-agent chỉ có `get_booking_features`, với token policy-agent có bốn tool còn lại;
data-agent gọi thẳng `predict_cancellation` bị gateway từ chối (`Unknown tool: predict_cancellation`). Qua kagent, data-agent
và policy-agent vẫn gọi tool bình thường qua gateway, log ghi `mcp.method.name=tools/call` kèm `jwt.sub` của từng agent.

![Kiểm security & policy của agentgateway](../images/edai-2/agentgateway-check.png)

*Chú thích: Kết quả chạy `gateway/check.sh`: gọi không token hoặc token giả bị trả `401`; `data-agent` chỉ thấy `get_booking_features` và bị chặn `Unknown tool` khi gọi `predict_cancellation`; route `/a2a` trả `200` khi có JWT.*
