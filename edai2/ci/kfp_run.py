"""Compile training_pipeline, upload thành version mới của pipeline cancel-risk-training trên KFP và tạo 1 run.
Jenkins gọi sau khi build image train-base; tham số run truyền dạng key=value (vd since=2025-01-01 until=2025-06-01)."""
import argparse
import sys

import kfp
from kfp import compiler

sys.path.insert(0, "ml")
from training_pipeline import training_pipeline  # noqa: E402

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", required=True)
    ap.add_argument("--version", required=True)            # = commit, để biết run nào chạy code nào
    ap.add_argument("params", nargs="*")
    a = ap.parse_args()
    compiler.Compiler().compile(training_pipeline, "training_pipeline.yaml")
    client = kfp.Client(host=a.host)
    name = "cancel-risk-training"
    pid = client.get_pipeline_id(name)
    if pid is None:
        pid = client.upload_pipeline("training_pipeline.yaml", pipeline_name=name).pipeline_id
    ver = client.upload_pipeline_version("training_pipeline.yaml", pipeline_version_name=a.version, pipeline_id=pid)
    exp = client.create_experiment("cancel-risk")
    run = client.run_pipeline(experiment_id=exp.experiment_id, job_name=f"train-{a.version}", pipeline_id=pid,
                              version_id=ver.pipeline_version_id, params=dict(p.split("=", 1) for p in a.params))
    print(run.run_id)
