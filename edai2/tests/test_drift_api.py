"""Test drift_api/drift_api.py với KSDrift thật của alibi-detect.

  - Fixture         : reference ghi ra file tạm như artifact MLflow, TestClient chạy lifespan để nạp reference
  - EP + BVA        : WINDOW - 1 dòng (chưa test), đúng WINDOW (test), instance sai số cột (422), body rỗng (422)
  - Đúng nghiệp vụ  : lead time cùng phân phối -> không drift; nhân 1,5 như covariate_drift của generator -> drift
"""
import numpy as np
import pytest
from fastapi.testclient import TestClient

import drift_api

RNG = np.random.default_rng(0)
REF = RNG.gamma(2, 10, 5000)                     # lead time ~ gamma(2, 10) như generator


@pytest.fixture
def client(tmp_path, monkeypatch):
    ref = tmp_path / "reference_lead_days.npy"
    np.save(ref, REF)
    monkeypatch.setattr(drift_api, "REF_PATH", str(ref))
    monkeypatch.setattr(drift_api, "WINDOW", 200)
    drift_api.state.update(detector=None, buffer=[])
    with TestClient(drift_api.app) as c:
        yield c


def rows(lead: np.ndarray) -> list[list[float]]:
    return [[float(x), 2, 1, 0, 0.0, 0.0, 0, 0.0, 0, 1] for x in lead]


def test_health(client):
    assert client.get("/healthz").json() == {"status": "ok"}
    assert client.get("/readyz").json() == {"status": "ready"}


def test_not_ready_before_reference():
    drift_api.state["detector"] = None
    assert TestClient(drift_api.app).get("/readyz").status_code == 503


def test_buffers_until_window(client):
    r = client.post("/", json={"instances": rows(RNG.gamma(2, 10, 199))}, headers={"ce-type": "org.kubeflow.serving.inference.request"})
    assert r.json() == {"buffered": 199, "is_drift": None, "p_val": None}
    r = client.post("/", json={"instances": rows(RNG.gamma(2, 10, 1))}).json()
    assert r["buffered"] == 0 and r["is_drift"] is not None


def test_batch_larger_than_window_drains_buffer(client):
    r = client.post("/", json={"instances": rows(RNG.gamma(2, 10, 450))}).json()
    assert r["buffered"] == 50 and r["is_drift"] is not None


def test_same_distribution_no_drift(client):
    r = client.post("/", json={"instances": rows(RNG.gamma(2, 10, 200))}).json()
    assert r["is_drift"] is False and r["p_val"] > 0.05


def test_covariate_drift_detected(client):
    r = client.post("/", json={"instances": rows(RNG.gamma(2, 10, 200) * 1.5)}).json()
    assert r["is_drift"] is True and r["p_val"] < 0.05
    assert drift_api.DRIFT_FLAG.labels("lead_days", drift_api.MODEL_VERSION)._value.get() == 1


@pytest.mark.parametrize("body", [{"instances": []}, {"instances": [[1.0, 2.0]]}, {}])
def test_bad_payload(client, body):
    assert client.post("/", json=body).status_code == 422
