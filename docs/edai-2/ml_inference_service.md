# ML inference service

Model được phục vụ bằng KServe theo mô hình model-inside-image.

<a id="edai-2-15"></a>
## Phục vụ model bằng KServe (model-inside-image)

KServe v0.15.2 cài ở chế độ RawDeployment (Deployment + Service + HPA); Knative Eventing và Istio được cài sau, cho
drift-api (mục dưới). Image `ml/cancel-risk:v1` theo mô hình model-inside-image: model version 1 tải từ MLflow
(`models:/cancel-risk/1`) rồi COPY vào `/mnt/models` lúc build (`serving/Dockerfile`, `MODEL_VERSION=1`), nên pod không
tải model lúc khởi động. InferenceService dựng từ `serving/kserve-cancel-risk.yaml`; chưa tạo `cancel-risk-bulk` (RawDeployment không scale về 0 nếu thiếu KEDA).

InferenceService `cancel-risk` Ready, Deployment `cancel-risk-predictor` 1/1, HPA 1–3 replica theo CPU. Gọi thẳng V1
predict trả `200` với xác suất [không huỷ, huỷ] và `model_version: "1"`. Qua booking-mcp, tool `predict_cancellation` và
REST `/v1/cancel-risk` lấy feature từ Feast rồi gọi KServe: 20/20 lời gọi thử thành công. Trace dưới đây ghi lúc chịu tải
(load test ở `testing.md`): lời gọi KServe chỉ mất 7,49 ms trên tổng 492,64 ms, phần còn lại là hai lần đọc online store Feast.

![KServe: InferenceService, Deployment, HPA và lời gọi predict](../images/edai-2/kserve-cli.png)

![Jaeger: booking-mcp → Feast → KServe](../images/edai-2/jaeger-trace-kserve.png)

## Kiểm thử Real-time Drift Detection (`drift-api` + `alibi-detect` KSDrift)

[`edai2/drift_api/drift_api.py`](../../edai2/drift_api/drift_api.py) chạy FastAPI nhận batch feature (hoặc CloudEvent từ Knative Eventing), tích lũy đủ `WINDOW` dòng rồi chạy `KSDrift` trên `lead_days` so với tập reference khi train (`gamma(2, 10)`).

Kiểm thử trong container `python:3.12-slim` (`pytest tests/test_drift_api.py -v`: **9/9 test pass**) và mô phỏng phân phối trước/sau mốc drift `2025-06-01` (`WINDOW=500`, `lead_days * 1.5`):
- **Trước `2025-06-01` (`PRE_2025_06_01`):** `is_drift=False`, `p_val=0.8746`
- **Sau `2025-06-01` (`POST_2025_06_01`):** `is_drift=True`, `p_val=3.11e-21`

![Unit test drift-api đạt 9/9 test](../images/edai-2/drift-api-tests.jpg)

![Kiểm thử drift-api KSDrift trước/sau mốc 2025-06-01 và CrossHair](../images/edai-2/drift-ksdrift-crosshair.jpg)

Trên GKE, `Broker/default` (Knative Eventing), `Trigger/cancel-risk-requests-to-drift-api`, `ScaledObject/drift-api` (KEDA) và `drift-api` (`2/2 Running` kèm Istio sidecar) đều hoạt động ở trạng thái `READY: True`:

![Tài nguyên Knative Eventing, KEDA ScaledObject và Istio trên namespace ml](../images/edai-2/ml-drift-keda-knative-istio.png)


