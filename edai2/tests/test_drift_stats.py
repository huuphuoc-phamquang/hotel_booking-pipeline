"""Test PSI/KS và quyết định retrain của drift_monitor (dags/drift_stats.py)."""
from datetime import date, timedelta

import numpy as np
import pytest

from drift_stats import (CALIB_RETRAIN, CLEAR_DAYS, LABEL_MATURITY_DAYS, POST_DRIFT_DAYS, PSI_RETRAIN, drift_report,
                         psi, retrain_window)

RNG = np.random.default_rng(1)
REF = RNG.gamma(2, 10, 20000)


def test_psi_zero_for_same_sample():
    assert psi(REF, REF) == pytest.approx(0.0, abs=1e-9)


def test_covariate_drift_of_generator_crosses_threshold():
    """lead time × 1,5 (covariate_drift của generator) phải vượt ngưỡng retrain; mẫu mới cùng phân phối thì không."""
    assert psi(REF, RNG.gamma(2, 10, 5000)) < 0.1
    assert psi(REF, RNG.gamma(2, 10, 5000) * 1.5) > PSI_RETRAIN


def test_psi_handles_constant_reference():
    assert np.isfinite(psi(np.zeros(100), RNG.gamma(2, 10, 100)))


@pytest.mark.parametrize("predicted, actual, retrain", [
    (0.33, 0.33, False),
    (0.33, 0.33 + CALIB_RETRAIN, False),          # biên: đúng bằng ngưỡng chưa retrain
    (0.33, 0.48, True),                           # tỉ lệ huỷ thật tăng sau drift, model vẫn dự báo như cũ
    (None, None, False),                          # chưa có booking nào qua checkin
])
def test_calibration_gate(predicted, actual, retrain):
    r = drift_report(REF, RNG.gamma(2, 10, 5000), predicted, actual)
    assert r["retrain"] is retrain and 0 <= r["ks_p_value"] <= 1


def run_days(start: date, drifted: list[bool], version: str = "1", state=None):
    """Chạy retrain_window qua nhiều ngày liên tiếp như DAG; trả (trạng thái cuối, các cửa sổ retrain đã gọi)."""
    windows = []
    for i, flag in enumerate(drifted):
        state, w = retrain_window(state, start + timedelta(days=i), flag, version)
        windows += [w] if w else []
    return state, windows


def test_retrain_waits_for_matured_post_drift_labels():
    """Phát hiện ngày D, drift kéo dài: retrain đúng 1 lần ở D + 30 + 90, since = D (cửa sổ chỉ có booking sau drift)."""
    d = date(2025, 6, 7)
    wait = POST_DRIFT_DAYS + LABEL_MATURITY_DAYS
    assert run_days(d, [False]) == (None, [])
    state, windows = run_days(d, [True] * wait)
    assert windows == [] and state["detected"] == str(d)                      # vẫn drift nhưng nhãn chưa chín
    assert run_days(d, [True] * (wait + 1))[1] == [(d, d + timedelta(days=wait))]
    # LABEL_SQL lấy booking_date trong [since, until - 90): đúng 30 ngày sau mốc phát hiện
    assert wait - LABEL_MATURITY_DAYS == POST_DRIFT_DAYS


def test_detection_cleared_when_drift_ends():
    """1 ngày PSI vượt ngưỡng rồi hết: xoá mốc sau CLEAR_DAYS ngày, không retrain 120 ngày sau."""
    d = date(2025, 6, 7)
    state, windows = run_days(d, [True] + [False] * CLEAR_DAYS + [False] * 200)
    assert state is None and windows == []
    # tắt chưa đủ CLEAR_DAYS ngày liên tiếp thì giữ mốc
    assert run_days(d, [True] + [False] * (CLEAR_DAYS - 1) + [True])[0]["detected"] == str(d)


def test_detection_reset_after_new_production_version():
    """Mốc ghi khi production là v1; v2 lên production thì mốc cũ không còn nghĩa, bắt đầu lại từ đầu."""
    d = date(2025, 6, 7)
    state, _ = run_days(d, [True] * 10, version="1")
    state, w = retrain_window(state, d + timedelta(days=10), False, "2")
    assert (state, w) == (None, None)
