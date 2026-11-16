# Observability

Metric Web API, telemetry hệ thống, log, trace, LLM/agent, drift theo lịch.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-2-46"></a>
## Web API monitoring metrics such as req/s, num of reqs, num of failures, etc.

**Rubric:** edai-2 · dòng 46 · 1 điểm · nhóm *Observability* › *Web API metrics*

**Cần nộp (cả nhóm):** Document show được các telemetry

**Cách làm:** [Đã có] prometheus-fastapi-instrumentator cho booking-mcp (req/s, số req, lỗi) + mcp_tool_calls/failures; dashboard observability/dashboards/booking-apis.json. [Cần làm] chụp dashboard.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-47"></a>
## Collect và visualize metrics với Prometheus + Grafana · edai-2 · Observability

**Rubric:** edai-2 · dòng 47 · 1 điểm · nhóm *Observability* › *Computing telemetry data (such as CPU, RAM, disk, network, etc.)*

> Collect và visualize metrics với Prometheus + Grafana (hoặc tool tương tự)

**Cách làm:** [Đã có] observability/stack/kube-prometheus-stack.yaml: CPU/RAM/disk/network theo node và pod (node-exporter, kube-state-metrics), Grafana qua ingress grafana.booking.local. [Cần làm] chụp dashboard.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-48"></a>
## Tương tự cho logs · edai-2 · Observability

**Rubric:** edai-2 · dòng 48 · 1 điểm · nhóm *Observability* › *Computing telemetry data (such as CPU, RAM, disk, network, etc.)*

**Cách làm:** [Đã có] observability/stack/efk.yaml (Fluent Bit -> Elasticsearch -> Kibana), Kibana qua ingress. [Cần làm] chụp.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-49"></a>
## Tương tự cho traces · edai-2 · Observability

**Rubric:** edai-2 · dòng 49 · 1 điểm · nhóm *Observability* › *Computing telemetry data (such as CPU, RAM, disk, network, etc.)*

**Cách làm:** [Đã có] observability/stack/jaeger.yaml (OTLP gRPC 4317, UI qua ingress); risk-api gửi trace. [Cần làm] OTel cho booking-mcp và tracing agentgateway; chụp 1 trace A2A -> MCP -> KServe.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-50"></a>
## Đảm bảo ít nhất các metrics · LLM-related telemetry data

**Rubric:** edai-2 · dòng 50 · 2 điểm · nhóm *Observability* › *LLM-related telemetry data*

> Đảm bảo ít nhất các metrics + token metrics (count of input tokens, output tokens and total tokens per req) + total round-trip time for a generation + TTFT + Frequencies of prompts caught by safety of PII

**Cách làm:** [Đã có] llm_metrics.py: token in/out/total, round-trip, TTFT, PII bị chặn; số thẻ chỉ tính là PII khi qua Luhn và không đứng sau BK-; tests/test_llm_metrics.py (11 test, coverage 100%): BK-<id> không bị chặn, 4111 1111 1111 1111 bị chặn.

**Kết quả:** chạy cục bộ, pass (2026-11-16): `edai2/tests/test_llm_metrics.py`. _Chưa có ảnh chụp trên cluster._

<a id="edai-2-51"></a>
## Đảm bảo ít nhất các metrics · Agent-related telemetry data

**Rubric:** edai-2 · dòng 51 · 2 điểm · nhóm *Observability* › *Agent-related telemetry data*

> Đảm bảo ít nhất các metrics + total num of times each agent is called + total num of times each MCP tool is called + total failures cho mỗi lượt call tool

**Cách làm:** [Đã có] agent_calls_total, mcp_tool_calls_total, mcp_tool_failures_total + dashboard observability/dashboards/llm-agents.json (gồm request A2A theo route qua agentgateway). [Cần làm] chụp dashboard.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

## Bổ sung final-coursework

<a id="final-46"></a>
### Web API monitoring metrics such as req/s, num

**Rubric:** final · dòng 46 · 2 điểm · nhóm *Observability* › *Web API metrics*

> Web API monitoring metrics such as req/s, num. of reqs, num. of failures, etc.

**Cần nộp (cả nhóm):** Capture màn hình thể hiện các data đã được capture, có thể coi trên các dashboard

**Cách làm:** [Đã có] prometheus-fastapi-instrumentator cho risk-api, drift-api, booking-mcp (http_requests_total, http_request_duration_seconds) + ServiceMonitor trong helm/api + dashboard observability/dashboards/booking-apis.json (req/s, 5xx, p95, replica). [Cần làm] chụp dashboard.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-47"></a>
### Collect và visualize metrics với Prometheus + Grafana · final · Observability

**Rubric:** final · dòng 47 · 2 điểm · nhóm *Observability* › *Computing telemetry data (such as CPU, RAM, disk, network, etc.)*

> Collect và visualize metrics với Prometheus + Grafana (hoặc tool tương tự)

**Cách làm:** [Đã có] observability/stack/kube-prometheus-stack.yaml (node-exporter, kube-state-metrics, Grafana sidecar nạp dashboard, scrape PushGateway + queue-proxy theo revision). [Cần làm] chụp dashboard.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-48"></a>
### Tương tự cho logs · final · Observability

**Rubric:** final · dòng 48 · 2 điểm · nhóm *Observability* › *Computing telemetry data (such as CPU, RAM, disk, network, etc.)*

**Cách làm:** [Đã có] observability/stack/efk.yaml: Fluent Bit (DaemonSet) -> Elasticsearch -> Kibana, lệnh cài trong file. [Cần làm] chụp Kibana.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-49"></a>
### Tương tự cho traces · final · Observability

**Rubric:** final · dòng 49 · 2 điểm · nhóm *Observability* › *Computing telemetry data (such as CPU, RAM, disk, network, etc.)*

**Cách làm:** [Đã có] risk-api: OTel FastAPI + httpx instrumentation + span feast.online, OTLP -> Jaeger (observability/stack/jaeger.yaml), bật bằng OTEL_EXPORTER_OTLP_ENDPOINT. [Cần làm] chụp 1 trace qua Feast + KServe.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-50"></a>
### Airflow data drift pipeline to periodically pull data from offline feature store and…

**Rubric:** final · dòng 50 · 1 điểm · nhóm *Observability* › *ML-related telemetry data*

> Airflow data drift pipeline to periodically pull data from offline feature store and compare with groundtruth and update to Grafana dashboard (via PushGateway). Assumption: we don't have groundtruth to monitor drift here!

**Cách làm:** [Đã có] DAG drift_monitor hằng ngày: lead_days 7 ngày từ Gold so với reference của model production (PSI + KS, dags/drift_stats.py) và tỉ lệ huỷ dự báo so với thực tế; push PushGateway -> Grafana. [Cần làm] chụp dashboard quanh 2025-06-01.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-51"></a>
### Trigger retrain by calling Kubeflow API

**Rubric:** final · dòng 51 · 1 điểm · nhóm *Observability* › *ML-related telemetry data*

> Trigger retrain by calling Kubeflow API (you can design by adding one step at the end of the Airflow data drift pipeline)

**Cách làm:** [Đã có] task retrain của drift_monitor (short-circuit khi PSI > 0,2 hoặc lệch calibration > 0,03) ghi mốc phát hiện (Variable cancel_risk_drift_detected); khi đủ 30 ngày booking sau mốc có nhãn chín (mốc + 120 ngày, drift_stats.retrain_window, có test) mới gọi kfp.Client().create_run_from_pipeline_package với since = mốc, until = ngày chạy, nên v2 chỉ học dữ liệu sau drift; hết drift 3 ngày liên tiếp hoặc production đổi version thì xoá mốc. calib_gap chỉ tính booking do đúng version production chấm. [Cần làm] chụp run KFP được gọi.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
