# Global model config

Một ModelConfig dùng chung cho mọi agent.

Mỗi mục dưới đây ứng với một dòng của rubric. Phần **Cách làm** mô tả giải pháp đã triển khai, đồng bộ từ
cột F của rubric. Phần **Kết quả** ghi test đã chạy, số liệu đo được hoặc ảnh chụp (`docs/images/`).

<a id="edai-2-7"></a>
## Deploy 1 global model config để các Agent có thể dùng follow tutorial này, config này sẽ…

**Rubric:** edai-2 · dòng 7 · 2 điểm · nhóm *Deploy 1 global model config để các Agent có thể dùng follow tutorial này, config này sẽ link tới inference platform ở trên thông qua cái agent gateway đề cập ở trên nốt*

**Cần nộp (cả nhóm):** Document thể hiện link tới code config và giải thích đã config gì

**Cách làm:** [Đã có] ModelConfig `default-model-config` trỏ tới `/v1` của agentgateway (`agents/agents.yaml`). [Cần làm] dẫn link tới file trong docs và giải thích.

**Kết quả:** đã có ModelConfig dùng chung trên cluster thứ hai ngày 2026-11-19, nhưng chưa đi qua agentgateway.
kagent 0.9.12 cài bằng Helm với [`k8s/kagent-values.yaml`](../../edai2/k8s/kagent-values.yaml): provider `openAI`
sinh ModelConfig `default-model-config` với model `qwen-3b` (vLLM, Qwen2.5-3B-Instruct, parser tool `hermes`), khoá
lấy từ Secret `llm-api` (giá trị gốc ở Vault `secret/agents/llm`), `baseUrl` truyền lúc cài. Cả ba agent trong
[`agents/agents-direct.yaml`](../../edai2/agents/agents-direct.yaml) dùng chung ModelConfig này. vLLM chạy trên máy
cá nhân (GPU 8 GB, `--max-model-len 4096`) và được đưa ra ngoài qua Cloudflare tunnel; gọi không khoá trả 401, có
khoá trả 200. Phần còn thiếu: `baseUrl` trỏ `/v1` của agentgateway như bản đích ở `agents/agents.yaml`.
