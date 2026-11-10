# A2A gateway

agentgateway làm entrypoint cho agent.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-2-24"></a>
## A2A Gateway

**Rubric:** edai-2 · dòng 24 · 2 điểm · nhóm *A2A Gateway (agentgateway as A2A Gateway)*

**Cần nộp (cả nhóm):** Tương tự bên trên

**Cách làm:** [Một phần] A2A mới có route /a2a/data-agent. [Cần làm] thêm route /a2a/pricing-agent (thay policy-agent); coordinator gọi agent con qua gateway thay vì gọi thẳng (sơ đồ: B4 coord -> gateway, B5/B6 gateway -> pricing/data); chụp log gateway thấy request A2A.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
