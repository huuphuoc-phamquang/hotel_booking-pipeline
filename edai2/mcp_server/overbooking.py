"""Số phòng bán vượt K cho 1 hotel × stay_date từ xác suất huỷ của các booking đang giữ phòng (design mục 1.2).

N = số booking huỷ ~ Poisson-binomial(p_1..p_n) (giả định huỷ độc lập). Bán vượt K: N < K thì phải chuyển khách
(c_walk / khách), N > K thì phòng trống (c_spoil / phòng). K tối ưu = K lớn nhất với P(N < K) <= c_spoil / (c_spoil + c_walk).
"""
import numpy as np


def cancel_distribution(probs: list[float]) -> np.ndarray:
    """P(N = n), n = 0..len(probs), bằng quy hoạch động O(n²) (chính xác, không xấp xỉ chuẩn)."""
    dist = np.zeros(len(probs) + 1)
    dist[0] = 1.0
    for i, p in enumerate(probs, start=1):
        dist[1:i + 1] = dist[1:i + 1] * (1 - p) + dist[:i] * p
        dist[0] *= 1 - p
    return dist


def limit(probs: list[float], c_spoil: float, c_walk: float) -> int:
    """K lớn nhất với P(N < K) <= c_spoil / (c_spoil + c_walk); không có booking thì K = 0."""
    if c_spoil <= 0 or c_walk <= 0:
        raise ValueError("c_spoil và c_walk phải dương")
    if any(not 0.0 <= p <= 1.0 for p in probs):
        raise ValueError("xác suất phải nằm trong [0, 1]")
    below = np.concatenate([[0.0], np.cumsum(cancel_distribution(probs))])   # below[k] = P(N < k)
    ratio = c_spoil / (c_spoil + c_walk)
    return int(np.flatnonzero(below[:len(probs) + 1] <= ratio + 1e-12).max())
