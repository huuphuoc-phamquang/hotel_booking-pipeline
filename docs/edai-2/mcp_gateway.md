# MCP gateway

agentgateway làm entrypoint cho MCP server.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-2-23"></a>
## MCP Gateway

**Rubric:** edai-2 · dòng 23 · 2 điểm · nhóm *MCP Gateway (agentgateway as MCP Gateway)*

**Cần nộp (cả nhóm):** Document phải show được setup agentgateway để làm MCP Gateway, show được các thiết lập về security và policy kèm giải thích tại sao dùng cái đó + link tới YAML chứa các setting

**Cách làm:** [Đã có] route /mcp qua gateway, JWT, mcpAuthorization theo tool + role (RemoteMCPServer trỏ gateway, không trỏ thẳng MCP). [Pricing] thêm rule cho tool pricing.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
