"""risk-api: Web API lấy feature theo booking_id từ Feast online rồi gọi KServe cancel-risk.

Rubric final › Web API kéo dữ liệu (lấy feature từ online store theo ID rồi gửi tới ML inference engine):
  - FastAPI + pydantic + healthcheck k8s : RiskRequest / CancelRisk, /healthz (liveness), /readyz (Feast đọc được)
  - async                                : Feast online async, httpx.AsyncClient dùng chung
  - monitoring                           : prometheus-fastapi-instrumentator (req/s, số req, lỗi, latency) ở /metrics;
                                           OTel trace FastAPI + httpx + span đọc Feast -> Jaeger khi có OTEL_EXPORTER_OTLP_ENDPOINT
  - batch                                : /v1/cancel-risk/batch chấm nhiều booking bằng 1 lần đọc Feast + 1 request
                                           KServe (DAG score_bookings dùng mỗi ngày, ghi gold.booking_risk)
Bài toán: xác suất huỷ của từng booking, revenue manager cộng dồn theo hotel × stay_date để chọn số phòng bán vượt.
Tool MCP predict_cancellation gọi lại API này, nên logic dự báo chỉ ở một chỗ.
"""
import os
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException
from feast import FeatureStore
from opentelemetry import trace
from prometheus_client import make_asgi_app
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel, Field

KSERVE_URL = os.environ.get("KSERVE_URL", "http://cancel-risk-predictor.ml.svc.cluster.local/v1/models/cancel-risk:predict")
BOOKING_FEATURES = ["booking_attributes:customer_id", "booking_attributes:hotel_id", "booking_attributes:lead_days",
                    "booking_attributes:nights", "booking_attributes:free_cancel", "booking_attributes:loyalty_tier"]
CONTEXT_FEATURES = ["customer_booking_stats:bookings_90d", "customer_booking_stats:cancel_rate_90d",
                    "customer_booking_stats:avg_lead_days_90d", "hotel_demand:bookings_7d",
                    "hotel_demand:cancel_rate_30d"]

store = FeatureStore(repo_path=os.environ.get("FEAST_REPO", "/feature_repo"))
tracer = trace.get_tracer("risk-api")
http = httpx.AsyncClient(timeout=5.0)


class RiskRequest(BaseModel):
    """Booking cần chấm điểm."""
    booking_id: int = Field(gt=0)


class BatchRequest(BaseModel):
    """Nhiều booking cần chấm điểm (1 lô của DAG score_bookings)."""
    booking_ids: list[int] = Field(min_length=1, max_length=1000)


class CancelRisk(BaseModel):
    """Xác suất booking bị huỷ. Chỉ dùng cộng dồn cho overbooking, không đổi giá hay điều kiện của khách."""
    booking_id: int
    probability: float = Field(ge=0.0, le=1.0)
    model_version: str | None = Field(None, description="version MLflow của revision KServe đã chấm (A/B canary)")


class BatchRisk(BaseModel):
    """Kết quả theo lô; booking chưa có trên online store nằm ở missing thay vì làm hỏng cả lô.
    Cả lô là 1 request KServe nên do đúng 1 revision chấm: model_version chung."""
    results: list[CancelRisk]
    missing: list[int]
    model_version: str | None = None


async def _online(features: list[str], entities: list[dict]) -> list[dict]:
    """Đọc nhiều dòng từ online store, 1 dict / entity theo đúng thứ tự (None nếu chưa có trong TTL)."""
    with tracer.start_as_current_span("feast.online", attributes={"feast.view": features[0].split(":")[0],
                                                                    "feast.rows": len(entities)}):
        resp = (await store.get_online_features_async(features=features, entity_rows=entities)).to_dict()
    return [dict(zip(resp, vals)) for vals in zip(*resp.values())]


async def model_rows(booking_ids: list[int]) -> tuple[list[int], list[list], list[int]]:
    """Dựng input theo đúng thứ tự MODEL_INPUTS của ml/training_pipeline.py, điền thiếu y như lúc train.
    Trả (booking tìm thấy, input tương ứng, booking chưa có trên online store)."""
    bs = await _online(BOOKING_FEATURES, [{"booking_id": i} for i in booking_ids])
    found = [(i, b) for i, b in zip(booking_ids, bs) if b.get("customer_id") is not None]
    missing = [i for i, b in zip(booking_ids, bs) if b.get("customer_id") is None]
    if not found:
        return [], [], missing
    fs = await _online(CONTEXT_FEATURES, [{"customer_id": b["customer_id"], "hotel_id": b["hotel_id"]} for _, b in found])
    rows = [[b["lead_days"], b["nights"], b["free_cancel"],
             f["bookings_90d"] or 0, f["cancel_rate_90d"] or 0.0, f["avg_lead_days_90d"] or 0.0,
             f["bookings_7d"] or 0, f["cancel_rate_30d"] or 0.0, int(f["bookings_90d"] is not None),
             b["loyalty_tier"] or 0] for (_, b), f in zip(found, fs)]
    return [i for i, _ in found], rows, missing


async def _predict(rows: list[list]) -> tuple[list[float], str | None]:
    """1 request KServe (V1 protocol) cho mọi dòng; trả (xác suất huỷ, model_version của revision đã chấm)."""
    r = await http.post(KSERVE_URL, json={"instances": rows})
    r.raise_for_status()
    body = r.json()
    # serving/predictor.py trả [P(không huỷ), P(huỷ)]; response chỉ có nhãn 0/1 thì lỗi ở đây
    return [float(p[1]) for p in body["predictions"]], body.get("model_version")


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await http.aclose()


app = FastAPI(title="risk-api", lifespan=lifespan)
Instrumentator(excluded_handlers=["/metrics", "/healthz", "/readyz"]).instrument(app)
app.mount("/metrics", make_asgi_app())


def setup_tracing() -> None:
    """Gửi trace OTLP (Jaeger nhận OTLP gRPC :4317); không đặt endpoint thì không bật (test, chạy local)."""
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    provider = TracerProvider(resource=Resource.create({"service.name": "risk-api"}))
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app, excluded_urls="healthz,readyz,metrics")
    HTTPXClientInstrumentor().instrument_client(http)


if os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"):
    setup_tracing()


@app.post("/v1/cancel-risk", response_model=CancelRisk)
async def cancel_risk(req: RiskRequest) -> CancelRisk:
    """Lấy feature theo booking_id rồi gọi KServe."""
    _, rows, missing = await model_rows([req.booking_id])
    if missing:
        raise HTTPException(status_code=404, detail=f"booking {req.booking_id} chưa có trên online store")
    probs, version = await _predict(rows)
    return CancelRisk(booking_id=req.booking_id, probability=probs[0], model_version=version)


@app.post("/v1/cancel-risk/batch", response_model=BatchRisk)
async def cancel_risk_batch(req: BatchRequest) -> BatchRisk:
    """Chấm cả lô: 2 lần đọc Feast + 1 request KServe thay vì mỗi booking 3 lượt."""
    ids, rows, missing = await model_rows(req.booking_ids)
    probs, version = await _predict(rows) if rows else ([], None)
    results = [CancelRisk(booking_id=i, probability=p, model_version=version) for i, p in zip(ids, probs)]
    return BatchRisk(results=results, missing=missing, model_version=version)


@app.get("/healthz")
async def healthz() -> dict:
    """Liveness probe: process còn sống."""
    return {"status": "ok"}


@app.get("/readyz")
async def readyz() -> dict:
    """Readiness probe: chỉ nhận traffic khi đọc được online store."""
    await _online(BOOKING_FEATURES, [{"booking_id": 1}])
    return {"status": "ready"}
