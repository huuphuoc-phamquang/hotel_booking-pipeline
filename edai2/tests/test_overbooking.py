"""Test K bán vượt (mcp_server/overbooking.py) và 2 tool propose_overbooking / apply_overbooking của server.py.

  - EP + BVA       : p = 0 / 1, không có booking, chi phí <= 0, xác suất ngoài [0, 1]
  - Oracle         : phân phối Poisson-binomial so với liệt kê đủ 2^n trường hợp; K so với định nghĩa trực tiếp
  - Property-based : K tăng khi c_walk giảm (chuyển khách rẻ hơn thì dám bán vượt nhiều hơn)
"""
import itertools
from datetime import date

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

import server
from overbooking import cancel_distribution, limit


def brute_distribution(probs):
    dist = np.zeros(len(probs) + 1)
    for outcome in itertools.product([0, 1], repeat=len(probs)):
        dist[sum(outcome)] += np.prod([p if o else 1 - p for p, o in zip(probs, outcome)])
    return dist


@pytest.mark.parametrize("probs", [[], [0.3], [0.1, 0.5, 0.9], [0.2] * 6, [0.0, 1.0, 0.4, 0.7]])
def test_distribution_matches_enumeration(probs):
    assert np.allclose(cancel_distribution(probs), brute_distribution(probs))


@given(st.lists(st.floats(0, 1), max_size=8), st.floats(0.1, 10), st.floats(0.1, 10))
@settings(max_examples=100, deadline=None)
def test_limit_matches_definition(probs, c_spoil, c_walk):
    below = np.concatenate([[0.0], np.cumsum(brute_distribution(probs))])
    expected = max(k for k in range(len(probs) + 1) if below[k] <= c_spoil / (c_spoil + c_walk) + 1e-12)
    assert limit(probs, c_spoil, c_walk) == expected


# BVA: huỷ chắc chắn -> bán vượt đủ n; không ai huỷ -> 0; không có booking -> 0
@pytest.mark.parametrize("probs, k", [([], 0), ([1.0] * 5, 5), ([0.0] * 5, 0)])
def test_limit_bounds(probs, k):
    assert limit(probs, 1.0, 3.0) == k


@pytest.mark.parametrize("probs, c_spoil, c_walk", [([0.5], 0, 1), ([0.5], 1, 0), ([1.01], 1, 1), ([-0.01], 1, 1)])
def test_limit_rejects_bad_input(probs, c_spoil, c_walk):
    with pytest.raises(ValueError):
        limit(probs, c_spoil, c_walk)


@given(st.lists(st.floats(0, 1), min_size=1, max_size=30))
@settings(max_examples=50, deadline=None)
def test_cheaper_walk_never_lowers_k(probs):
    assert limit(probs, 1.0, 1.0) >= limit(probs, 1.0, 5.0)


def fake_db(monkeypatch, risk, rooms):
    calls = []

    async def _query(sql, params, fetch=True):
        calls.append(params)
        return risk if sql == server.RISK_SQL else rooms
    monkeypatch.setattr(server, "_query", _query)
    return calls


async def test_propose_compares_with_rooms(monkeypatch):
    calls = fake_db(monkeypatch, [(0.9, date(2025, 10, 1))] * 3 + [(0.9, date(2025, 10, 2))], [(5,)])
    p = await server.propose_overbooking(7, date(2025, 10, 10))
    k = limit([0.9] * 4, server.C_SPOIL, server.C_WALK)
    assert (p.bookings, p.expected_cancellations, p.scored_date, p.k) == (4, 3.6, date(2025, 10, 2), k)
    assert (p.rooms, p.can_sell) == (5, 5 + k - 4) and calls == [(7, date(2025, 10, 10))] * 2


async def test_propose_full_hotel_cannot_sell(monkeypatch):
    """Đã giữ nhiều hơn rooms + K (xác suất huỷ thấp, K = 0): không nhận thêm, không ra số âm."""
    fake_db(monkeypatch, [(0.01, date(2025, 10, 1))] * 6, [(5,)])
    p = await server.propose_overbooking(7, date(2025, 10, 10))
    assert (p.k, p.can_sell) == (0, 0)


async def test_propose_without_bookings(monkeypatch):
    fake_db(monkeypatch, [], [])
    p = await server.propose_overbooking(7, date(2025, 10, 10))
    assert (p.bookings, p.k, p.scored_date, p.rooms, p.can_sell) == (0, 0, None, None, None)


async def test_apply_writes_and_rejects_negative(monkeypatch):
    calls = []

    async def _query(sql, params, fetch=True):
        calls.append((sql, params, fetch))
        return []
    monkeypatch.setattr(server, "_query", _query)
    assert "K=2" in await server.apply_overbooking(7, date(2025, 10, 10), 2)
    assert calls == [(server.APPLY_SQL, (7, date(2025, 10, 10), 2), False)]
    with pytest.raises(ValueError):
        await server.apply_overbooking(7, date(2025, 10, 10), -1)


async def test_propose_counts_failure(monkeypatch):
    async def _boom(sql, params, fetch=True):
        raise ConnectionError("db down")
    monkeypatch.setattr(server, "_query", _boom)
    before = server.TOOL_FAILURES.labels("propose_overbooking")._value.get()
    with pytest.raises(ConnectionError):
        await server.propose_overbooking(7, date(2025, 10, 10))
    assert server.TOOL_FAILURES.labels("propose_overbooking")._value.get() == before + 1
