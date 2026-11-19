"""Proxy đo telemetry cho lời gọi LLM (đặt giữa agent và agentgateway, hoặc dùng làm thư viện trong agent).

Rubric edai-2 › Observability › LLM-related telemetry data:
  - token metrics: input / output / total tokens mỗi request    -> llm_tokens_total{kind}
  - total round-trip time cho 1 lần generate                    -> llm_request_seconds
  - TTFT (time to first token)                                  -> llm_ttft_seconds
  - tần suất prompt bị chặn vì PII                              -> llm_pii_blocked_total
Rubric edai-2 › Agent-related telemetry: agent_calls_total{agent} (tool calls đếm trong mcp_server).
Prometheus scrape /metrics -> Grafana dashboard. Trace gửi qua OpenTelemetry tới Jaeger.
"""
import json
import re
import time

import httpx
from opentelemetry import trace
from prometheus_client import Counter, Histogram

GATEWAY = "http://agentgateway.gateway.svc.cluster.local:3000/v1/chat/completions"

TOKENS = Counter("llm_tokens_total", "Số token", ["model", "kind"])          # kind = input|output|total
LATENCY = Histogram("llm_request_seconds", "Round-trip 1 lần generate", ["model"],
                    buckets=(0.25, 0.5, 1, 2, 4, 8, 16, 32))
TTFT = Histogram("llm_ttft_seconds", "Time to first token", ["model"], buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 4))
PII_BLOCKED = Counter("llm_pii_blocked_total", "Prompt bị chặn vì chứa PII", ["pii_type"])
AGENT_CALLS = Counter("agent_calls_total", "Số lần mỗi agent được gọi", ["agent"])

PII_PATTERNS = {                                          # khách đặt phòng hay dán giấy tờ vào chat
    "cccd": re.compile(r"\b0\d{11}\b"),                     # căn cước 12 số
    "passport_vn": re.compile(r"\b[A-Z]\d{7}\b"),
    "phone_vn": re.compile(r"\b0\d{9}\b"),
    "email": re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"),
}
# Số thẻ 13-16 chữ số; booking_id cũng là số 11-13 chữ số nên chỉ tính là thẻ khi qua Luhn, và bỏ qua số đứng sau
# "BK-" (mọi tool/UI hiển thị mã booking dạng BK-<id>; Luhn một mình vẫn để lọt ~10% số ngẫu nhiên)
CARD = re.compile(r"(?<!BK-)(?<![\d-])(?:\d[ -]?){12,15}\d(?![\d-])")
tracer = trace.get_tracer("llm-proxy")


def luhn_ok(number: str) -> bool:
    digits = [int(c) for c in number if c.isdigit()][::-1]
    return sum(d if i % 2 == 0 else (d * 2 - 9 if d > 4 else d * 2) for i, d in enumerate(digits)) % 10 == 0


def detect_pii(text: str) -> str | None:
    """Trả về loại PII đầu tiên tìm thấy, None nếu sạch."""
    if any(luhn_ok(m.group()) for m in CARD.finditer(text)):
        return "card"
    for name, pat in PII_PATTERNS.items():
        if pat.search(text):
            return name
    return None


async def chat(agent: str, model: str, messages: list[dict], client: httpx.AsyncClient) -> str:
    """Gọi LLM dạng stream, đo TTFT/latency/token, chặn prompt có PII."""
    AGENT_CALLS.labels(agent).inc()
    pii = detect_pii(" ".join(m["content"] for m in messages))
    if pii:
        PII_BLOCKED.labels(pii).inc()
        raise ValueError(f"Prompt chứa PII ({pii}), đã chặn")

    with tracer.start_as_current_span("llm.chat", attributes={"agent": agent, "model": model}):
        start, first, parts, usage = time.perf_counter(), None, [], {}
        body = {"model": model, "messages": messages, "stream": True, "stream_options": {"include_usage": True}}
        async with client.stream("POST", GATEWAY, json=body) as r:
            if r.status_code >= 400:                  # 401/429/503 của gateway: không đếm như lần gọi thành công
                await r.aread()
                r.raise_for_status()
            async for line in r.aiter_lines():
                if not line.startswith("data: ") or line == "data: [DONE]":
                    continue
                chunk = json.loads(line[6:])
                if chunk.get("choices") and chunk["choices"][0]["delta"].get("content"):
                    if first is None:
                        first = time.perf_counter()
                        TTFT.labels(model).observe(first - start)
                    parts.append(chunk["choices"][0]["delta"]["content"])
                if chunk.get("usage"):
                    usage = chunk["usage"]
        LATENCY.labels(model).observe(time.perf_counter() - start)
        TOKENS.labels(model, "input").inc(usage.get("prompt_tokens", 0))
        TOKENS.labels(model, "output").inc(usage.get("completion_tokens", 0))
        TOKENS.labels(model, "total").inc(usage.get("total_tokens", 0))
        return "".join(parts)
