"""Kubeflow Pipeline (KFP v2) huấn luyện model dự đoán booking bị huỷ, log và gắn alias trên MLflow.

Rubric edai-2 › ML Pipelines › Training Pipelines:
  - >= 4 step: load_from_feast -> split_by_time -> train -> evaluate (+ register)
  - Training phân tán: distributed=True thì step train tạo Kubeflow Trainer TrainJob runtime XGBoost 2 node
    (ml/train_xgb_dist.py, xgboost.collective); evaluate dùng model y như bản 1 node
  - Lưu model, data, metadata lên MLflow; tự gắn tag release=latest; alias `production` khi qua cổng ở evaluate
Split theo thời gian (không random) để tránh rò thông tin tương lai vào train.
Nhãn is_cancelled do generator sinh từ công thức đã biết (edai1/generator/config.yaml › label), nên có thể so
feature importance với hệ số thật. Từ 2025-06-01 generator đổi cả hệ số nhãn (concept drift) lẫn phân phối lead time
(covariate drift): drift_monitor / drift-api bắt được trên feature, tỉ lệ huỷ dự báo lệch khỏi thực tế ->
retrain với since = ngày phát hiện, khi booking sau mốc đã chín nhãn (calibration lệch chứ AUC gần như không đổi).
"""
from kfp import compiler, dsl, kubernetes
from kfp.dsl import Dataset, Input, Metrics, Model, Output

import os

BASE_IMAGE = os.getenv("TRAIN_BASE_IMAGE", "asia-southeast1-docker.pkg.dev/hotel-booking-edai2/booking/ml/train-base:1.4")   # có sẵn ml/data_version.py + pyiceberg[sql-postgres,s3fs]
MLFLOW_URI = "http://mlflow.mlops.svc.cluster.local:5000"
MODEL_NAME = "cancel-risk"
# Cổng promote: AUC >= MIN_AUC (sàn chặn model hỏng), lệch calibration <= MAX_CALIB_GAP (overbooking dùng thẳng
# xác suất), và Brier <= bản production chấm trên cùng tập validation. So Brier chứ không so AUC: sau drift AUC của
# bản cũ gần như giữ nguyên, chỉ calibration lệch (docs/problem_design.md mục 4, 6). MIN_AUC là sàn chặn model hỏng, đặt dưới mức
# model đạt trên generator (số đo nằm trong docs, chạy lại generator/profile_data.py khi đổi config).
MIN_AUC = 0.60
MAX_CALIB_GAP = 0.03
FEATURES = ["customer_booking_stats:bookings_90d", "customer_booking_stats:cancel_rate_90d",
            "customer_booking_stats:avg_lead_days_90d", "hotel_demand:bookings_7d",
            "hotel_demand:cancel_rate_30d"]
# Thứ tự cột đưa vào model; mcp_server/server.py (model_rows) dựng request theo đúng thứ tự này.
# Không có bookings_1h: hotel_realtime chưa có lịch sử cho dữ liệu train (toàn 0 lúc train, khác 0 lúc serve).
# has_customer_history = bookings_90d > 1: snapshot booking_date + 1 đã đếm chính booking này, nên > 0 luôn đúng lúc
# train; > 1 = khách còn booking khác trong 90 ngày. Train và serve cùng điền thiếu bằng 0.
MODEL_INPUTS = ["lead_days", "nights", "free_cancel", "bookings_90d", "cancel_rate_90d", "avg_lead_days_90d",
                "bookings_7d", "cancel_rate_30d", "has_customer_history", "loyalty_tier"]
LABEL = "is_cancelled"

# event_timestamp = booking_date + 1 ngày: point-in-time join lấy snapshot DP3 của chính ngày đặt (gồm booking này,
# chưa huỷ), đúng snapshot online mà score_bookings dùng khi chấm (sau khi materialize ngày ds). Booking huỷ ngay
# trong ngày đặt hoặc nhận phòng ngay trong ngày đặt bị loại ở cả hai phía (score_bookings không chấm) nên snapshot
# không lộ nhãn và hai phía cùng phân phối lead_days.
LABEL_SQL = """
SELECT f.booking_id, c.customer_id, h.hotel_id, (f.booking_date + 1)::timestamp AS event_timestamp,
       f.lead_days, f.nights, (f.cancellation_policy = 'flexible')::int AS free_cancel, c.loyalty_tier,
       l.is_cancelled
FROM gold.fact_bookings f
JOIN gold.labels_cancel l USING (booking_id)
JOIN gold.dim_customer c USING (customer_key)
JOIN gold.dim_hotel h USING (hotel_key)
-- nhãn (booking_id, is_cancelled) lấy từ view gold.labels_cancel (cancelled_at, không từ status lúc chụp)
-- cửa sổ [since, until); nhãn chỉ chắc chắn khi đã qua ngày nhận phòng trước until (huỷ chỉ xảy ra trước checkin).
-- Dừng booking_date ở until - 90 ngày: nếu không, cuối cửa sổ chỉ còn booking lead ngắn (lead dài chưa tới checkin)
-- và split_by_time đưa đúng phần lệch đó vào validation. 90 = LABEL_MATURITY_DAYS của dags/drift_stats.py.
WHERE f.booking_date >= '{since}' AND f.booking_date < '{until}'::date - 90 AND f.checkin_date < '{until}'
  AND f.checkin_date > f.booking_date
  AND (f.cancelled_at IS NULL OR f.cancelled_at >= f.booking_date + 1)
-- lấy mẫu theo booking_id (tất định, chạy lại ra cùng tập): pandas không chứa nổi cả cửa sổ 9 tháng; mod() thay
-- toán tử modulo: read_sql qua psycopg 3 coi ký tự phần trăm là placeholder, kể cả trong comment SQL
  AND mod(f.booking_id, 100) < {sample_pct}
"""


@dsl.component(base_image=BASE_IMAGE)
def load_from_feast(features: list, label_sql: str, since: str, until: str, sample_pct: int,
                    data: Output[Dataset]) -> int:
    """Point-in-time join bảng booking (nhãn + cột của chính booking) với feature offline tại booking_date,
    chỉ trong cửa sổ [since, until), lấy sample_pct% booking."""
    import pandas as pd
    from feast import FeatureStore
    store = FeatureStore(repo_path="/feature_repo")
    import os
    labels = pd.read_sql(label_sql.format(since=since, until=until, sample_pct=sample_pct), os.environ["WAREHOUSE_DSN"])
    df = store.get_historical_features(entity_df=labels, features=features).to_df()
    # không dropna: bỏ khách mới làm lệch tập train; điền thiếu y như mcp_server (`or 0`)
    df["has_customer_history"] = (df["bookings_90d"].fillna(0) > 1).astype(int)
    num = [c.split(":")[1] for c in features]
    df[num] = df[num].astype(float)                            # NUMERIC của Postgres có thể về Decimal, XGBoost không nhận
    df = df.fillna(0)
    df.to_parquet(data.path)
    # data versioning: ghi đè Iceberg ml.train_cancel_risk, trả snapshot_id để MLflow ghi (tái lập bằng time travel)
    from data_version import snapshot_training_set
    from pyiceberg.catalog import load_catalog
    catalog = load_catalog("lake", type="sql", uri=os.environ["ICEBERG_CATALOG_URI"], warehouse="s3://lake/",
                           **{"s3.endpoint": os.environ["S3_ENDPOINT"]})
    return snapshot_training_set(catalog, df)


@dsl.component(base_image=BASE_IMAGE)
def split_by_time(data: Input[Dataset], train: Output[Dataset], valid: Output[Dataset]):
    """80% khoảng thời gian đầu làm train, phần sau làm validation."""
    import pandas as pd
    df = pd.read_parquet(data.path).sort_values("event_timestamp")
    cut = df["event_timestamp"].quantile(0.8)
    df[df["event_timestamp"] <= cut].to_parquet(train.path)
    df[df["event_timestamp"] > cut].to_parquet(valid.path)


@dsl.component(base_image=BASE_IMAGE)
def train(train: Input[Dataset], model: Output[Model], inputs: list, label: str,
          n_estimators: int = 300, max_depth: int = 6):
    """XGBoost binary classifier trên đúng cột `inputs`; ghi model ra .joblib."""
    import joblib
    import pandas as pd
    from xgboost import XGBClassifier
    df = pd.read_parquet(train.path)
    X, y = df[inputs], df[label]
    # không dùng scale_pos_weight: nó giữ AUC nhưng đẩy xác suất lên (dự báo ~53% khi thật ~42%), làm sai overbooking
    clf = XGBClassifier(n_estimators=n_estimators, max_depth=max_depth, eval_metric="auc")
    clf.fit(X, y)
    joblib.dump(clf, model.path)


@dsl.component(base_image=BASE_IMAGE)
def train_distributed(train: Input[Dataset], model: Output[Model], inputs: list, label: str,
                      n_estimators: int = 300, max_depth: int = 6, num_nodes: int = 2):
    """Tạo TrainJob (Kubeflow Trainer, runtime xgboost-distributed) đọc tập train trên S3, đợi xong, chép model về."""
    import time
    import uuid

    import fsspec
    from kubernetes import client, config
    config.load_incluster_config()
    name = f"cancel-risk-{uuid.uuid4().hex[:8]}"
    out = f"s3://mlpipeline/trainjobs/{name}/model.joblib"
    body = {"apiVersion": "trainer.kubeflow.org/v1alpha1", "kind": "TrainJob", "metadata": {"name": name},
            "spec": {"runtimeRef": {"name": "xgboost-distributed"},
                     "trainer": {"image": "registry.booking.local/ml/train-base:1.4", "numNodes": num_nodes,
                                 "command": ["python", "/app/ml/train_xgb_dist.py", train.uri, out, ",".join(inputs),
                                             label, str(n_estimators), str(max_depth)],
                                 "resourcesPerNode": {"requests": {"cpu": "2", "memory": "4Gi"}}}}}
    api = client.CustomObjectsApi()
    api.create_namespaced_custom_object("trainer.kubeflow.org", "v1alpha1", "kubeflow", "trainjobs", body)
    while True:
        conds = api.get_namespaced_custom_object("trainer.kubeflow.org", "v1alpha1", "kubeflow", "trainjobs", name)                    .get("status", {}).get("conditions", [])
        done = {c["type"] for c in conds if c["status"] == "True"}
        if "Failed" in done:
            raise RuntimeError(f"TrainJob {name} failed: {conds}")
        if "Complete" in done:
            break
        time.sleep(15)
    with fsspec.open(out, "rb") as src, open(model.path, "wb") as dst:
        dst.write(src.read())


@dsl.component(base_image=BASE_IMAGE)
def evaluate_and_register(model: Input[Model], valid: Input[Dataset], train_data: Input[Dataset],
                          metrics: Output[Metrics], inputs: list, label: str,
                          mlflow_uri: str, model_name: str, min_auc: float, max_calib_gap: float,
                          train_snapshot_id: int):
    """Chấm AUC + calibration + Brier trên validation, log lên MLflow (tag release=latest); gắn alias production khi
    AUC >= min_auc, lệch calibration <= max_calib_gap và Brier không cao hơn bản production trên cùng tập validation."""
    import joblib
    import mlflow
    import pandas as pd
    from mlflow.exceptions import MlflowException
    from mlflow.tracking import MlflowClient
    from sklearn.metrics import brier_score_loss, roc_auc_score
    clf = joblib.load(model.path)
    df = pd.read_parquet(valid.path)
    p = clf.predict_proba(df[inputs])[:, 1]
    auc = roc_auc_score(df[label], p)
    calib_gap = abs(p.mean() - df[label].mean())               # tỉ lệ huỷ dự báo so với thật
    brier = brier_score_loss(df[label], p)
    for k, v in {"val_auc": auc, "val_calib_gap": calib_gap, "val_brier": brier}.items():
        metrics.log_metric(k, v)

    mlflow.set_tracking_uri(mlflow_uri)
    try:                                                       # bản production hiện tại, chấm lại trên cùng validation
        prod = mlflow.sklearn.load_model(f"models:/{model_name}@production")
        prod_p = prod.predict_proba(df[inputs])[:, 1]
        prod_auc, prod_brier = roc_auc_score(df[label], prod_p), brier_score_loss(df[label], prod_p)
    except MlflowException:                                    # lần đầu: chưa có alias production
        prod_auc, prod_brier = 0.0, 1.0
    with mlflow.start_run():
        mlflow.log_params({**clf.get_params(), "train_snapshot_id": train_snapshot_id})
        mlflow.log_metrics({"val_auc": auc, "val_calib_gap": calib_gap, "val_brier": brier,
                            "prod_auc_same_valid": prod_auc, "prod_brier_same_valid": prod_brier})
        mlflow.log_dict(dict(zip(inputs, clf.feature_importances_.tolist())), "feature_importance.json")
        train_df = pd.read_parquet(train_data.path)
        mlflow.log_input(mlflow.data.from_pandas(train_df, name="train"), context="training")
        # reference cho drift-api (KSDrift) và drift_monitor (PSI/KS): CI chép artifact này vào image cùng version model
        import numpy as np
        np.save("reference_lead_days.npy", train_df["lead_days"].to_numpy())
        mlflow.log_artifact("reference_lead_days.npy")
        info = mlflow.sklearn.log_model(clf, "model", registered_model_name=model_name)
    client = MlflowClient()
    version = info.registered_model_version
    client.set_model_version_tag(model_name, version, "release", "latest")   # MLflow cấm alias tên "latest"
    if auc >= min_auc and calib_gap <= max_calib_gap and brier <= prod_brier:
        client.set_registered_model_alias(model_name, "production", version)


@dsl.pipeline(name="cancel-risk-training")
def training_pipeline(since: str = "2025-01-01", until: str = "2025-06-01", sample_pct: int = 5,
                      n_estimators: int = 300, max_depth: int = 6, distributed: bool = True):
    """Nối 4 step. Lần đầu train trên [since, until) trước mốc drift (booking tới until - 90 ngày); retrain do
    drift_monitor truyền since = ngày phát hiện để train và validation cùng chế độ dữ liệu sau drift."""
    loaded = load_from_feast(features=FEATURES, label_sql=LABEL_SQL, since=since, until=until, sample_pct=sample_pct)
    # DSN warehouse (user ml_reader), catalog Iceberg, endpoint S3, Feast PG lấy từ Secret ml-warehouse, không viết trong code
    kubernetes.use_secret_as_env(loaded, secret_name="ml-warehouse", secret_key_to_env={
        "warehouse_dsn": "WAREHOUSE_DSN",
        "iceberg_catalog_uri": "ICEBERG_CATALOG_URI",
        "s3_endpoint": "S3_ENDPOINT",
        "aws_access_key_id": "AWS_ACCESS_KEY_ID",
        "aws_secret_access_key": "AWS_SECRET_ACCESS_KEY",
        "feast_pg_password": "FEAST_PG_PASSWORD",
    })
    loaded.set_env_variable(name="FEAST_PG_HOST", value="postgres.data.svc.cluster.local")
    loaded.set_env_variable(name="FEAST_PG_USER", value="postgres")
    split = split_by_time(data=loaded.outputs["data"])
    with dsl.If(distributed == True):  # noqa: E712 (biểu thức điều kiện của KFP, không phải so sánh Python)
        dist = train_distributed(train=split.outputs["train"], inputs=MODEL_INPUTS, label=LABEL,
                                 n_estimators=n_estimators, max_depth=max_depth)
    with dsl.Else():
        single = train(train=split.outputs["train"], inputs=MODEL_INPUTS, label=LABEL,
                       n_estimators=n_estimators, max_depth=max_depth)
    evaluate_and_register(model=dsl.OneOf(dist.outputs["model"], single.outputs["model"]), valid=split.outputs["valid"],
                          train_data=split.outputs["train"], inputs=MODEL_INPUTS, label=LABEL,
                          mlflow_uri=MLFLOW_URI, model_name=MODEL_NAME, min_auc=MIN_AUC, max_calib_gap=MAX_CALIB_GAP,
                          train_snapshot_id=loaded.outputs["Output"])


if __name__ == "__main__":
    compiler.Compiler().compile(training_pipeline, "training_pipeline.yaml")
