"""Train phân tán 2 worker (ml/train_xgb_dist.py) với RabitTracker cục bộ = cách Kubeflow Trainer chạy 2 pod.

So với XGBClassifier train 1 node trên toàn bộ dữ liệu (step train hiện tại): AUC gần như bằng nhau, model rank 0
ghi ra predict_proba được (dạng KServe sklearnserver dùng)."""
import multiprocessing as mp

import joblib
import numpy as np
import pandas as pd
import pytest

xgb = pytest.importorskip("xgboost")
from sklearn.metrics import roc_auc_score  # noqa: E402
from xgboost.tracker import RabitTracker  # noqa: E402

from train_xgb_dist import train_worker  # noqa: E402

INPUTS = ["lead_days", "free_cancel", "loyalty_tier"]


def data(n=6000, seed=0):
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({"lead_days": rng.gamma(2, 10, n), "free_cancel": rng.integers(0, 2, n),
                       "loyalty_tier": rng.integers(0, 4, n)})
    logit = -2 + 0.8 * np.log1p(df["lead_days"]) / 3 * 3 + 1.2 * df["free_cancel"] - 0.5 * df["loyalty_tier"]
    df["is_cancelled"] = (rng.random(n) < 1 / (1 + np.exp(-logit))).astype(int)
    return df


def test_two_workers_match_single_node(tmp_path):
    train, valid = data(), data(seed=1)
    train.to_parquet(tmp_path / "train.parquet")
    tracker = RabitTracker(n_workers=2, host_ip="127.0.0.1")
    tracker.start()
    args = tracker.worker_args()
    ctx = mp.get_context("spawn")
    procs = [ctx.Process(target=train_worker, args=({**args, "dmlc_task_id": str(r)}, str(tmp_path / "train.parquet"),
                                                     str(tmp_path / "model.joblib"), INPUTS, "is_cancelled", 50, 4))
             for r in range(2)]
    for p in procs:
        p.start()
    for p in procs:
        p.join(120)
    tracker.wait_for(60)
    assert [p.exitcode for p in procs] == [0, 0]
    dist = joblib.load(tmp_path / "model.joblib")
    single = xgb.XGBClassifier(n_estimators=50, max_depth=4, tree_method="hist").fit(train[INPUTS], train["is_cancelled"])
    auc_d = roc_auc_score(valid["is_cancelled"], dist.predict_proba(valid[INPUTS])[:, 1])
    auc_s = roc_auc_score(valid["is_cancelled"], single.predict_proba(valid[INPUTS])[:, 1])
    assert dist.predict_proba(valid[INPUTS]).shape == (len(valid), 2) and abs(auc_d - auc_s) < 0.01
