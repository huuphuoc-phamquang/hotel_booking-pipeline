"""MCP server cung cấp tool cho agent đặt phòng: đọc online feature, dự đoán rủi ro huỷ, tra chính sách (RAG),
đề xuất số phòng bán vượt (propose_overbooking) và ghi lại số đã duyệt (apply_overbooking, agent bắt buộc HITL).

Rubric edai-2 › Web API kéo dữ liệu user và chunk:
  - FastAPI/pydantic + healthcheck k8s : input/output là pydantic model, /healthz và /readyz cho probe
  - async cho concurrent processing    : tool là async def, Feast online async, httpx.AsyncClient
  - Deploy dạng MCP tool               : FastMCP streamable HTTP, mount trong FastAPI, deploy bằng Helm
Rubric edai-2 › ML Inference Service: predict_cancellation lấy feature theo booking_id từ Feast online rồi gọi
  thẳng KServe cancel-risk. Cùng logic mở thêm REST /v1/cancel-risk (locust) và /v1/cancel-risk/batch (DAG
  score_bookings ghi gold.booking_risk), nên input model chỉ dựng ở một chỗ (model_rows).
Rubric edai-2 › Observability: /metrics (req/s, số req, lỗi, latency), đếm số lần gọi mỗi tool và số lần lỗi;
  OTel trace FastAPI + httpx + span đọc Feast -> Jaeger khi có OTEL_EXPORTER_OTLP_ENDPOINT.
"""
import asyncio
import os
from contextlib import asynccontextmanager
from datetime import date

import httpx
from fastapi import FastAPI, HTTPException
from feast import FeatureStore
from mcp.server.fastmcp import FastMCP          # mcp SDK 1.x; bản 2.x đổi thành mcp.server.mcpserver.MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from opentelemetry import trace
from prometheus_client import Counter, make_asgi_app
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel, Field

from overbooking import limit

KSERVE_URL = os.environ.get("KSERVE_URL", "http://cancel-risk-predictor.ml.svc.cluster.local/v1/models/cancel-risk:predict")
# InferenceService không logger cho chấm lại hàng loạt (serving/kserve-cancel-risk.yaml › cancel-risk-bulk)
KSERVE_BULK_URL = os.environ.get("KSERVE_BULK_URL",
                                 "http://cancel-risk-bulk-predictor.ml.svc.cluster.local/v1/models/cancel-risk:predict")
BOOKING_FEATURES = ["booking_attributes:customer_id", "booking_attributes:hotel_id", "booking_attributes:lead_days",
                    "booking_attributes:nights", "booking_attributes:free_cancel", "booking_attributes:loyalty_tier"]
CONTEXT_FEATURES = ["customer_booking_stats:bookings_90d", "customer_booking_stats:cancel_rate_90d",
                    "customer_booking_stats:avg_lead_days_90d", "hotel_demand:bookings_7d",
                    "hotel_demand:cancel_rate_30d"]
ONLINE_FEATURES = ["customer_booking_stats:bookings_90d", "customer_booking_stats:cancel_rate_90d",
                   "customer_booking_stats:avg_lead_days_90d", "hotel_demand:bookings_7d",
                   "hotel_demand:cancel_rate_30d", "hotel_realtime:bookings_1h"]

WAREHOUSE_DSN = os.environ.get("WAREHOUSE_DSN", "postgresql://mcp@postgres/warehouse")
# Chi phí theo đơn vị giá phòng: phòng trống mất 1 đêm, chuyển khách sang khách sạn khác tốn ~3 đêm (đền bù + uy tín)
C_SPOIL = float(os.environ.get("OVERBOOK_C_SPOIL", "1.0"))
C_WALK = float(os.environ.get("OVERBOOK_C_WALK", "3.0"))
# Booking chấm lúc tạo (score_bookings) và chấm lại khi promote (rescore_active): lấy lần chấm mới nhất của mỗi
# booking; chỉ cộng booking chưa huỷ tính tới lần chấm mới nhất của cả bảng (as_of)
RISK_SQL = """SELECT DISTINCT ON (r.booking_id) r.probability, r.scored_date
FROM gold.booking_risk r JOIN gold.fact_bookings f USING (booking_id)
WHERE r.hotel_id = %s AND r.stay_date = %s
  AND (f.cancelled_at IS NULL OR f.cancelled_at >= (SELECT max(scored_date) FROM gold.booking_risk))
ORDER BY r.booking_id, r.scored_date DESC"""
ROOMS_SQL = "SELECT rooms FROM gold.hotel_rooms WHERE hotel_id = %s AND stay_date = %s"
APPLY_SQL = """INSERT INTO gold.overbooking_limits (hotel_id, stay_date, k) VALUES (%s, %s, %s)
ON CONFLICT (hotel_id, stay_date) DO UPDATE SET k = EXCLUDED.k, approved_at = now()"""

TOOL_CALLS = Counter("mcp_tool_calls_total", "Số lần gọi tool", ["tool"])
TOOL_FAILURES = Counter("mcp_tool_failures_total", "Số lần tool lỗi", ["tool"])

store = FeatureStore(repo_path=os.environ.get("FEAST_REPO", "/feature_repo"))
# Chặn DNS rebinding của SDK chỉ nhận Host localhost -> gọi qua tên service hay agentgateway bị 421; xác thực đã ở gateway
mcp = FastMCP("booking-tools", stateless_http=True, streamable_http_path="/",
              transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False))
http = httpx.AsyncClient(timeout=5.0)
tracer = trace.get_tracer("booking-mcp")
_embedder = None


class BookingFeatures(BaseModel):
    """Feature online của cặp (khách, khách sạn); None nếu chưa có dữ liệu trong TTL."""
    customer_id: int = Field(gt=0)
    hotel_id: int = Field(gt=0)
    bookings_90d: int | None = None
    cancel_rate_90d: float | None = None
    avg_lead_days_90d: float | None = None
    bookings_7d: int | None = None
    cancel_rate_30d: float | None = None
    bookings_1h: int | None = None


class RiskRequest(BaseModel):
    """Booking cần chấm điểm."""
    booking_id: int = Field(gt=0)


class BatchRequest(BaseModel):
    """Nhiều booking cần chấm điểm (1 lô của DAG score_bookings)."""
    booking_ids: list[int] = Field(min_length=1, max_length=1000)
    bulk: bool = Field(False, description="chấm lại hàng loạt: gọi cancel-risk-bulk, không qua KServe logger")


class CancelRisk(BaseModel):
    """Xác suất booking bị huỷ. Chỉ cộng dồn theo hotel × stay_date cho overbooking, không đổi giá hay điều kiện
    của khách."""
    booking_id: int
    probability: float = Field(ge=0.0, le=1.0)
    model_version: str | None = Field(None, description="version MLflow của revision KServe đã chấm")


class BatchRisk(BaseModel):
    """Kết quả theo lô; booking chưa có trên online store nằm ở missing thay vì làm hỏng cả lô.
    Cả lô là 1 request KServe nên do đúng 1 revision chấm: model_version chung."""
    results: list[CancelRisk]
    missing: list[int]
    model_version: str | None = None


class OverbookingProposal(BaseModel):
    """Đề xuất bán vượt cho 1 đêm: chưa ghi gì, revenue manager duyệt rồi mới gọi apply_overbooking."""
    hotel_id: int
    stay_date: date
    bookings: int = Field(ge=0, description="số booking đang giữ phòng")
    expected_cancellations: float = Field(ge=0)
    k: int = Field(ge=0, description="số phòng nên bán vượt")
    rooms: int | None = Field(None, description="số phòng mở bán đêm đó; None nếu ngoài 30 đêm của gold.hotel_rooms")
    can_sell: int | None = Field(None, ge=0, description="số booking còn nhận được: rooms + k - bookings, sàn 0")
    scored_date: date | None = Field(None, description="ngày chấm gần nhất trong các booking đang giữ phòng")


class Chunk(BaseModel):
    """1 đoạn chính sách tìm được bằng vector search."""
    chunk_id: str
    text: str
    score: float


async def _features(customer_id: int, hotel_id: int) -> BookingFeatures:
    """Đọc online store bất đồng bộ rồi đổi về pydantic model."""
    resp = await store.get_online_features_async(features=ONLINE_FEATURES,
                                                 entity_rows=[{"customer_id": customer_id, "hotel_id": hotel_id}])
    row = {k: v[0] for k, v in resp.to_dict().items()}
    return BookingFeatures(**row)


@mcp.tool()
async def get_booking_features(customer_id: int, hotel_id: int) -> BookingFeatures:
    """Lấy feature gần nhất: lịch sử đặt/huỷ của khách, nhu cầu 7 ngày và 1 giờ qua của khách sạn."""
    TOOL_CALLS.labels("get_booking_features").inc()
    try:
        return await _features(customer_id, hotel_id)
    except Exception:
        TOOL_FAILURES.labels("get_booking_features").inc()
        raise


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
             f["bookings_7d"] or 0, f["cancel_rate_30d"] or 0.0, int((f["bookings_90d"] or 0) > 1),
             b["loyalty_tier"] or 0] for (_, b), f in zip(found, fs)]
    return [i for i, _ in found], rows, missing


async def _predict(rows: list[list], url: str = KSERVE_URL) -> tuple[list[float], str | None]:
    """1 request KServe (V1 protocol) cho mọi dòng; trả (xác suất huỷ, model_version của revision đã chấm)."""
    r = await http.post(url, json={"instances": rows})
    r.raise_for_status()
    body = r.json()
    # serving/predictor.py trả [P(không huỷ), P(huỷ)]; response chỉ có nhãn 0/1 thì lỗi ở đây
    return [float(p[1]) for p in body["predictions"]], body.get("model_version")


async def _cancel_risk(booking_id: int) -> CancelRisk:
    """Feature theo booking_id từ Feast online + 1 request KServe; LookupError nếu booking chưa lên online store."""
    _, rows, missing = await model_rows([booking_id])
    if missing:
        raise LookupError(f"booking {booking_id} chưa có trên online store")
    probs, version = await _predict(rows)
    return CancelRisk(booking_id=booking_id, probability=probs[0], model_version=version)


@mcp.tool()
async def predict_cancellation(booking_id: int) -> CancelRisk:
    """Xác suất booking này bị huỷ: lấy feature theo booking_id từ online store rồi gọi model cancel-risk (KServe)."""
    TOOL_CALLS.labels("predict_cancellation").inc()
    try:
        return await _cancel_risk(booking_id)
    except Exception:
        TOOL_FAILURES.labels("predict_cancellation").inc()
        raise


async def _query(sql: str, params: tuple, fetch: bool = True) -> list[tuple]:
    """1 câu SQL trên warehouse (psycopg 3 async); kết nối ngắn hạn vì tool ít gọi."""
    import psycopg
    async with await psycopg.AsyncConnection.connect(WAREHOUSE_DSN) as conn:
        cur = await conn.execute(sql, params)
        return await cur.fetchall() if fetch else []


@mcp.tool()
async def propose_overbooking(hotel_id: int, stay_date: date) -> OverbookingProposal:
    """Đề xuất số phòng bán vượt cho đêm stay_date: cộng dồn xác suất huỷ của booking còn giữ phòng (gold.booking_risk,
    DAG score_bookings chấm lúc tạo) rồi lấy K tối ưu theo chi phí phòng trống / chuyển khách, và so với số phòng:
    còn nhận được rooms + K - bookings booking nữa. Chỉ đề xuất, không ghi."""
    TOOL_CALLS.labels("propose_overbooking").inc()
    try:
        rows, rooms = await asyncio.gather(_query(RISK_SQL, (hotel_id, stay_date)),
                                           _query(ROOMS_SQL, (hotel_id, stay_date)))
        probs = [float(r[0]) for r in rows]
        k = limit(probs, C_SPOIL, C_WALK)
        n_rooms = int(rooms[0][0]) if rooms else None
        return OverbookingProposal(hotel_id=hotel_id, stay_date=stay_date, bookings=len(probs),
                                   expected_cancellations=round(sum(probs), 2), k=k, rooms=n_rooms,
                                   can_sell=None if n_rooms is None else max(0, n_rooms + k - len(probs)),
                                   scored_date=max(r[1] for r in rows) if rows else None)
    except Exception:
        TOOL_FAILURES.labels("propose_overbooking").inc()
        raise


@mcp.tool()
async def apply_overbooking(hotel_id: int, stay_date: date, k: int) -> str:
    """Ghi số phòng bán vượt đã được revenue manager duyệt vào gold.overbooking_limits (kagent requireApproval)."""
    TOOL_CALLS.labels("apply_overbooking").inc()
    try:
        if k < 0:
            raise ValueError("k phải >= 0")
        await _query(APPLY_SQL, (hotel_id, stay_date, k), fetch=False)
        return f"Đã ghi K={k} cho hotel {hotel_id} đêm {stay_date}"
    except Exception:
        TOOL_FAILURES.labels("apply_overbooking").inc()
        raise


@mcp.tool()
async def search_policy(question: str, top_k: int = 4) -> list[Chunk]:
    """RAG: embed câu hỏi rồi lấy top_k đoạn chính sách huỷ/hoàn tiền/quy định gần nhất."""
    TOOL_CALLS.labels("search_policy").inc()
    try:
        global _embedder
        if _embedder is None:                    # nạp model 1 lần, không nạp lại mỗi request
            from sentence_transformers import SentenceTransformer
            _embedder = SentenceTransformer("BAAI/bge-m3")
        vec = _embedder.encode(question, normalize_embeddings=True).tolist()
        # API Feast này là sync -> chạy trong thread để không chặn event loop
        res = (await asyncio.to_thread(store.retrieve_online_documents_v2,
                                       features=["policy_chunks:text", "policy_chunks:embedding"],
                                       query=vec, top_k=top_k)).to_dict()
        return [Chunk(chunk_id=c, text=t, score=s)
                for c, t, s in zip(res["chunk_id"], res["text"], res["distance"])]
    except Exception:
        TOOL_FAILURES.labels("search_policy").inc()
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Khởi động session manager của MCP cùng vòng đời FastAPI."""
    async with mcp.session_manager.run():
        yield
    await http.aclose()


app = FastAPI(title="booking-tools", lifespan=lifespan)
Instrumentator(excluded_handlers=["/metrics", "/healthz", "/readyz"]).instrument(app)                # req/s, số req, lỗi của /mcp
app.mount("/mcp", mcp.streamable_http_app())
app.mount("/metrics", make_asgi_app())


def setup_tracing() -> None:
    """Gửi trace OTLP (Jaeger nhận OTLP gRPC :4317); không đặt endpoint thì không bật (test, chạy local)."""
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    provider = TracerProvider(resource=Resource.create({"service.name": "booking-mcp"}))
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app, excluded_urls="healthz,readyz,metrics")
    HTTPXClientInstrumentor().instrument_client(http)


if os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"):
    setup_tracing()


@app.post("/v1/cancel-risk", response_model=CancelRisk)
async def cancel_risk(req: RiskRequest) -> CancelRisk:
    """REST cho cùng logic của predict_cancellation (load test bằng locust)."""
    try:
        return await _cancel_risk(req.booking_id)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/v1/cancel-risk/batch", response_model=BatchRisk)
async def cancel_risk_batch(req: BatchRequest) -> BatchRisk:
    """Chấm cả lô cho DAG score_bookings: 2 lần đọc Feast + 1 request KServe thay vì mỗi booking 3 lượt."""
    ids, rows, missing = await model_rows(req.booking_ids)
    url = KSERVE_BULK_URL if req.bulk else KSERVE_URL
    probs, version = await _predict(rows, url) if rows else ([], None)
    results = [CancelRisk(booking_id=i, probability=p, model_version=version) for i, p in zip(ids, probs)]
    return BatchRisk(results=results, missing=missing, model_version=version)


@app.get("/healthz")
async def healthz() -> dict:
    """Liveness probe: process còn sống."""
    return {"status": "ok"}


@app.get("/readyz")
async def readyz() -> dict:
    """Readiness probe: chỉ nhận traffic khi đọc được online store."""
    await _features(1, 1)
    return {"status": "ready"}
