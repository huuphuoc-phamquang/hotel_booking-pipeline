"""Thống kê drift batch cho DAG drift_monitor (tách khỏi file DAG để test không cần Airflow)."""
from datetime import date, timedelta

import numpy as np
from scipy.stats import ks_2samp

PSI_BINS = 10
PSI_RETRAIN = 0.2        # quy ước thường dùng: < 0,1 ổn định, 0,1–0,2 theo dõi, > 0,2 lệch đáng kể
CALIB_RETRAIN = 0.03     # = MAX_CALIB_GAP của cổng promote (ml/training_pipeline.py)
POST_DRIFT_DAYS = 30     # số ngày booking sau mốc phát hiện cần có nhãn trước khi retrain
LABEL_MATURITY_DAYS = 90 # = LABEL_SQL của training_pipeline: chỉ lấy booking_date < until - 90 (nhãn đã chín)
CLEAR_DAYS = 3           # hết drift chừng này ngày liên tiếp thì xoá mốc phát hiện (1 ngày vượt ngưỡng lẻ không retrain)


def psi(reference: np.ndarray, current: np.ndarray, bins: int = PSI_BINS) -> float:
    """Population Stability Index trên các bin chia theo phân vị của reference; bin rỗng được làm trơn 1e-4."""
    edges = np.unique(np.quantile(reference, np.linspace(0, 1, bins + 1)))
    edges[0], edges[-1] = -np.inf, np.inf
    ref = np.histogram(reference, edges)[0] / len(reference)
    cur = np.histogram(current, edges)[0] / len(current)
    ref, cur = np.clip(ref, 1e-4, None), np.clip(cur, 1e-4, None)
    return float(np.sum((cur - ref) * np.log(cur / ref)))


def drift_report(reference: np.ndarray, current: np.ndarray, predicted: float | None, actual: float | None) -> dict:
    """PSI + KS trên lead_days, lệch calibration (tỉ lệ huỷ dự báo - thực tế) và quyết định retrain."""
    gap = None if predicted is None or actual is None else abs(predicted - actual)
    report = {"psi": psi(reference, current), "ks_p_value": float(ks_2samp(reference, current).pvalue), "calib_gap": gap}
    report["retrain"] = report["psi"] > PSI_RETRAIN or (gap is not None and gap > CALIB_RETRAIN)
    return report


def retrain_window(state: dict | None, ds: date, drifted: bool, version: str) -> tuple[dict | None, tuple | None]:
    """Trả (trạng thái cần lưu, cửa sổ retrain (since, until) hoặc None).
    state = {"detected", "last_drift": ngày ISO, "version": version production lúc phát hiện} (lưu dạng JSON).
    Ngày đầu drift: chỉ ghi mốc. Retrain khi đã đủ POST_DRIFT_DAYS ngày booking sau mốc có nhãn chín, cửa sổ bắt đầu
    từ mốc nên train và validation chỉ có dữ liệu sau drift; retrain sớm hơn thì LABEL_SQL toàn booking trước drift.
    Xoá mốc khi hết drift CLEAR_DAYS ngày liên tiếp, hoặc khi production đã là version khác (mốc đo trên model cũ)."""
    if state and state["version"] != version:
        state = None
    if state is None:
        return ({"detected": str(ds), "last_drift": str(ds), "version": version} if drifted else None), None
    if drifted:
        state = {**state, "last_drift": str(ds)}
    elif ds - date.fromisoformat(state["last_drift"]) >= timedelta(days=CLEAR_DAYS):
        return None, None
    detected = date.fromisoformat(state["detected"])
    if ds >= detected + timedelta(days=POST_DRIFT_DAYS + LABEL_MATURITY_DAYS):
        return None, (detected, ds)
    return state, None
