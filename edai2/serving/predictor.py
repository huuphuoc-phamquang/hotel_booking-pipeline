"""Predictor KServe của cancel-risk: như sklearnserver với PREDICT_PROBA (trả [P(không huỷ), P(huỷ)]), thêm
model_version vào response. risk-api lưu version vào gold.booking_risk để drift_monitor đo calibration đúng bản
production và A/B canary so được từng bản (2 revision cùng tên service, chỉ response cho biết bản nào đã chấm).
MODEL_VERSION = version MLflow, gắn lúc build image (serving/Dockerfile).
"""
import argparse
import os

import joblib
import numpy as np
from kserve import Model, ModelServer, model_server

MODEL_VERSION = os.environ["MODEL_VERSION"]


class CancelRisk(Model):
    def __init__(self, name: str, model_dir: str):
        super().__init__(name)
        self.model = joblib.load(os.path.join(model_dir, "model.joblib"))   # ci/fetch_model.py ghi đúng tên này
        self.ready = True

    def predict(self, payload: dict, headers: dict = None, response_headers: dict = None) -> dict:
        proba = self.model.predict_proba(np.asarray(payload["instances"], dtype=float))
        return {"predictions": proba.tolist(), "model_version": MODEL_VERSION}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(parents=[model_server.parser])
    parser.add_argument("--model_dir", default="/mnt/models")
    args, _ = parser.parse_known_args()
    ModelServer().start([CancelRisk(args.model_name, args.model_dir)])
