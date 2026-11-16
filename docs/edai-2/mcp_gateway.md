# MCP gateway

agentgateway là điểm vào duy nhất cho MCP server.

Mỗi mục dưới đây ứng với một dòng của rubric. Phần **Cách làm** mô tả giải pháp đã triển khai, đồng bộ từ
cột F của rubric. Phần **Kết quả** ghi test đã chạy, số liệu đo được hoặc ảnh chụp (`docs/images/`).

<a id="edai-2-23"></a>
## MCP Gateway

**Rubric:** edai-2 · dòng 23 · 2 điểm · nhóm *MCP Gateway (agentgateway as MCP Gateway)*

**Cần nộp (cả nhóm):** Document phải show được setup agentgateway để làm MCP Gateway, show được các thiết lập về security và policy kèm giải thích tại sao dùng cái đó + link tới YAML chứa các setting

**Cách làm:** [Đã có] Route `/mcp` đi qua gateway, xác thực JWT, `mcpAuthorization` theo tool và role; `RemoteMCPServer` trỏ tới gateway thay vì gọi thẳng MCP.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._
