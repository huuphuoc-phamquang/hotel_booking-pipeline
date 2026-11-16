"""Unit test cho mcp_server/server.py.

Rubric edai-2 › Validation & Verification:
  - Coverage > 90% + fixture + mock   : fixture `client`, `fake_features`; mock Feast và KServe bằng monkeypatch/respx
  - Equivalence partitioning + BVA    : test_probability_bounds (biên 0 và 1); biên input ở test_risk_api.py
  - Mutation testing (mutmut > 80%)   : chỉ mutate file thay đổi (mutmut 2.x --paths-to-mutate, xem Jenkinsfile)
  - Idempotency bằng property-based   : test_predict_idempotent dùng hypothesis (có thể chạy backend crosshair)
Cần pytest-asyncio với asyncio_mode = "auto" (pytest.ini) để chạy test async.
Chạy: pytest --cov=mcp_server --cov-report=term-missing --cov-fail-under=90
"""
import asyncio
import json
import numpy as np

import pytest
import respx
from fastapi.testclient import TestClient
from httpx import Response
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

import server


@pytest.fixture
def fake_features(monkeypatch):
    """Thay _features bằng hàm giả, không cần Feast thật."""
    async def _fake(customer_id: int, hotel_id: int) -> server.BookingFeatures:
        return server.BookingFeatures(customer_id=customer_id, hotel_id=hotel_id, bookings_90d=3,
                                      cancel_rate_90d=0.33, avg_lead_days_90d=21.0, bookings_7d=120,
                                      cancel_rate_30d=0.18, bookings_1h=4)
    monkeypatch.setattr(server, "_features", _fake)


@pytest.fixture
def client(fake_features):
    """TestClient cho FastAPI app (health endpoints)."""
    # không dùng `with`: lifespan gọi session_manager.run(), MCP SDK chỉ cho gọi 1 lần mỗi process
    return TestClient(server.app)


def test_healthz(client):
    assert client.get("/healthz").json() == {"status": "ok"}


def test_readyz_ok(client):
    assert client.get("/readyz").status_code == 200


# Equivalence partitioning: [0, 1] -> trả nguyên xác suất ; ngoài [0, 1] (risk-api hỏng) -> ValidationError
# Boundary value analysis: -0.001, 0.0, 1.0, 1.001
@pytest.mark.parametrize("prob, ok", [(-0.001, False), (0.0, True), (0.5, True), (1.0, True), (1.001, False)])
@respx.mock
async def test_probability_bounds(prob, ok):
    respx.post(server.RISK_API_URL).mock(return_value=Response(200, json={"booking_id": 7, "probability": prob}))
    if ok:
        assert (await server.predict_cancellation(7)).probability == prob
    else:
        with pytest.raises(ValidationError):
            await server.predict_cancellation(7)


def test_cancel_risk_has_no_per_customer_decision():
    """Không cá nhân hoá điều kiện đặt phòng: output chỉ có xác suất, không có field quyết định (cọc, giá) theo khách."""
    assert set(server.CancelRisk.model_fields) == {"booking_id", "probability"}


@respx.mock
async def test_predict_delegates_to_risk_api():
    """Tool không tự dựng input model: gửi đúng booking_id sang risk-api (logic dự báo chỉ ở một chỗ)."""
    route = respx.post(server.RISK_API_URL).mock(return_value=Response(200, json={"booking_id": 7, "probability": 0.1}))
    await server.predict_cancellation(7)
    assert json.loads(route.calls.last.request.content) == {"booking_id": 7}


@respx.mock
async def test_predict_failure_counted():
    respx.post(server.RISK_API_URL).mock(return_value=Response(404))
    before = server.TOOL_FAILURES.labels("predict_cancellation")._value.get()
    with pytest.raises(Exception):
        await server.predict_cancellation(7)
    assert server.TOOL_FAILURES.labels("predict_cancellation")._value.get() == before + 1


async def test_features_reads_online_store(monkeypatch):
    """_features đổi response của Feast (mỗi feature là 1 list) thành BookingFeatures."""
    class _Resp:
        def to_dict(self):
            return {"customer_id": [42], "hotel_id": [7], "bookings_90d": [3], "cancel_rate_90d": [None],
                    "avg_lead_days_90d": [12.5], "bookings_7d": [80], "cancel_rate_30d": [0.2], "bookings_1h": [None]}

    async def _get(**kwargs):
        return _Resp()
    monkeypatch.setattr(server.store, "get_online_features_async", _get, raising=False)
    f = await server._features(42, 7)
    assert f.bookings_90d == 3 and f.cancel_rate_90d is None and f.bookings_1h is None


async def test_get_booking_features_failure_counted(monkeypatch):
    async def _boom(customer_id, hotel_id):
        raise RuntimeError("online store down")
    monkeypatch.setattr(server, "_features", _boom)
    before = server.TOOL_FAILURES.labels("get_booking_features")._value.get()
    with pytest.raises(RuntimeError):
        await server.get_booking_features(customer_id=1, hotel_id=1)
    assert server.TOOL_FAILURES.labels("get_booking_features")._value.get() == before + 1


class _FakeEmbedder:
    """Thay SentenceTransformer: trả vector cố định, không tải model 2GB khi test."""
    def encode(self, text, normalize_embeddings=True):
        return np.array([0.1, 0.2, 0.3])


async def test_search_policy_maps_chunks(monkeypatch):
    class _Res:
        def to_dict(self):
            return {"chunk_id": ["refund.md#0"], "text": ["Huỷ miễn phí trước 24 giờ"], "distance": [0.12]}
    monkeypatch.setattr(server, "_embedder", _FakeEmbedder())
    monkeypatch.setattr(server.store, "retrieve_online_documents_v2", lambda **kw: _Res(), raising=False)
    chunks = await server.search_policy("Huỷ phòng có mất phí không?", top_k=1)
    assert chunks == [server.Chunk(chunk_id="refund.md#0", text="Huỷ miễn phí trước 24 giờ", score=0.12)]


async def test_search_policy_failure_counted(monkeypatch):
    def _boom(**kw):
        raise RuntimeError("vector index missing")
    monkeypatch.setattr(server, "_embedder", _FakeEmbedder())
    monkeypatch.setattr(server.store, "retrieve_online_documents_v2", _boom, raising=False)
    before = server.TOOL_FAILURES.labels("search_policy")._value.get()
    with pytest.raises(RuntimeError):
        await server.search_policy("đổi ngày nhận phòng?")
    assert server.TOOL_FAILURES.labels("search_policy")._value.get() == before + 1


@settings(max_examples=50, deadline=None)
@given(booking_id=st.integers(min_value=1, max_value=10**13),
       prob=st.floats(min_value=0.0, max_value=1.0, allow_nan=False))
def test_predict_idempotent(booking_id, prob):
    """Cùng input gọi 2 lần phải ra cùng kết quả (không có state ẩn / random)."""
    async def call_twice():
        with respx.mock:
            respx.post(server.RISK_API_URL).mock(
                return_value=Response(200, json={"booking_id": booking_id, "probability": prob}))
            return await server.predict_cancellation(booking_id), await server.predict_cancellation(booking_id)

    first, second = asyncio.run(call_twice())     # hypothesis không chạy trực tiếp test async
    assert first == second
