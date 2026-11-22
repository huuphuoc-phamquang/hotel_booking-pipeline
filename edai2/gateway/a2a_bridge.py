"""MCP bridge cho coordinator-agent gọi data-agent và policy-agent qua A2A của agentgateway.

Thay vì kagent gọi thẳng pod agent con trong cluster (bỏ qua gateway), coordinator-agent gọi tool MCP
`delegate_data_agent` / `delegate_policy_agent` -> agentgateway (/mcp-a2a) -> a2a-bridge ->
agentgateway (/a2a/<agent>/) kèm JWT của coordinator-agent và OTel traceparent.
"""
import os
import uuid
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from opentelemetry import trace

GATEWAY_BASE = os.environ.get("GATEWAY_BASE", "http://agentgateway.gateway.svc.cluster.local:3000").rstrip("/")
COORDINATOR_AUTH = os.environ.get("COORDINATOR_AUTH", "")

mcp = FastMCP(
    "coordinator-a2a",
    stateless_http=True,
    streamable_http_path="/",
    transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
)
http = httpx.AsyncClient(timeout=60.0)


def _extract_a2a_text(payload: dict) -> str:
    """Rút văn bản trả lời từ kết quả JSON-RPC A2A (artifacts hoặc status.message)."""
    res = payload.get("result") or {}
    state = (res.get("status") or {}).get("state", "")
    parts: list[str] = []
    for art in res.get("artifacts") or []:
        for p in art.get("parts") or []:
            if p.get("text"):
                parts.append(p["text"])
    if not parts:
        msg = (res.get("status") or {}).get("message") or {}
        for p in msg.get("parts") or []:
            if p.get("text"):
                parts.append(p["text"])
    text = "\n".join(parts).strip()
    if state == "input-required":
        return f"[Yêu cầu người duyệt (HITL - {state})]: {text}"
    return text or str(res)


async def _call_a2a(agent: str, question: str) -> str:
    url = f"{GATEWAY_BASE}/a2a/{agent}/"
    body = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "message/send",
        "params": {
            "message": {
                "role": "user",
                "messageId": str(uuid.uuid4()),
                "parts": [{"kind": "text", "text": question}],
            }
        },
    }
    headers = {"Content-Type": "application/json"}
    if COORDINATOR_AUTH:
        headers["Authorization"] = COORDINATOR_AUTH
    resp = await http.post(url, json=body, headers=headers)
    resp.raise_for_status()
    return _extract_a2a_text(resp.json())


@mcp.tool()
async def delegate_data_agent(question: str) -> str:
    """Chuyển câu hỏi về lịch sử khách hàng và nhu cầu khách sạn tới data-agent qua A2A Gateway."""
    return await _call_a2a("data-agent", question)


@mcp.tool()
async def delegate_policy_agent(question: str) -> str:
    """Chuyển câu hỏi về xác suất huỷ, chính sách hoàn tiền hoặc overbooking tới policy-agent qua A2A Gateway."""
    return await _call_a2a("policy-agent", question)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with mcp.session_manager.run():
        yield
    await http.aclose()


app = FastAPI(title="a2a-bridge", lifespan=lifespan)
app.mount("/mcp", mcp.streamable_http_app())


@app.get("/healthz")
async def healthz() -> dict:
    return {"status": "ok"}


if os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"):
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    provider = TracerProvider(resource=Resource.create({"service.name": "a2a-bridge"}))
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app, excluded_urls="healthz")
    HTTPXClientInstrumentor().instrument_client(http)
