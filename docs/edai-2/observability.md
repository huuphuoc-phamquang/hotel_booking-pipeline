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

**Cách làm:** [Đã có] `observability/stack/jaeger.yaml` nhận OTLP gRPC cổng 4317, UI qua ingress; risk-api đã gửi trace. [Cần làm] bổ sung OTel cho booking-mcp và tracing cho agentgateway; chụp một trace A2A → MCP → KServe.

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

## Bổ sung final-coursework

<a id="final-46"></a>
### Web API monitoring metrics such as req/s, num

**Rubric:** final · dòng 46 · 2 điểm · nhóm *Observability* › *Web API metrics*

> Web API monitoring metrics such as req/s, num. of reqs, num. of failures, etc.

**Cần nộp (cả nhóm):** Capture màn hình thể hiện các data đã được capture, có thể coi trên các dashboard

**Cách làm:** [Đã có] risk-api, drift-api và booking-mcp dùng `prometheus-fastapi-instrumentator` (`http_requests_total`, `http_request_duration_seconds`); chart `helm/api` có ServiceMonitor; dashboard `observability/dashboards/booking-apis.json` hiển thị req/s, lỗi 5xx, p95 và số replica. [Cần làm] chụp dashboard.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="final-47"></a>
### Collect và visualize metrics với Prometheus + Grafana · final · Observability

**Rubric:** final · dòng 47 · 2 điểm · nhóm *Observability* › *Computing telemetry data (such as CPU, RAM, disk, network, etc.)*

> Collect và visualize metrics với Prometheus + Grafana (hoặc tool tương tự)

**Cách làm:** [Đã có] `observability/stack/kube-prometheus-stack.yaml` gồm node-exporter, kube-state-metrics, sidecar Grafana tự nạp dashboard, và scrape PushGateway cùng queue-proxy theo revision. [Cần làm] chụp dashboard.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="final-48"></a>
### Tương tự cho logs · final · Observability

**Rubric:** final · dòng 48 · 2 điểm · nhóm *Observability* › *Computing telemetry data (such as CPU, RAM, disk, network, etc.)*

**Cách làm:** [Đã có] `observability/stack/efk.yaml`: Fluent Bit (DaemonSet) → Elasticsearch → Kibana; lệnh cài nằm trong file. [Cần làm] chụp Kibana.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="final-49"></a>
### Tương tự cho traces · final · Observability

**Rubric:** final · dòng 49 · 2 điểm · nhóm *Observability* › *Computing telemetry data (such as CPU, RAM, disk, network, etc.)*

**Cách làm:** [Đã có] risk-api bật OTel cho FastAPI và httpx, thêm span `feast.online`, gửi OTLP tới Jaeger (`observability/stack/jaeger.yaml`); tracing chỉ bật khi có `OTEL_EXPORTER_OTLP_ENDPOINT`. [Cần làm] chụp một trace đi qua Feast và KServe.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="final-50"></a>
### Airflow data drift pipeline to periodically pull data from offline feature store and…

**Rubric:** final · dòng 50 · 1 điểm · nhóm *Observability* › *ML-related telemetry data*

> Airflow data drift pipeline to periodically pull data from offline feature store and compare with groundtruth and update to Grafana dashboard (via PushGateway). Assumption: we don't have groundtruth to monitor drift here!

**Cách làm:** [Đã có] DAG `drift_monitor` chạy hằng ngày: so `lead_days` của 7 ngày gần nhất trong Gold với reference của model production (PSI và KS, `dags/drift_stats.py`), so tỉ lệ huỷ dự báo với thực tế, rồi đẩy kết quả qua PushGateway lên Grafana. [Cần làm] chụp dashboard quanh mốc 2025-06-01.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="final-51"></a>
### Trigger retrain by calling Kubeflow API

**Rubric:** final · dòng 51 · 1 điểm · nhóm *Observability* › *ML-related telemetry data*

> Trigger retrain by calling Kubeflow API (you can design by adding one step at the end of the Airflow data drift pipeline)

**Cách làm:** [Đã có] Khi PSI > 0,2 hoặc lệch calibration > 0,03, `drift_monitor` ghi mốc phát hiện vào Variable `cancel_risk_drift_detected`. Retrain chỉ được gọi (`kfp.Client().create_run_from_pipeline_package`) khi đã có đủ 30 ngày booking sau mốc với nhãn chín, tức khoảng mốc + 120 ngày (`drift_stats.retrain_window`, có test), với `since` là mốc và `until` là ngày chạy; nhờ vậy v2 chỉ học dữ liệu sau drift. Mốc bị xoá khi hết drift 3 ngày liên tiếp hoặc khi production đổi version. `calib_gap` chỉ tính booking do đúng version production chấm. [Cần làm] chụp run KFP được gọi.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._
