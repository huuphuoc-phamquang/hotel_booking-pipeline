# Web API: risk-api & drift-api

risk-api lấy feature theo `booking_id` rồi gọi KServe `cancel-risk`. drift-api phát hiện drift theo thời gian
thực. Cả hai autoscale bằng KEDA.

Mỗi mục dưới đây ứng với một dòng của rubric. Phần **Cách làm** mô tả giải pháp đã triển khai, đồng bộ từ
cột F của rubric. Phần **Kết quả** ghi test đã chạy, số liệu đo được hoặc ảnh chụp (`docs/images/`).

<a id="final-3"></a>
## Có sử dụng FastAPI + data validation + healthcheck for k8s · final · Web API kéo dữ liệu

**Rubric:** final · dòng 3 · 2 điểm · nhóm *Web API kéo dữ liệu* › *Có sử dụng FastAPI + data validation (với pydantic)*

> Có sử dụng FastAPI + data validation (với pydantic) + healthcheck for k8s

**Cần nộp (cả nhóm):** Capture màn hình cách mọi người handle rolling update và fall back

**Cách làm:** [Đã có] risk-api (`edai2/risk_api/risk_api.py`) nhận `POST /v1/cancel-risk {booking_id}` (pydantic, `booking_id` > 0), đọc `booking_attributes` và feature khách, khách sạn từ Feast, rồi gọi KServe cancel-risk. API trả 404 khi booking chưa có trên online store, có `/healthz`, `/readyz`. Tool MCP `predict_cancellation` gọi lại API này. [Cần làm] chụp rolling update và rollback.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="final-4"></a>
## Sử dụng async · final · Web API kéo dữ liệu

**Rubric:** final · dòng 4 · 2 điểm · nhóm *Web API kéo dữ liệu* › *Có sử dụng FastAPI + data validation (với pydantic)*

**Cách làm:** [Đã có] Handler của risk-api là async; Feast online được đọc bằng `get_online_features_async`, KServe được gọi qua một `httpx.AsyncClient` dùng chung.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="final-5"></a>
## Deploy to k8s with helm + rollingupdate + auto fallback · final · Web API kéo dữ liệu

**Rubric:** final · dòng 5 · 2 điểm · nhóm *Web API kéo dữ liệu* › *Có sử dụng FastAPI + data validation (với pydantic)*

> Deploy to k8s with helm + rollingupdate + auto fallback (see --atomic)

**Cách làm:** [Đã có] Chart chung `helm/api` (`values-risk-api.yaml`, `values-drift-api.yaml`, `values-booking-mcp.yaml`) dùng RollingUpdate `maxUnavailable: 0` và probe; Jenkins chạy `helm upgrade --install --atomic --timeout 5m`. [Cần làm] deploy image lỗi rồi chụp quá trình tự rollback (`helm history`).

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="final-6"></a>
## Có sử dụng FastAPI + data validation + healthcheck for k8s · final · Web API cho Real-time Drift Detection

**Rubric:** final · dòng 6 · 2 điểm · nhóm *Web API cho Real-time Drift Detection* › *Có sử dụng FastAPI + data validation (với pydantic)*

> Có sử dụng FastAPI + data validation (với pydantic) + healthcheck for k8s

**Cách làm:** [Đã có] `drift_api/drift_api.py` là FastAPI nhận CloudEvent từ Knative Eventing (KServe logger của cancel-risk → Broker → Trigger, `k8s/drift-eventing.yaml`), kiểm payload bằng pydantic. Mỗi 500 dòng, API chạy alibi-detect KSDrift trên `lead_days` với reference là tập train của model production (artifact MLflow), trả `is_drift`, `p_val` và đẩy lên Prometheus; có `/healthz`, `/readyz`. `score_bookings` chấm mỗi booking một lần lúc tạo, nên request giữ phân phối `lead_days` như lúc train; chấm lại hằng ngày từng khiến KS báo drift giả. Lần chấm lại hàng loạt sau promote đi qua `cancel-risk-bulk` không có logger. [Cần làm] chụp p-value trước và sau 2025-06-01.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="final-7"></a>
## Sử dụng async · final · Web API cho Real-time Drift Detection

**Rubric:** final · dòng 7 · 2 điểm · nhóm *Web API cho Real-time Drift Detection* › *Có sử dụng FastAPI + data validation (với pydantic)*

**Cách làm:** [Đã có] Handler async; KSDrift chạy trong threadpool (`run_in_threadpool`) để không chặn event loop.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="final-8"></a>
## Deploy to k8s with helm + rollingupdate + auto fallback · final · Web API cho Real-time Drift Detection

**Rubric:** final · dòng 8 · 2 điểm · nhóm *Web API cho Real-time Drift Detection* › *Có sử dụng FastAPI + data validation (với pydantic)*

> Deploy to k8s with helm + rollingupdate + auto fallback (see --atomic)

**Cách làm:** [Đã có] drift-api dùng chung chart `helm/api` (`values-drift-api.yaml`): RollingUpdate `maxUnavailable: 0`, probe, `--atomic`. [Cần làm] chụp rollback.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="final-9"></a>
## Web API kéo dữ liệu

**Rubric:** final · dòng 9 · 2 điểm · nhóm *Autoscale* › *Autoscale Web API kéo dữ liệu và drift detection (ví dụ dùng với KEDA để scale theo req)*

**Cần nộp (cả nhóm):** Capture màn hình cách mọi người handle autoscale và demonstrate it worked!

**Cách làm:** [Đã có] `k8s/keda.yaml` có ScaledObject cho risk-api theo `rate(http_requests_total)` (từ `prometheus-fastapi-instrumentator`), từ 2 tới 10 replica; chart bỏ `replicas` khi bật autoscale để helm không ghi đè KEDA. [Cần làm] chụp quá trình scale khi chạy locust.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="final-10"></a>
## Web API cho drift detection

**Rubric:** final · dòng 10 · 2 điểm · nhóm *Autoscale* › *Autoscale Web API kéo dữ liệu và drift detection (ví dụ dùng với KEDA để scale theo req)*

**Cách làm:** [Đã có] `k8s/keda.yaml` scale drift-api theo `drift_events_total`, nhưng giữ 1 replica vì buffer cửa sổ KS nằm trong bộ nhớ pod (shortcut đã ghi trong file). [Cần làm] chụp.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._
