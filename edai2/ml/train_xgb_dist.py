"""Worker XGBoost phân tán (xgboost.collective) cho TrainJob của Kubeflow Trainer (runtime XGBoost, 2 worker).

Mỗi worker đọc phần dữ liệu của mình (dòng rank::world_size), các worker allreduce histogram (tree_method=hist) nên
ra cùng 1 model như train trên toàn bộ dữ liệu; rank 0 ghi model dạng XGBClassifier (joblib) như step train 1 node
để evaluate_and_register và KServe sklearnserver dùng y nguyên.
Tracker: Trainer đặt DMLC_TRACKER_URI / DMLC_TRACKER_PORT / DMLC_TASK_ID / DMLC_NUM_WORKER cho từng pod;
tests/test_train_xgb_dist.py chạy 2 process với RabitTracker cục bộ theo đúng cách đó.
Chạy: python train_xgb_dist.py <train.parquet> <model.joblib> <cột input, cách nhau dấu phẩy> <nhãn>
"""
import os
import sys

import fsspec
import joblib
import pandas as pd
import xgboost as xgb
from xgboost import collective


def tracker_args_from_env() -> dict:
    return {"dmlc_tracker_uri": os.environ["DMLC_TRACKER_URI"], "dmlc_tracker_port": int(os.environ["DMLC_TRACKER_PORT"]),
            "dmlc_task_id": os.environ.get("DMLC_TASK_ID", os.environ.get("JOB_COMPLETION_INDEX", "0"))}


def train_worker(tracker_args: dict, train_path: str, model_path: str, inputs: list[str], label: str,
                 n_estimators: int = 300, max_depth: int = 6) -> None:
    with collective.CommunicatorContext(**tracker_args):
        rank, world = collective.get_rank(), collective.get_world_size()
        df = pd.read_parquet(train_path, columns=[*inputs, label]).iloc[rank::world]
        params = {"objective": "binary:logistic", "tree_method": "hist", "max_depth": max_depth, "eval_metric": "auc"}
        booster = xgb.train(params, xgb.DMatrix(df[inputs], label=df[label]), num_boost_round=n_estimators)
        if rank == 0:
            clf = xgb.XGBClassifier(n_estimators=n_estimators, max_depth=max_depth)
            clf.load_model(booster.save_raw("json"))
            with fsspec.open(model_path, "wb") as f:              # s3://... trên cluster, đường dẫn file khi test
                joblib.dump(clf, f)


if __name__ == "__main__":
    train_path, model_path, cols, lab = sys.argv[1:5]
    train_worker(tracker_args_from_env(), train_path, model_path, cols.split(","), lab)
