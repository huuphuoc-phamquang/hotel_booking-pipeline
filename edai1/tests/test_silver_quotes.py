"""silver_quotes: 4 chế độ (baseline / aqe / aqe_tuned / salt) cho đúng cùng một kết quả, không mất quote nào khi join inventory.
Cần pyspark + Java; chạy: pytest tests/test_silver_quotes.py"""
import sys

import pandas as pd
import pytest

pyspark = pytest.importorskip("pyspark")
sys.path.insert(0, "spark_jobs")

from generator.offline_gen import gen_dims, gen_inventory, gen_quotes, load_config  # noqa: E402
from silver_quotes import MODES, enrich_quotes, spark_for  # noqa: E402


@pytest.fixture(scope="module")
def bronze(tmp_path_factory):
    cfg = load_config("generator/config.yaml")
    cfg["dims"] = {"hotels": 300, "customers": 5000}
    cfg["shards_per_day"] = 2
    dims = gen_dims(cfg)
    root = tmp_path_factory.mktemp("bronze")
    q = pd.concat([gen_quotes(cfg, dims, d, s) for d in (40, 41) for s in range(2)], ignore_index=True)
    stays = range(q["stay_date"].min().dayofyear - 1, q["stay_date"].max().dayofyear)   # start_date = 01/01
    inv = pd.concat([gen_inventory(cfg, dims, s) for s in stays], ignore_index=True)
    for name, df in (("quotes", q), ("inventory", inv)):              # cùng cách ghi với landing (upload_parquet)
        df.to_parquet(root / f"{name}.parquet", coerce_timestamps="us", allow_truncated_timestamps=True)
    return root, q


def test_modes_agree_and_keep_every_quote(bronze):
    root, q = bronze
    results = {}
    for mode in MODES:
        spark = spark_for(mode)
        quotes, inv = spark.read.parquet(str(root / "quotes.parquet")), spark.read.parquet(str(root / "inventory.parquet"))
        out = enrich_quotes(quotes, inv, mode).select("quote_id", "rooms").toPandas()
        results[mode] = out.sort_values("quote_id").reset_index(drop=True)
        spark.stop()
    assert len(results["baseline"]) == len(q) and results["baseline"]["quote_id"].is_unique
    assert (results["baseline"]["rooms"] >= 1).all()
    for mode in MODES[1:]:
        pd.testing.assert_frame_equal(results["baseline"], results[mode])
