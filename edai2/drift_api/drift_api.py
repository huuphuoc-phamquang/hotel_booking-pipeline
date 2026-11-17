"""drift-api: phát hiện drift realtime trên request của cancel-risk (KServe logger -> KNative Broker -> Trigger -> đây).

Phát hiện drift realtime (ngoài phạm vi rubric edai-1/edai-2, giữ làm mở rộng):
  - FastAPI + pydantic + healthcheck k8s : InferenceRequest (payload CloudEvent), /healthz, /readyz, /metrics
  - async                                : handler async, KSDrift chạy trong threadpool để không chặn event loop
  - alibi-detect                         : KSDrift chỉ trên lead_days (cột 0 của MODEL_INPUTS); nights không đổi
                                           theo drift, free_cancel nhị phân không hợp KS
Gom WINDOW request rồi mới test (KS trên vài dòng không có lực). Reference = lead_days của tập train model production
(evaluate_and_register log artifact reference_lead_days.npy, CI chép vào image cùng version model).
"""
import os
from contextlib import asynccontextmanager

import numpy as np
from fastapi import FastAPI, Header, HTTPException
from fastapi.concurrency import run_in_threadpool
from prometheus_client import Counter, Gauge, make_asgi_app
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel, Field

REF_PATH = os.environ.get("REF_PATH", "/app/reference/reference_lead_days.npy")
MODEL_VERSION = os.environ.get("MODEL_VERSION", "unknown")
WINDOW = int(os.environ.get("DRIFT_WINDOW", "500"))
P_VAL = float(os.environ.get("DRIFT_P_VAL", "0.05"))
LEAD_DAYS = 0                                           # vị trí lead_days trong MODEL_INPUTS (ml/training_pipeline.py)
N_INPUTS = 10

DRIFT_P = Gauge("drift_p_value", "p-value KS của cửa sổ gần nhất", ["feature", "model_version"])
DRIFT_FLAG = Gauge("drift_is_drift", "1 nếu cửa sổ gần nhất drift", ["feature", "model_version"])
EVENTS = Counter("drift_events_total", "Số CloudEvent nhận được", ["ce_type"])

state: dict = {"detector": None, "buffer": []}


class InferenceRequest(BaseModel):
    """Body của CloudEvent org.kubeflow.serving.inference.request = request V1 gửi tới KServe."""
    instances: list[list[float]] = Field(min_length=1)


class DriftResult(BaseModel):
    buffered: int
    is_drift: bool | None = None                        # None: chưa đủ WINDOW dòng
    p_val: float | None = None


def build_detector(reference: np.ndarray):
    from alibi_detect.cd import KSDrift
    return KSDrift(reference.reshape(-1, 1).astype(np.float32), p_val=P_VAL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    state["detector"] = build_detector(np.load(REF_PATH))
    yield


app = FastAPI(title="drift-api", lifespan=lifespan)
Instrumentator(excluded_handlers=["/metrics", "/healthz", "/readyz"]).instrument(app)
app.mount("/metrics", make_asgi_app())


@app.post("/", response_model=DriftResult)
async def receive(req: InferenceRequest, ce_type: str = Header("unknown")) -> DriftResult:
    """Nhận 1 CloudEvent (binary mode: header ce-type, body = request); đủ WINDOW dòng thì chạy KS và xoá buffer."""
    EVENTS.labels(ce_type).inc()
    if any(len(row) != N_INPUTS for row in req.instances):
        raise HTTPException(422, f"mỗi instance phải có {N_INPUTS} cột như MODEL_INPUTS")
    buf = state["buffer"]
    buf.extend(row[LEAD_DAYS] for row in req.instances)
    if len(buf) < WINDOW:
        return DriftResult(buffered=len(buf))
    x = np.array(buf[:WINDOW], dtype=np.float32).reshape(-1, 1)
    del buf[:WINDOW]
    data = (await run_in_threadpool(state["detector"].predict, x))["data"]
    p = float(np.min(data["p_val"]))
    DRIFT_P.labels("lead_days", MODEL_VERSION).set(p)
    DRIFT_FLAG.labels("lead_days", MODEL_VERSION).set(int(data["is_drift"]))
    return DriftResult(buffered=len(buf), is_drift=bool(data["is_drift"]), p_val=p)


@app.get("/healthz")
async def healthz() -> dict:
    return {"status": "ok"}


@app.get("/readyz")
async def readyz() -> dict:
    """Chỉ nhận event khi đã nạp reference."""
    if state["detector"] is None:
        raise HTTPException(503, "chưa nạp reference")
    return {"status": "ready"}
