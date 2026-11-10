# Web API: pricing-api & drift-api

Web API kéo dữ liệu, drift detection realtime, autoscale bằng KEDA.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="final-3"></a>
## Có sử dụng FastAPI + data validation + healthcheck for k8s · final · Web API kéo dữ liệu

**Rubric:** final · dòng 3 · 2 điểm · nhóm *Web API kéo dữ liệu* › *Có sử dụng FastAPI + data validation (với pydantic)*

> Có sử dụng FastAPI + data validation (với pydantic) + healthcheck for k8s

**Cần nộp (cả nhóm):** Capture màn hình cách mọi người handle rolling update và fall back

**Cách làm:** [Thiết kế] pricing-api FastAPI POST /v1/quote {hotel_id, room_type, stay_date, rate_plan}, pydantic kiểm stay_date ≥ hôm nay, rate_plan hợp lệ; lấy feature online từ Feast theo hotel_id + stay_date rồi gọi KServe demand-model + cancel-segment; /healthz liveness, /readyz kiểm Feast + KServe. MCP quote_price gọi lại API này. [Cần làm] chụp rolling update + rollback.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-4"></a>
## Sử dụng async · final · Web API kéo dữ liệu

**Rubric:** final · dòng 4 · 2 điểm · nhóm *Web API kéo dữ liệu* › *Có sử dụng FastAPI + data validation (với pydantic)*

**Cách làm:** [Thiết kế] handler async; Feast online read + 2 request KServe chạy song song bằng asyncio.gather + httpx.AsyncClient dùng chung.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-5"></a>
## Deploy to k8s with helm + rollingupdate + auto fallback · final · Web API kéo dữ liệu

**Rubric:** final · dòng 5 · 2 điểm · nhóm *Web API kéo dữ liệu* › *Có sử dụng FastAPI + data validation (với pydantic)*

> Deploy to k8s with helm + rollingupdate + auto fallback (see --atomic)

**Cách làm:** [Đã có] chart helm/booking-mcp (RollingUpdate maxUnavailable 0, probe) dùng lại cho pricing-api; helm upgrade --install --atomic --timeout 5m. [Cần làm] deploy image lỗi -> chụp tự rollback (helm history).

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-6"></a>
## Có sử dụng FastAPI + data validation + healthcheck for k8s · final · Web API cho Real-time Drift Detection

**Rubric:** final · dòng 6 · 2 điểm · nhóm *Web API cho Real-time Drift Detection* › *Có sử dụng FastAPI + data validation (với pydantic)*

> Có sử dụng FastAPI + data validation (với pydantic) + healthcheck for k8s

**Cách làm:** [Thiết kế] drift-api FastAPI nhận CloudEvent từ KNative Eventing (KServe logger của demand-model -> Broker -> Trigger), pydantic cho payload; alibi-detect KSDrift với reference = tập train của model production; trả is_drift, p_val, đẩy Prometheus; /healthz, /readyz.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-7"></a>
## Sử dụng async · final · Web API cho Real-time Drift Detection

**Rubric:** final · dòng 7 · 2 điểm · nhóm *Web API cho Real-time Drift Detection* › *Có sử dụng FastAPI + data validation (với pydantic)*

**Cách làm:** [Thiết kế] handler async; detector chạy trong threadpool (run_in_threadpool) để không chặn event loop.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-8"></a>
## Deploy to k8s with helm + rollingupdate + auto fallback · final · Web API cho Real-time Drift Detection

**Rubric:** final · dòng 8 · 2 điểm · nhóm *Web API cho Real-time Drift Detection* › *Có sử dụng FastAPI + data validation (với pydantic)*

> Deploy to k8s with helm + rollingupdate + auto fallback (see --atomic)

**Cách làm:** [Thiết kế] cùng chart, RollingUpdate + --atomic như pricing-api. [Cần làm] chụp rollback.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-9"></a>
## Web API kéo dữ liệu

**Rubric:** final · dòng 9 · 2 điểm · nhóm *Autoscale* › *Autoscale Web API kéo dữ liệu và drift detection (ví dụ dùng với KEDA để scale theo req)*

**Cần nộp (cả nhóm):** Capture màn hình cách mọi người handle autoscale và demonstrate it worked!

**Cách làm:** [Thiết kế] KEDA ScaledObject Prometheus scaler theo rate(http_requests_total[1m]) của pricing-api, min 2 max 10. [Cần làm] chụp scale khi locust.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-10"></a>
## Web API cho drift detection

**Rubric:** final · dòng 10 · 2 điểm · nhóm *Autoscale* › *Autoscale Web API kéo dữ liệu và drift detection (ví dụ dùng với KEDA để scale theo req)*

**Cách làm:** [Thiết kế] KEDA ScaledObject theo số CloudEvent/s vào drift-api, min 2 max 10. [Cần làm] chụp scale.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
