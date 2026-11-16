"""Bộ Great Expectations của DP1 trên đúng dữ liệu landing generator sinh: dữ liệu sạch qua, lỗi cài vào thì fail."""
import pandas as pd
import pytest

pytest.importorskip("great_expectations")
from generator.offline_gen import gen_dims, landing_partitions, load_config  # noqa: E402
from governance.bronze_checks import EXPECTATIONS, columns, validate_frame  # noqa: E402


@pytest.fixture(scope="module")
def landing():
    cfg = load_config("generator/config.yaml")
    cfg["dims"] = {"hotels": 300, "customers": 5000}
    cfg["shards_per_day"] = 2
    parts = {}
    for k, df, _ in landing_partitions(cfg, gen_dims(cfg), 200, 201):
        parts.setdefault(k.split("/")[0], []).append(df)
    return {t: pd.concat(v, ignore_index=True) for t, v in parts.items()}


@pytest.mark.parametrize("table", list(EXPECTATIONS))
def test_generator_landing_passes(landing, table):
    r = validate_frame(table, landing[table][columns(table)])
    assert r.success, [x.expectation_config.type for x in r.results if not x.success]


def test_injected_errors_fail(landing):
    q = landing["quotes"][columns("quotes")].copy()
    q.loc[0, "price"] = -1
    q.loc[1, "quote_id"] = q.loc[2, "quote_id"]
    r = validate_frame("quotes", q)
    failed = {x.expectation_config.type for x in r.results if not x.success}
    assert not r.success and failed == {"expect_column_values_to_be_between", "expect_column_values_to_be_unique"}


def test_empty_partition_fails():
    assert not validate_frame("payments", pd.DataFrame({c: [] for c in columns("payments")})).success
