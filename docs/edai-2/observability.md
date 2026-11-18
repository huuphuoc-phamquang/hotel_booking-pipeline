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

**Cách làm:** [Đã có] `observability/stack/kube-prometheus-stack.yaml` thu CPU, RAM, disk, network theo node và pod (node-exporter, kube-state-metrics); Grafana truy cập qua ingress `grafana.booking.local`. Đã chạy trên GKE (2026-11-18), ảnh dashboard cluster, namespace, node trong docs.

**Kết quả:** cài trên GKE ngày 2026-11-18 vào namespace `monitoring`: `kube-prometheus-stack` 93.4.0 (`observability/stack/kube-prometheus-stack.yaml`, PVC Prometheus dùng storage class `standard`), Pushgateway, Jaeger (`stack/jaeger.yaml`), Elasticsearch và Kibana 8.5.1, Fluent Bit 0.58.3 (`stack/efk.yaml`). Grafana đọc mật khẩu admin từ Secret `grafana-admin`, các dashboard
có sẵn của chart (node-exporter, kube-state-metrics) hiện CPU, RAM, disk, network theo cluster, node và pod. Ảnh chụp
lúc job Spark 105 GiB chạy: namespace `data` dùng khoảng 38 core và 128 GiB RAM, mỗi executor Spark khoảng 6 core.

![Grafana: toàn cluster](../images/edai-2/grafana-cluster.png)

![Grafana: namespace data theo pod](../images/edai-2/grafana-namespace-data.png)

![Grafana: một node (Node Exporter)](../images/edai-2/grafana-node.png)

<a id="edai-2-48"></a>
## Tương tự cho logs · edai-2 · Observability

**Rubric:** edai-2 · dòng 48 · 1 điểm · nhóm *Observability* › *Computing telemetry data (such as CPU, RAM, disk, network, etc.)*

**Cách làm:** [Đã có] `observability/stack/efk.yaml` (Fluent Bit → Elasticsearch → Kibana), Kibana truy cập qua ingress. Đã chạy trên GKE (2026-11-18): Fluent Bit → index `booking-*`, ảnh Kibana trong docs.

**Kết quả:** cài trên GKE ngày 2026-11-18 vào namespace `monitoring`: `kube-prometheus-stack` 93.4.0 (`observability/stack/kube-prometheus-stack.yaml`, PVC Prometheus dùng storage class `standard`), Pushgateway, Jaeger (`stack/jaeger.yaml`), Elasticsearch và Kibana 8.5.1, Fluent Bit 0.58.3 (`stack/efk.yaml`). Fluent Bit (DaemonSet, 1 pod mỗi node) đọc log container, gắn metadata
pod/namespace, bỏ log của `kube-system` và `monitoring`, đẩy vào index `booking-YYYY.MM.DD`. Kibana (data view
`booking-*`) nhận khoảng 48 nghìn dòng log trong 15 phút; lọc KQL theo pod task Airflow DP2 ra đúng log của
`silver_bookings`, `stage_gold`, `upsert_gold`. Chart Kibana 8.5.1 bật `csp.strict` làm một số trình duyệt bị chặn,
nên đặt `csp.strict: false`.

![Kibana Discover](../images/edai-2/kibana-discover.png)

![Kibana lọc log task DP2](../images/edai-2/kibana-filter-airflow.png)

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
