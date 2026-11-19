# Global model config

Một ModelConfig dùng chung cho mọi agent.

Mỗi mục ứng với một dòng của rubric, ghi lại phần đã triển khai và kết quả (số liệu đo được, ảnh chụp trong
`docs/images/`).

<a id="edai-2-7"></a>
## Deploy 1 global model config để các Agent có thể dùng follow tutorial này, config này sẽ…

kagent 0.9.12 cài bằng Helm với [`k8s/kagent-values.yaml`](../../edai2/k8s/kagent-values.yaml) trên cluster thứ hai
ngày 2026-11-19. Provider `openAI` của chart sinh ModelConfig `default-model-config`:

- `model: qwen-3b`: Qwen2.5-3B-Instruct phục vụ bằng vLLM, parser tool `hermes`.
- `baseUrl: http://agentgateway.gateway.svc.cluster.local:3000/v1`: route LLM của agentgateway, không gọi thẳng vLLM.
- `apiKeySecretRef: llm-api`: Secret chứa JWT của client `kagent` do Keycloak cấp (tạo bằng `gateway/deploy.sh`);
  kagent gửi nó dưới dạng `Authorization: Bearer`. Khoá vLLM chỉ nằm ở gateway.

Cả ba agent trong [`agents/agents-gke.yaml`](../../edai2/agents/agents-gke.yaml) dùng chung ModelConfig này. Gateway
chia lưu lượng 90/10 giữa model gốc `qwen-3b` và adapter LoRA `qwen-booking-v2`
([`gateway/agentgateway.yaml`](../../edai2/gateway/agentgateway.yaml)), nên đổi model hay tỉ lệ chỉ cần sửa gateway,
không sửa agent. Từ khi chuyển kagent sang gateway tới lúc chụp (các lượt hỏi data-agent, policy-agent,
coordinator-agent và các lần chạy `gateway/check.sh`), log route `llm` ghi 13 request trả 200, cùng `jwt.sub` của
client `kagent` (12 tới `qwen-3b`, 1 tới `qwen-booking-v2`), và 6 request không token hoặc token giả mạo trả 401.

vLLM chạy trên máy GPU cá nhân (8 GB, `--max-model-len 4096`) và được đưa ra ngoài qua Cloudflare tunnel; URL tunnel
đổi mỗi lần khởi động lại, khi đó chỉ cần chạy lại `gateway/deploy.sh`.

![Log agentgateway: request LLM có JWT, chia 90/10 theo model](../images/edai-2/agentgateway-llm-log.png)
