# Agent registry

Registry lưu agent card và MCP server.

<a id="edai-2-8"></a>
## Triển khai agentregistry

agentregistry v0.4.0 namespace `agentregistry`. Registry dùng Postgres sẵn có của data platform (database `agentregistry`, extension pgvector)
thay cho Postgres bundled để không thêm pod; chuỗi kết nối nằm trong Secret `agentregistry-db`. Một pod phục vụ cả
web UI, REST API (`/v0/...`, tài liệu ở `/docs`) và MCP endpoint của registry; UI ra ngoài qua Ingress có basic auth.

Catalog hiện có 4 agent (`coordinator-agent`, `data-agent`, `policy-agent`, `policy-agent-v2`) và 1 MCP server `booking-tools`, gắn tag theo phiên bản commit đang deploy. Mỗi mục lưu đủ thông tin từ A2A agent card: mô tả, model, MCP server, repository và địa chỉ A2A qua `agentgateway`.

![agentregistry: catalog 4 agent](../images/edai-2/registry-agents.png)

![agentregistry: chi tiết policy-agent](../images/edai-2/registry-agent-detail.png)

*Chú thích: Trang chi tiết của `policy-agent` trên `agentregistry`: liệt kê đầy đủ A2A Agent Card, model sử dụng, địa chỉ gateway và MCP server `booking-tools`.*
