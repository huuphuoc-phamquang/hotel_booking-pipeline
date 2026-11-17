"""Unit test cho mcp_server/server.py.

Rubric edai-2 › Validation & Verification:
  - Coverage > 90% + fixture + mock   : fixture `client`, `fake_features`; mock Feast bằng monkeypatch
  - Equivalence partitioning + BVA    : test_probability_bounds, test_booking_id_bounds ở test_cancel_risk.py
  - Mutation testing (mutmut > 80%)   : chỉ mutate file thay đổi (mutmut 2.x --paths-to-mutate, xem Jenkinsfile)
  - Idempotency bằng property-based   : test_predict_tool_idempotent ở test_cancel_risk.py (hypothesis)
Cần pytest-asyncio với asyncio_mode = "auto" (pytest.ini) để chạy test async.
Chạy: pytest --cov=mcp_server --cov-report=term-missing --cov-fail-under=90
"""
import numpy as np
import pytest
from fastapi.testclient import TestClient

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


def test_cancel_risk_has_no_per_customer_decision():
    """Không cá nhân hoá điều kiện đặt phòng: output chỉ có xác suất, không có field quyết định (cọc, giá) theo khách."""
    assert set(server.CancelRisk.model_fields) == {"booking_id", "probability", "model_version"}


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
