"""DAG drift_monitor: mỗi ngày so lead_days 7 ngày gần nhất với reference của model production (PSI + KS) và tỉ lệ huỷ
dự báo với thực tế, đẩy PushGateway -> Grafana; lệch quá ngưỡng thì gọi Kubeflow chạy lại training_pipeline.

Rubric final › Drift detection (batch) + ML telemetry; bổ sung cho drift-api (realtime, KServe logger).
  - reference : artifact reference_lead_days.npy của run đã đăng ký version alias production (MLflow)
  - current   : gold.fact_bookings, booking_date trong 7 ngày tới hết ngày ds
  - calibration: booking nhận phòng trong 7 ngày qua (đã có kết cục), chỉ booking do đúng version production chấm
                 (gold.booking_risk.model_version): sau khi promote v2, điểm cũ của v1 không bị tính là của v2
Connection warehouse; Variable mlflow_uri, pushgateway_url, kfp_host, kfp_pipeline_package đặt trong Airflow.
Retrain không chạy ngay ngày phát hiện: LABEL_SQL chỉ lấy booking đã chín nhãn (booking_date < until - 90), nên retrain
ngay sẽ toàn dữ liệu trước drift. Variable cancel_risk_drift_detected (JSON) giữ mốc phát hiện; đủ 30 ngày booking sau
mốc có nhãn chín (drift_stats.retrain_window) thì retrain trên [mốc, ds). Hết drift 3 ngày liên tiếp hoặc production
đổi version thì xoá mốc.
"""
from datetime import date, datetime

from airflow.decorators import dag, task
from airflow.models import Variable

MODEL_NAME = "cancel-risk"
DETECTED_VAR = "cancel_risk_drift_detected"
CURRENT_SQL = """SELECT lead_days FROM gold.fact_bookings
WHERE booking_date > %(ds)s::date - 7 AND booking_date <= %(ds)s::date"""
CALIB_SQL = """SELECT avg(r.probability), avg(l.is_cancelled)
FROM gold.booking_risk r
JOIN gold.fact_bookings f USING (booking_id)
JOIN gold.labels_cancel l USING (booking_id)
WHERE r.model_version = %(version)s
  AND f.checkin_date > %(ds)s::date - 7 AND f.checkin_date <= %(ds)s::date"""


@dag(dag_id="drift_monitor", start_date=datetime(2025, 1, 1), schedule="@daily", catchup=False, max_active_runs=1,
     tags=["ml", "drift"])
def drift_monitor():

    @task
    def measure(ds=None) -> dict:
        import mlflow
        import numpy as np
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from drift_stats import drift_report                  # scipy: chỉ import lúc chạy task, không lúc parse DAG
        from mlflow.tracking import MlflowClient
        mlflow.set_tracking_uri(Variable.get("mlflow_uri"))
        mv = MlflowClient().get_model_version_by_alias(MODEL_NAME, "production")
        reference = np.load(mlflow.artifacts.download_artifacts(run_id=mv.run_id, artifact_path="reference_lead_days.npy"))
        pg = PostgresHook(postgres_conn_id="warehouse")
        current = np.array([r[0] for r in pg.get_records(CURRENT_SQL, parameters={"ds": ds})], dtype=float)
        predicted, actual = pg.get_first(CALIB_SQL, parameters={"ds": ds, "version": str(mv.version)})
        report = drift_report(reference, current, None if predicted is None else float(predicted),
                              None if actual is None else float(actual))
        return {**report, "model_version": mv.version}

    @task
    def push(report: dict) -> None:
        from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
        reg = CollectorRegistry()
        for name in ("psi", "ks_p_value", "calib_gap"):
            if report[name] is not None:
                Gauge(f"cancel_risk_{name}", f"drift_monitor {name}", ["model_version"], registry=reg) \
                    .labels(report["model_version"]).set(report[name])
        push_to_gateway(Variable.get("pushgateway_url"), job="drift_monitor", registry=reg)

    @task.short_circuit
    def plan_retrain(report: dict, ds=None) -> list[str] | None:
        """Ghi/đọc mốc phát hiện; trả [since, until] khi đã đủ nhãn chín sau mốc, None thì bỏ qua retrain."""
        from drift_stats import retrain_window
        state, window = retrain_window(Variable.get(DETECTED_VAR, default_var=None, deserialize_json=True),
                                       date.fromisoformat(ds), report["retrain"], str(report["model_version"]))
        Variable.set(DETECTED_VAR, state, serialize_json=True)
        return [str(window[0]), str(window[1])] if window else None

    @task
    def retrain(window: list[str], ds=None) -> str:
        import kfp
        run = kfp.Client(host=Variable.get("kfp_host")).create_run_from_pipeline_package(
            Variable.get("kfp_pipeline_package"), run_name=f"retrain-{ds}",
            arguments={"since": window[0], "until": window[1]})
        return run.run_id

    report = measure()
    push(report)
    retrain(plan_retrain(report))


drift_monitor()
