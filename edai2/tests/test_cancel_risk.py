"""Unit test cho phần dự báo của mcp_server/server.py: feature theo booking_id từ Feast online rồi gọi KServe
(tool predict_cancellation, REST /v1/cancel-risk và /v1/cancel-risk/batch).

Rubric edai-2 › Validation & Verification:
  - Coverage > 90% + fixture + mock   : fixture `online` giả Feast, respx giả KServe
  - Equivalence partitioning + BVA    : test_probability_bounds (biên 0 và 1), test_booking_id_bounds
  - Idempotency bằng property-based   : test_cancel_risk_idempotent (hypothesis)
Chạy: PYTHONPATH=mcp_server pytest tests/test_cancel_risk.py --cov=mcp_server --cov-fail-under=90
"""
import asyncio
import json
from unittest.mock import patch

import pytest
import respx
from fastapi.testclient import TestClient
from httpx import Response
from hypothesis import given, settings
from hypothesis import strategies as st

import server

BOOKING = {"customer_id": 42, "hotel_id": 7, "lead_days": 30, "nights": 2, "free_cancel": 1, "loyalty_tier": 2}
CONTEXT = {"bookings_90d": 3, "cancel_rate_90d": 0.33, "avg_lead_days_90d": 21.0, "bookings_7d": 120,
           "cancel_rate_30d": 0.18}


def fake_online(booking: dict | None, context: dict):
    """Giả _online: booking_attributes theo booking_id, feature khách/khách sạn theo (customer_id, hotel_id)."""
    async def _online(features, entities):
        return [(booking or {k: None for k in BOOKING}) if "booking_id" in e else context for e in entities]
    return _online


@pytest.fixture
def online(monkeypatch):
    monkeypatch.setattr(server, "_online", fake_online(BOOKING, CONTEXT))


@pytest.fixture
def client(online):
    return TestClient(server.app)


@respx.mock
def test_sends_features_in_model_order(client):
    """Thứ tự gửi KServe phải khớp MODEL_INPUTS lúc train; sai thứ tự model vẫn chạy nhưng dự đoán sai."""
    route = respx.post(server.KSERVE_URL).mock(
        return_value=Response(200, json={"predictions": [[0.9, 0.1]], "model_version": "13"}))
    r = client.post("/v1/cancel-risk", json={"booking_id": 7})
    assert r.json() == {"booking_id": 7, "probability": 0.1, "model_version": "13"}
    assert json.loads(route.calls.last.request.content)["instances"][0] == [30, 2, 1, 3, 0.33, 21.0, 120, 0.18, 1, 2]


@respx.mock
def test_new_customer_filled_like_training(monkeypatch):
    """Khách chưa có dòng customer_booking_stats: điền 0 + has_customer_history = 0, giống load_from_feast."""
    monkeypatch.setattr(server, "_online", fake_online(BOOKING, {k: None for k in CONTEXT}))
    route = respx.post(server.KSERVE_URL).mock(return_value=Response(200, json={"predictions": [[0.9, 0.1]]}))
    TestClient(server.app).post("/v1/cancel-risk", json={"booking_id": 7})
    assert json.loads(route.calls.last.request.content)["instances"][0] == [30, 2, 1, 0, 0.0, 0.0, 0, 0.0, 0, 2]


def test_unknown_booking_is_404(monkeypatch):
    monkeypatch.setattr(server, "_online", fake_online(None, CONTEXT))
    assert TestClient(server.app).post("/v1/cancel-risk", json={"booking_id": 7}).status_code == 404


# BVA booking_id: 0 không hợp lệ, 1 hợp lệ
@pytest.mark.parametrize("booking_id, status", [(0, 422), (-1, 422), ("abc", 422)])
def test_booking_id_bounds(client, booking_id, status):
    assert client.post("/v1/cancel-risk", json={"booking_id": booking_id}).status_code == status


# EP + BVA cho output của KServe: trong [0, 1] trả nguyên; ngoài [0, 1] là model hỏng -> lỗi, không trả về
@pytest.mark.parametrize("prob, ok", [(-0.001, False), (0.0, True), (0.5, True), (1.0, True), (1.001, False)])
@respx.mock
async def test_probability_bounds(online, prob, ok):
    respx.post(server.KSERVE_URL).mock(return_value=Response(200, json={"predictions": [[1 - prob, prob]]}))
    if ok:
        assert (await server.cancel_risk(server.RiskRequest(booking_id=7))).probability == prob
    else:
        with pytest.raises(ValueError):
            await server.cancel_risk(server.RiskRequest(booking_id=7))


@respx.mock
async def test_label_only_response_rejected(online):
    """Runtime trả nhãn 0/1 (vd sklearnserver thiếu PREDICT_PROBA): phải lỗi thay vì coi nhãn là xác suất."""
    respx.post(server.KSERVE_URL).mock(return_value=Response(200, json={"predictions": [1]}))
    with pytest.raises(TypeError):
        await server.cancel_risk(server.RiskRequest(booking_id=7))


@respx.mock
async def test_kserve_error_propagates(online):
    respx.post(server.KSERVE_URL).mock(return_value=Response(503))
    with pytest.raises(Exception):
        await server.cancel_risk(server.RiskRequest(booking_id=7))


async def test_online_splits_rows(monkeypatch):
    """_online đổi response của Feast (mỗi feature là 1 list) thành 1 dict / entity, giữ thứ tự."""
    class _Resp:
        def to_dict(self):
            return {"booking_id": [7, 8], "lead_days": [30, 5], "loyalty_tier": [None, 1]}

    async def _get(**kwargs):
        return _Resp()
    monkeypatch.setattr(server.store, "get_online_features_async", _get, raising=False)
    assert await server._online(["booking_attributes:lead_days"], [{"booking_id": 7}, {"booking_id": 8}]) == \
        [{"booking_id": 7, "lead_days": 30, "loyalty_tier": None}, {"booking_id": 8, "lead_days": 5, "loyalty_tier": 1}]


@respx.mock
def test_batch_one_kserve_call_and_missing(monkeypatch):
    """Lô 3 booking, 1 chưa có trên online store: 1 request KServe 2 dòng, booking thiếu nằm ở missing."""
    async def _online(features, entities):
        if "booking_id" in entities[0]:
            return [BOOKING if e["booking_id"] != 9 else {k: None for k in BOOKING} for e in entities]
        return [CONTEXT for _ in entities]
    monkeypatch.setattr(server, "_online", _online)
    route = respx.post(server.KSERVE_URL).mock(
        return_value=Response(200, json={"predictions": [[0.9, 0.1], [0.3, 0.7]], "model_version": "14"}))
    r = TestClient(server.app).post("/v1/cancel-risk/batch", json={"booking_ids": [7, 9, 8]})
    assert r.json() == {"results": [{"booking_id": 7, "probability": 0.1, "model_version": "14"},
                                    {"booking_id": 8, "probability": 0.7, "model_version": "14"}],
                        "missing": [9], "model_version": "14"}
    assert route.call_count == 1 and len(json.loads(route.calls.last.request.content)["instances"]) == 2


def test_batch_all_missing_skips_kserve(monkeypatch):
    monkeypatch.setattr(server, "_online", fake_online(None, CONTEXT))
    r = TestClient(server.app).post("/v1/cancel-risk/batch", json={"booking_ids": [7]})
    assert r.json() == {"results": [], "missing": [7], "model_version": None}


@pytest.mark.parametrize("ids", [[], list(range(1, 1002))])
def test_batch_size_bounds(client, ids):
    assert client.post("/v1/cancel-risk/batch", json={"booking_ids": ids}).status_code == 422


@settings(max_examples=50, deadline=None)
@given(booking_id=st.integers(min_value=1, max_value=10**13), prob=st.floats(min_value=0.0, max_value=1.0))
def test_cancel_risk_idempotent(booking_id, prob):
    """Cùng booking gọi 2 lần ra cùng kết quả (không state ẩn, không random)."""
    async def call_twice():
        with patch.object(server, "_online", fake_online(BOOKING, CONTEXT)), respx.mock:
            respx.post(server.KSERVE_URL).mock(return_value=Response(200, json={"predictions": [[1 - prob, prob]]}))
            req = server.RiskRequest(booking_id=booking_id)
            return await server.cancel_risk(req), await server.cancel_risk(req)

    first, second = asyncio.run(call_twice())
    assert first == second


@respx.mock
def test_metrics_count_requests(client):
    """/metrics có http_requests_total theo handler + status (dashboard Grafana và KEDA dùng)."""
    respx.post(server.KSERVE_URL).mock(return_value=Response(200, json={"predictions": [[0.9, 0.1]]}))
    client.post("/v1/cancel-risk", json={"booking_id": 7})
    body = client.get("/metrics/").text
    assert 'http_requests_total{handler="/v1/cancel-risk",method="POST",status="2xx"}' in body


def test_tracing_setup(monkeypatch):
    """setup_tracing gắn FastAPI + httpx instrumentation và span feast.online không lỗi (exporter không cần chạy)."""
    pytest.importorskip("opentelemetry.instrumentation.fastapi")
    server.setup_tracing()
    assert getattr(server.app, "_is_instrumented_by_opentelemetry", False)


@respx.mock
def test_batch_bulk_skips_logged_service(monkeypatch):
    """bulk=True (rescore_active) gọi cancel-risk-bulk, không chạm InferenceService có KServe logger."""
    monkeypatch.setattr(server, "_online", fake_online(BOOKING, CONTEXT))
    logged = respx.post(server.KSERVE_URL).mock(return_value=Response(200, json={"predictions": [[0.9, 0.1]]}))
    bulk = respx.post(server.KSERVE_BULK_URL).mock(
        return_value=Response(200, json={"predictions": [[0.9, 0.1]], "model_version": "14"}))
    r = TestClient(server.app).post("/v1/cancel-risk/batch", json={"booking_ids": [7], "bulk": True})
    assert r.json()["model_version"] == "14" and bulk.call_count == 1 and logged.call_count == 0


@respx.mock
async def test_tool_uses_same_path(online):
    """Tool predict_cancellation và REST dùng chung model_rows + KServe: cùng input, cùng kết quả."""
    route = respx.post(server.KSERVE_URL).mock(return_value=Response(200, json={"predictions": [[0.6, 0.4]]}))
    assert (await server.predict_cancellation(7)).probability == 0.4
    assert json.loads(route.calls.last.request.content)["instances"][0] == [30, 2, 1, 3, 0.33, 21.0, 120, 0.18, 1, 2]


async def test_tool_unknown_booking_counted(monkeypatch):
    monkeypatch.setattr(server, "_online", fake_online(None, CONTEXT))
    before = server.TOOL_FAILURES.labels("predict_cancellation")._value.get()
    with pytest.raises(LookupError):
        await server.predict_cancellation(7)
    assert server.TOOL_FAILURES.labels("predict_cancellation")._value.get() == before + 1


@settings(max_examples=50, deadline=None)
@given(booking_id=st.integers(min_value=1, max_value=10**13), prob=st.floats(min_value=0.0, max_value=1.0))
def test_predict_tool_idempotent(booking_id, prob):
    """Tool MCP gọi 2 lần cùng booking ra cùng kết quả."""
    async def call_twice():
        with patch.object(server, "_online", fake_online(BOOKING, CONTEXT)), respx.mock:
            respx.post(server.KSERVE_URL).mock(return_value=Response(200, json={"predictions": [[1 - prob, prob]]}))
            return await server.predict_cancellation(booking_id), await server.predict_cancellation(booking_id)

    first, second = asyncio.run(call_twice())
    assert first == second
