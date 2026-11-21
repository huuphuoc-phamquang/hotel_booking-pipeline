"""HTTP proxy bọc `llm_metrics.py` để Prometheus scrape `/metrics` (TTFT, latency, token, PII block)."""
import os

import httpx
from fastapi import FastAPI, HTTPException, Request
from prometheus_client import make_asgi_app

import llm_metrics

if os.getenv("LLM_GATEWAY_URL"):
    llm_metrics.GATEWAY = os.environ["LLM_GATEWAY_URL"]

app = FastAPI(title="llm-proxy", version="0.1.0")
app.mount("/metrics", make_asgi_app())


@app.get("/healthz")
async def healthz() -> dict:
    return {"status": "ok"}


@app.post("/v1/chat/completions")
async def chat_completions(request: Request) -> dict:
    body = await request.json()
    model = body.get("model", "qwen-3b")
    messages = body.get("messages", [])
    agent = request.headers.get("x-agent-name", "kagent")
    headers = {}
    if auth := request.headers.get("authorization"):
        headers["Authorization"] = auth

    try:
        async with httpx.AsyncClient(headers=headers, timeout=60.0) as client:
            content = await llm_metrics.chat(agent=agent, model=model, messages=messages, client=client)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Upstream gateway error: {exc}") from exc

    return {
        "id": "chatcmpl-proxy",
        "object": "chat.completion",
        "model": model,
        "choices": [{"index": 0, "message": {"role": "assistant", "content": content}, "finish_reason": "stop"}],
    }
