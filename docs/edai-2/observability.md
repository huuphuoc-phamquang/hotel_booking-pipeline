# Observability

Metric Web API, telemetry hệ thống, log, trace, LLM/agent, drift theo lịch.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-2-46"></a>
## Web API monitoring metrics such as req/s, num of reqs, num of failures, etc.

**Rubric:** edai-2 · dòng 46 · 1 điểm · nhóm *Observability* › *Web API metrics*

**Cần nộp (cả nhóm):** Document show được các telemetry

**Cách làm:** [Thiết kế] prometheus-fastapi-instrumentator cho booking-mcp (req/s, số req, số lỗi) + dashboard Grafana. [Cần làm] chụp dashboard.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-47"></a>
## Collect và visualize metrics với Prometheus + Grafana · edai-2 · Observability

**Rubric:** edai-2 · dòng 47 · 1 điểm · nhóm *Observability* › *Computing telemetry data (such as CPU, RAM, disk, network, etc.)*

> Collect và visualize metrics với Prometheus + Grafana (hoặc tool tương tự)

**Cách làm:** [Thiết kế] kube-prometheus-stack: CPU/RAM/disk/network theo node và pod, Grafana qua ingress. [Cần làm] chụp dashboard.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-48"></a>
## Tương tự cho logs · edai-2 · Observability

**Rubric:** edai-2 · dòng 48 · 1 điểm · nhóm *Observability* › *Computing telemetry data (such as CPU, RAM, disk, network, etc.)*

**Cách làm:** [Thiết kế] EFK (Fluent Bit -> Elasticsearch -> Kibana) thu log pod; Kibana qua ingress. [Cần làm] chụp.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-49"></a>
## Tương tự cho traces · edai-2 · Observability

**Rubric:** edai-2 · dòng 49 · 1 điểm · nhóm *Observability* › *Computing telemetry data (such as CPU, RAM, disk, network, etc.)*

**Cách làm:** [Thiết kế] OTel SDK cho booking-mcp + tracing agentgateway -> Jaeger; Jaeger qua ingress. [Cần làm] chụp 1 trace A2A -> MCP -> KServe.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-50"></a>
## Đảm bảo ít nhất các metrics · LLM-related telemetry data

**Rubric:** edai-2 · dòng 50 · 2 điểm · nhóm *Observability* › *LLM-related telemetry data*

> Đảm bảo ít nhất các metrics + token metrics (count of input tokens, output tokens and total tokens per req) + total round-trip time for a generation + TTFT + Frequencies of prompts caught by safety of PII

**Cách làm:** [Đã có] llm_metrics.py: token in/out/total, round-trip, TTFT, PII bị chặn. [Cần sửa] regex thẻ khớp nhầm booking_id 13 chữ số: chỉ chặn khi qua kiểm Luhn, hiển thị mã booking dạng BK-<id> và bỏ qua số sau BK-; test booking_id không bị chặn, thẻ test 4111... bị chặn. [Cần làm] dashboard Grafana.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-51"></a>
## Đảm bảo ít nhất các metrics · Agent-related telemetry data

**Rubric:** edai-2 · dòng 51 · 2 điểm · nhóm *Observability* › *Agent-related telemetry data*

> Đảm bảo ít nhất các metrics + total num of times each agent is called + total num of times each MCP tool is called + total failures cho mỗi lượt call tool

**Cách làm:** [Đã có] agent_calls_total, mcp_tool_calls_total, mcp_tool_failures_total. [Cần làm] dashboard; agent_calls chỉ đếm khi gọi qua chat() -> đếm ở gateway cho kagent.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

## Bổ sung final-coursework

<a id="final-46"></a>
### Web API monitoring metrics such as req/s, num

**Rubric:** final · dòng 46 · 2 điểm · nhóm *Observability* › *Web API metrics*

> Web API monitoring metrics such as req/s, num. of reqs, num. of failures, etc.

**Cần nộp (cả nhóm):** Capture màn hình thể hiện các data đã được capture, có thể coi trên các dashboard

**Cách làm:** [Thiết kế] prometheus-fastapi-instrumentator cho pricing-api và drift-api (req/s, số req, số lỗi, latency) + dashboard Grafana.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-47"></a>
### Collect và visualize metrics với Prometheus + Grafana · final · Observability

**Rubric:** final · dòng 47 · 2 điểm · nhóm *Observability* › *Computing telemetry data (such as CPU, RAM, disk, network, etc.)*

> Collect và visualize metrics với Prometheus + Grafana (hoặc tool tương tự)

**Cách làm:** [Thiết kế] kube-prometheus-stack (node-exporter, kube-state-metrics) + Grafana.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-48"></a>
### Tương tự cho logs · final · Observability

**Rubric:** final · dòng 48 · 2 điểm · nhóm *Observability* › *Computing telemetry data (such as CPU, RAM, disk, network, etc.)*

**Cách làm:** [Thiết kế] EFK: Fluent Bit -> Elasticsearch -> Kibana.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-49"></a>
### Tương tự cho traces · final · Observability

**Rubric:** final · dòng 49 · 2 điểm · nhóm *Observability* › *Computing telemetry data (such as CPU, RAM, disk, network, etc.)*

**Cách làm:** [Thiết kế] OTel SDK cho pricing-api (FastAPI + httpx instrumentation) -> Jaeger; 1 trace qua Feast + KServe.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-50"></a>
### Airflow data drift pipeline to periodically pull data from offline feature store and…

**Rubric:** final · dòng 50 · 1 điểm · nhóm *Observability* › *ML-related telemetry data*

> Airflow data drift pipeline to periodically pull data from offline feature store and compare with groundtruth and update to Grafana dashboard (via PushGateway). Assumption: we don't have groundtruth to monitor drift here!

**Cách làm:** [Thiết kế] DAG drift_monitor hằng ngày: feature 7 ngày từ offline store so với reference của model production (PSI + KS), push lên Prometheus PushGateway -> Grafana.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-51"></a>
### Trigger retrain by calling Kubeflow API

**Rubric:** final · dòng 51 · 1 điểm · nhóm *Observability* › *ML-related telemetry data*

> Trigger retrain by calling Kubeflow API (you can design by adding one step at the end of the Airflow data drift pipeline)

**Cách làm:** [Thiết kế] task cuối drift_monitor gọi KFP API (kfp.Client().create_run_from_pipeline_package) khi PSI > 0,2 ở feature quan trọng.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
