"""Hàm cầu thật (ground truth) mà generator dùng để quyết định lượt xem giá nào thành booking.

Một ô = hotel × stay_date; giá tính theo P/P̄:
  xác suất đặt   p(P) = min(1, conversion · u^kappa · (P/P̄)^(−β))
β theo phân khúc (số sao) và nhóm lead time; u là cầu ẩn của ô (model không thấy).
Không có model nào ước lượng cầu: đồ án chỉ có model cancel-risk; hàm này chỉ để booking sinh ra từ quotes.
"""
import numpy as np
import pandas as pd

SEGMENT_OF_STARS = np.array([0, 0, 0, 1, 2, 2])   # index = số sao: 1-2 budget, 3 mid, 4-5 luxury


def season_of(cfg: dict, days: pd.DatetimeIndex) -> np.ndarray:
    """Hệ số mùa theo stay_date (peak_periods trong config), bản vector hoá."""
    s = np.ones(len(days))
    for p in cfg["skew"]["peak_periods"]:
        s[(days >= pd.Timestamp(p["from"])) & (days <= pd.Timestamp(p["to"]))] = p["factor"]
    return s


def book_prob(cfg: dict, rel_price, u, beta):
    """Xác suất 1 lượt xem giá thành booking (ground truth cho cột booked của quotes)."""
    d = cfg["demand"]
    return np.minimum(1.0, d["conversion"] * u ** d["kappa"] * rel_price ** -beta)
