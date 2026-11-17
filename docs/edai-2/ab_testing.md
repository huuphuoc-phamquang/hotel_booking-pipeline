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

**Cách làm:** [Đã có] agentgateway chia trọng số 90/10 giữa qwen v1 và v2; dashboard `observability/dashboards/llm-agents.json` hiển thị token, TTFT, round-trip theo model. [Cần làm] chụp dashboard.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._
