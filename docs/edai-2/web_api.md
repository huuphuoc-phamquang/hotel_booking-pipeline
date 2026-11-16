# Web API: risk-api & drift-api

risk-api lấy feature theo `booking_id` rồi gọi KServe `cancel-risk`; drift-api phát hiện drift realtime; autoscale bằng KEDA.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="final-3"></a>
## Có sử dụng FastAPI + data validation + healthcheck for k8s · final · Web API kéo dữ liệu

**Rubric:** final · dòng 3 · 2 điểm · nhóm *Web API kéo dữ liệu* › *Có sử dụng FastAPI + data validation (với pydantic)*

> Có sử dụng FastAPI + data validation (với pydantic) + healthcheck for k8s

**Cần nộp (cả nhóm):** Capture màn hình cách mọi người handle rolling update và fall back

**Cách làm:** [Đã có] risk-api (edai2/risk_api/risk_api.py): FastAPI POST /v1/cancel-risk {booking_id} (pydantic, booking_id > 0) -> Feast booking_attributes + feature khách/khách sạn -> KServe cancel-risk; 404 khi booking chưa có trên online store; /healthz, /readyz. Tool MCP predict_cancellation gọi lại API này. [Cần làm] chụp rolling update + rollback.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-4"></a>
## Sử dụng async · final · Web API kéo dữ liệu

**Rubric:** final · dòng 4 · 2 điểm · nhóm *Web API kéo dữ liệu* › *Có sử dụng FastAPI + data validation (với pydantic)*

**Cách làm:** [Đã có] risk-api: handler async; đọc Feast online bằng get_online_features_async, gọi KServe bằng httpx.AsyncClient dùng chung.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-5"></a>
## Deploy to k8s with helm + rollingupdate + auto fallback · final · Web API kéo dữ liệu

**Rubric:** final · dòng 5 · 2 điểm · nhóm *Web API kéo dữ liệu* › *Có sử dụng FastAPI + data validation (với pydantic)*

> Deploy to k8s with helm + rollingupdate + auto fallback (see --atomic)

**Cách làm:** [Đã có] chart chung helm/api (values-risk-api.yaml, values-drift-api.yaml, values-booking-mcp.yaml): RollingUpdate maxUnavailable 0, probe; Jenkins helm upgrade --install --atomic --timeout 5m. [Cần làm] deploy image lỗi -> chụp tự rollback (helm history).

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-6"></a>
## Có sử dụng FastAPI + data validation + healthcheck for k8s · final · Web API cho Real-time Drift Detection

**Rubric:** final · dòng 6 · 2 điểm · nhóm *Web API cho Real-time Drift Detection* › *Có sử dụng FastAPI + data validation (với pydantic)*

> Có sử dụng FastAPI + data validation (với pydantic) + healthcheck for k8s

**Cách làm:** [Đã có] drift_api/drift_api.py: FastAPI nhận CloudEvent từ KNative Eventing (KServe logger của cancel-risk -> Broker -> Trigger, k8s/drift-eventing.yaml), pydantic cho payload; gom 500 dòng rồi alibi-detect KSDrift chỉ trên lead_days với reference = tập train của model production (artifact MLflow); trả is_drift, p_val, đẩy Prometheus; /healthz, /readyz. [Cần làm] chụp p_value trước/sau 2025-06-01; score_bookings chấm mỗi booking 1 lần lúc tạo nên request giữ phân phối lead_days như lúc train (chấm lại mỗi ngày làm KS báo drift giả).

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-7"></a>
## Sử dụng async · final · Web API cho Real-time Drift Detection

**Rubric:** final · dòng 7 · 2 điểm · nhóm *Web API cho Real-time Drift Detection* › *Có sử dụng FastAPI + data validation (với pydantic)*

**Cách làm:** [Đã có] handler async; KSDrift chạy trong threadpool (run_in_threadpool) để không chặn event loop.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-8"></a>
## Deploy to k8s with helm + rollingupdate + auto fallback · final · Web API cho Real-time Drift Detection

**Rubric:** final · dòng 8 · 2 điểm · nhóm *Web API cho Real-time Drift Detection* › *Có sử dụng FastAPI + data validation (với pydantic)*

> Deploy to k8s with helm + rollingupdate + auto fallback (see --atomic)

**Cách làm:** [Đã có] drift-api dùng chung chart helm/api (values-drift-api.yaml): RollingUpdate maxUnavailable 0, probe, --atomic. [Cần làm] chụp rollback.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-9"></a>
## Web API kéo dữ liệu

**Rubric:** final · dòng 9 · 2 điểm · nhóm *Autoscale* › *Autoscale Web API kéo dữ liệu và drift detection (ví dụ dùng với KEDA để scale theo req)*

**Cần nộp (cả nhóm):** Capture màn hình cách mọi người handle autoscale và demonstrate it worked!

**Cách làm:** [Đã có] k8s/keda.yaml: ScaledObject risk-api theo rate(http_requests_total) (prometheus-fastapi-instrumentator), min 2 max 10; chart bỏ replicas khi autoscaled để helm không ghi đè KEDA. [Cần làm] chụp scale khi locust.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-10"></a>
## Web API cho drift detection

**Rubric:** final · dòng 10 · 2 điểm · nhóm *Autoscale* › *Autoscale Web API kéo dữ liệu và drift detection (ví dụ dùng với KEDA để scale theo req)*

**Cách làm:** [Đã có] k8s/keda.yaml cho drift-api theo drift_events_total; giữ 1 replica vì buffer cửa sổ KS nằm trong bộ nhớ pod (shortcut ghi trong file). [Cần làm] chụp.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
