# Observability

Metric của Web API, telemetry hệ thống, log, trace, telemetry cho LLM và agent, kiểm tra drift theo lịch.

Mỗi mục dưới đây ứng với một dòng của rubric. Phần **Cách làm** mô tả giải pháp đã triển khai, đồng bộ từ
cột F của rubric. Phần **Kết quả** ghi test đã chạy, số liệu đo được hoặc ảnh chụp (`docs/images/`).

<a id="edai-2-46"></a>
## Web API monitoring metrics such as req/s, num of reqs, num of failures, etc.

**Rubric:** edai-2 · dòng 46 · 1 điểm · nhóm *Observability* › *Web API metrics*

**Cần nộp (cả nhóm):** Document show được các telemetry

**Cách làm:** [Đã có] booking-mcp dùng `prometheus-fastapi-instrumentator` (req/s, số request, lỗi) cùng các metric `mcp_tool_calls`, `mcp_tool_failures`; dashboard `observability/dashboards/booking-apis.json`. [Cần làm] chụp dashboard.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-2-47"></a>
## Collect và visualize metrics với Prometheus + Grafana · edai-2 · Observability

**Rubric:** edai-2 · dòng 47 · 1 điểm · nhóm *Observability* › *Computing telemetry data (such as CPU, RAM, disk, network, etc.)*

> Collect và visualize metrics với Prometheus + Grafana (hoặc tool tương tự)

**Cách làm:** [Đã có] `observability/stack/kube-prometheus-stack.yaml` thu CPU, RAM, disk, network theo node và pod (node-exporter, kube-state-metrics); Grafana truy cập qua ingress `grafana.booking.local`. [Cần làm] chụp dashboard.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-2-48"></a>
## Tương tự cho logs · edai-2 · Observability

**Rubric:** edai-2 · dòng 48 · 1 điểm · nhóm *Observability* › *Computing telemetry data (such as CPU, RAM, disk, network, etc.)*

**Cách làm:** [Đã có] `observability/stack/efk.yaml` (Fluent Bit → Elasticsearch → Kibana), Kibana truy cập qua ingress. [Cần làm] chụp.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-2-49"></a>
## Tương tự cho traces · edai-2 · Observability

**Rubric:** edai-2 · dòng 49 · 1 điểm · nhóm *Observability* › *Computing telemetry data (such as CPU, RAM, disk, network, etc.)*

**Cách làm:** [Đã có] `observability/stack/jaeger.yaml` nhận OTLP gRPC cổng 4317, UI qua ingress; booking-mcp gửi trace (FastAPI, httpx tới KServe, span đọc Feast). [Cần làm] tracing cho agentgateway; chụp một trace A2A → MCP → KServe.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-2-50"></a>
## Đảm bảo ít nhất các metrics · LLM-related telemetry data

**Rubric:** edai-2 · dòng 50 · 2 điểm · nhóm *Observability* › *LLM-related telemetry data*

> Đảm bảo ít nhất các metrics + token metrics (count of input tokens, output tokens and total tokens per req) + total round-trip time for a generation + TTFT + Frequencies of prompts caught by safety of PII

**Cách làm:** [Đã có] `llm_metrics.py` đo token vào, ra, tổng, thời gian round-trip, TTFT và số lần chặn PII. Số thẻ chỉ bị coi là PII khi qua kiểm Luhn và không đứng sau `BK-`. `tests/test_llm_metrics.py` (11 test, coverage 100%) xác nhận `BK-<id>` không bị chặn, còn `4111 1111 1111 1111` bị chặn.

**Kết quả:** các test `edai2/tests/test_llm_metrics.py` chạy cục bộ và đạt (2026-11-16). Chưa có ảnh chụp trên cluster.

<a id="edai-2-51"></a>
## Đảm bảo ít nhất các metrics · Agent-related telemetry data

**Rubric:** edai-2 · dòng 51 · 2 điểm · nhóm *Observability* › *Agent-related telemetry data*

> Đảm bảo ít nhất các metrics + total num of times each agent is called + total num of times each MCP tool is called + total failures cho mỗi lượt call tool

**Cách làm:** [Đã có] Các metric `agent_calls_total`, `mcp_tool_calls_total`, `mcp_tool_failures_total` cùng dashboard `observability/dashboards/llm-agents.json` (có request A2A theo route qua agentgateway). [Cần làm] chụp dashboard.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._
