# A/B testing

A/B testing cho agent, LLM và model inference.

Mỗi mục dưới đây ứng với một dòng của rubric. Phần **Cách làm** mô tả giải pháp đã triển khai, đồng bộ từ
cột F của rubric. Phần **Kết quả** ghi test đã chạy, số liệu đo được hoặc ảnh chụp (`docs/images/`).

<a id="edai-2-52"></a>
## Perform A/B test for agents with different model config and monitor them

**Rubric:** edai-2 · dòng 52 · 1 điểm · nhóm *A/B Testing* › *When you deploy a new model, don't replace the old one directly, you should do A/B test, monitor it, and deploy.*

**Cần nộp (cả nhóm):** Document về A/B test được implement như thế nào, dashboard như thế nào

**Cách làm:** [Đã có] Trong `agents.yaml`, policy-agent-v2 dùng ModelConfig `model-config-v2` (route `/llm-v2` chỉ tới qwen-v2) và prompt riêng; agentgateway chia `/a2a/policy-agent` 50/50. [Cần làm] dashboard so sánh latency, token, tỉ lệ tool lỗi và tỉ lệ đề xuất bị từ chối.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

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

![A/B offline giữa base, v1 và v1b](../images/edai-2/llm-ab-offline.png)
