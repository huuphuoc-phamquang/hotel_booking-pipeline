"""llm_proxy: chuyển tiếp chat sang llm_metrics.chat, đổi lỗi PII thành 400 và lỗi gateway thành 502."""
import importlib

import httpx
import pytest

import llm_metrics
import llm_proxy


@pytest.fixture
def client():
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=llm_proxy.app), base_url="http://proxy")


async def test_healthz(client):
    assert (await client.get("/healthz")).json() == {"status": "ok"}


async def test_chat_forwards_agent_model_and_auth(client, monkeypatch):
    seen = {}

    async def fake_chat(agent, model, messages, client):
        seen.update(agent=agent, model=model, messages=messages, auth=client.headers.get("authorization"))
        return "K = 2"

    monkeypatch.setattr(llm_metrics, "chat", fake_chat)
    r = await client.post("/v1/chat/completions", headers={"x-agent-name": "policy-agent", "authorization": "Bearer t"},
                          json={"model": "qwen-booking-v2", "messages": [{"role": "user", "content": "hi"}]})
    assert r.status_code == 200
    assert r.json()["choices"][0]["message"]["content"] == "K = 2"
    assert seen == {"agent": "policy-agent", "model": "qwen-booking-v2",
                    "messages": [{"role": "user", "content": "hi"}], "auth": "Bearer t"}


async def test_chat_defaults_without_headers(client, monkeypatch):
    async def fake_chat(agent, model, messages, client):
        assert (agent, model, messages, client.headers.get("authorization")) == ("kagent", "qwen-3b", [], None)
        return ""

    monkeypatch.setattr(llm_metrics, "chat", fake_chat)
    assert (await client.post("/v1/chat/completions", json={})).json()["model"] == "qwen-3b"


@pytest.mark.parametrize("exc, status", [(ValueError("prompt chứa PII: card"), 400),
                                         (httpx.ConnectError("gateway down"), 502)])
async def test_chat_maps_errors(client, monkeypatch, exc, status):
    async def fake_chat(agent, model, messages, client):
        raise exc

    monkeypatch.setattr(llm_metrics, "chat", fake_chat)
    assert (await client.post("/v1/chat/completions", json={"messages": []})).status_code == status


def test_gateway_url_from_env(monkeypatch):
    monkeypatch.setenv("LLM_GATEWAY_URL", "http://gw:3000/v1/chat/completions")
    monkeypatch.setattr(llm_metrics, "GATEWAY", llm_metrics.GATEWAY)      # khôi phục sau test
    importlib.reload(llm_proxy)
    assert llm_metrics.GATEWAY == "http://gw:3000/v1/chat/completions"
