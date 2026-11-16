"""Tải model alias (mặc định production) của cancel-risk từ MLflow vào serving/model/model.joblib cho image KServe.
In ra version để Jenkins gắn tag image = version MLflow (và MODEL_VERSION của drift-api)."""
import argparse
import os

import joblib
import mlflow
from mlflow.tracking import MlflowClient

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--alias", default="production")
    ap.add_argument("--out", default="serving/model")
    a = ap.parse_args()
    mv = MlflowClient().get_model_version_by_alias("cancel-risk", a.alias)
    clf = mlflow.sklearn.load_model(f"models:/cancel-risk@{a.alias}")
    os.makedirs(a.out, exist_ok=True)
    joblib.dump(clf, os.path.join(a.out, "model.joblib"))          # serving/predictor.py nạp model.joblib trong /mnt/models
    print(mv.version)
