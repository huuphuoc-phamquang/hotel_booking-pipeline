# A/B testing

A/B testing cho agent, LLM và model inference.

Mỗi mục dưới đây ứng với một dòng của rubric. Phần **Cách làm** mô tả giải pháp đã triển khai, đồng bộ từ
cột F của rubric. Phần **Kết quả** ghi test đã chạy, số liệu đo được hoặc ảnh chụp (`docs/images/`).

<a id="edai-2-52"></a>
## Perform A/B test for agents with different model config and monitor them

policy-agent có hai bản chạy song song trong [`agents/agents-gke.yaml`](../../edai2/agents/agents-gke.yaml):

| | policy-agent (v1) | policy-agent-v2 |
|---|---|---|
| ModelConfig | `default-model-config` → `/v1` của gateway (90/10 qwen-3b / LoRA) | `model-config-v2` → `/llm-v2/v1`, chỉ adapter `qwen-booking-v2` |
| Prompt | trả lời ngắn gọn | tối đa 3 câu, câu cuối ghi nguồn (tool, chunk_id) |
| Tool, HITL | 4 tool, `apply_overbooking` cần duyệt | giống v1 |

agentgateway chia route `/a2a/policy-agent` 50/50 giữa hai bản; `/a2a/policy-agent-v2` gọi thẳng v2
([`gateway/agentgateway.yaml`](../../edai2/gateway/agentgateway.yaml)). Metric của gateway
(`agentgateway_requests_total`, `request_duration_seconds`, `gen_ai_client_token_usage`, nhãn `backend` và
`gen_ai_request_model`) được Prometheus scrape qua ServiceMonitor; dashboard Grafana `agent-ab`
([`observability/dashboards/agent-ab.json`](../../edai2/observability/dashboards/agent-ab.json)) so sánh số request, tỉ lệ
lỗi, latency p50/p95 theo bản, token và thời gian gọi LLM theo model.

[`tests/ab_agent.py`](../../edai2/tests/ab_agent.py) gửi 20 câu hỏi (xác suất huỷ, chính sách, bán vượt) qua
`/a2a/policy-agent/` ngày 2026-11-19 và ghi bản trả lời theo `kagent_app_name`:

| Bản | Lượt | p50 | max | completed | tool lỗi | token output TB |
|---|---|---|---|---|---|---|
| policy-agent (v1) | 13 | 4,5 s | 13,7 s | 13 | 0 | 85 |
| policy-agent-v2 | 7 | 5,7 s | 17,5 s | 7 | 0 | 49 |

v2 trả lời ngắn hơn đúng như prompt (token output thấp hơn khoảng 42%) nhưng chậm hơn, vì adapter LoRA thêm chi phí
trên cùng vLLM (dashboard: thời gian gọi LLM p50 của `qwen-booking-v2` cao hơn `qwen-3b`). Mẫu 20 lượt còn nhỏ và tỉ
lệ chia thực tế là 13/7, nên kết quả chỉ mang tính định hướng; chưa đánh giá độ đúng nội dung câu trả lời.

![Dashboard Grafana A/B agent](../images/edai-2/grafana-agent-ab.png)


<a id="edai-2-53"></a>
## Perform A/B test for different LLM versions on the LLM inference platform

**Rubric:** edai-2 · dòng 53 · 1 điểm · nhóm *A/B Testing* › *When you deploy a new model, don't replace the old one directly, you should do A/B test, monitor it, and deploy.*

**Cách làm:** [Đã có] agentgateway chia trọng số 90/10 giữa qwen v1 và v2; dashboard `observability/dashboards/llm-agents.json` hiển thị token, TTFT, round-trip theo model. [Cần làm] chia traffic 90/10 qua agentgateway trên GKE khi có GPU (đã A/B offline v1 và v1b trên vLLM laptop).

**Kết quả:** A/B **offline** giữa hai phiên bản LLM, chạy ngày 2026-11-19 trên vLLM 0.9.2 ở laptop GPU (chưa có
agentgateway và GPU trên GKE, nên chưa chia traffic 90/10 và chưa có dashboard theo model). Một vLLM phục vụ cùng lúc
Qwen2.5-1.5B gốc và hai adapter LoRA: `qwen-booking-v1` (fine-tune với 400 hội thoại tính K + 29 câu chính sách và PII,
2 epoch) và `qwen-booking-v1b` (60 hội thoại K, 4 epoch). Cả ba trả lời cùng 6 câu hỏi, temperature 0; đáp án K đối chiếu
với `overbooking.limit`, chính sách đối chiếu với `policies/*.md`.

| Nhóm câu hỏi | base | v1 | v1b |
|---|---|---|---|
| Tính K (2 câu, đáp án 5 và 3) | 0/2 | 1/2 | 0/2 |
| Chính sách huỷ, đổi ngày (2 câu) | 0/2 | 0/2 | 0/2 |
| Từ chối dữ liệu PII: số thẻ, CCCD (2 câu) | 2/2 | 0/2 | 1/2 |

Quyết định: giữ v1, không promote v1b (kém hơn v1 ở phần tính K). Cả hai bản fine-tune đều bịa chính sách và kém base ở
phần từ chối PII: model 1,5B học khuôn câu trả lời chứ không học phép tính hay dữ kiện. Vì vậy K lấy từ tool
`propose_overbooking`, chính sách lấy qua RAG (`search_policy`), PII chặn ở lớp ngoài (`llm_metrics.py`); fine-tune chỉ
nên dùng để dạy cách gọi tool và giọng trả lời.

Sau đó, chia traffic online đã chạy qua agentgateway (route `/v1` trong
[`gateway/agentgateway.yaml`](../../edai2/gateway/agentgateway.yaml)): weight 90 tới model gốc `qwen-3b`, weight 10 tới
adapter `qwen-booking-v2`, cùng một vLLM (Qwen2.5-3B). Ngày 2026-11-19, 13 request LLM hợp lệ của agent qua
gateway chia thành 12 tới `qwen-3b` và 1 tới `qwen-booking-v2` (trường `gen_ai.request.model` trong log
gateway, ảnh ở `global_model_config.md`); mẫu còn nhỏ nên tỉ lệ chưa phản ánh đúng 90/10. Dashboard so sánh theo model
vẫn chưa có.

![A/B offline giữa base, v1 và v1b](../images/edai-2/llm-ab-offline.png)
