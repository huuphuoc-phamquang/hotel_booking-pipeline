"""Recipe DataHub (governance/datahub/*.yml) parse được bằng class config của từng source, tên dataset sinh ra khớp
URN trong governance/emit_datahub.py (lệch tên thì lineage gắn vào dataset rỗng), và mọi bảng Gold có mô tả.
Cần: pip install 'acryl-datahub[postgres,iceberg,s3]==1.7.0.19'"""
import re
from pathlib import Path

import pytest

pytest.importorskip("datahub")
from datahub.configuration.config_loader import load_config_file  # noqa: E402

from governance import emit_datahub as ed  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ENV = {"POSTGRES_PASSWORD": "x", "MINIO_ACCESS_KEY": "k", "MINIO_SECRET_KEY": "s", "DATAHUB_GMS": "http://gms:8080"}


@pytest.fixture
def recipes(monkeypatch):
    for k, v in ENV.items():
        monkeypatch.setenv(k, v)
    return {f.stem: load_config_file(f)["source"]["config"] for f in (ROOT / "governance/datahub").glob("*.yml")}


def test_recipes_parse(recipes):
    from datahub.ingestion.source.iceberg.iceberg_common import IcebergSourceConfig
    from datahub.ingestion.source.sql.postgres import PostgresConfig
    PostgresConfig.model_validate(recipes["postgres_gold"])
    IcebergSourceConfig.model_validate(recipes["iceberg_silver"])


@pytest.mark.parametrize("path, name", [("s3://lake/bronze/raw_bookings/dt=2025-03-01/part-0.parquet", "raw_bookings"),
                                        ("s3://lake/bronze/raw_hotels/part-0.parquet", "raw_hotels")])
def test_s3_dataset_name_matches_lineage(recipes, path, name):
    from datahub.ingestion.source.s3.config import DataLakeSourceConfig
    specs = [ps for ps in DataLakeSourceConfig.model_validate(recipes["s3_bronze"]).path_specs if ps.allowed(path)]
    assert len(specs) == 1
    assert specs[0].extract_table_name_and_path(path)[0] == f"lake/bronze/{name}"
    assert f"s3:lake/bronze/{name}" in ed.TABLES["bronze"]


def test_every_table_documented():
    gold = re.findall(r"CREATE (?:TABLE|VIEW) gold\.(\w+)", (ROOT / "schema/gold_schema.sql").read_text(encoding="utf-8"))
    documented = {ref for tables in ed.TABLES.values() for ref in tables}
    assert {f"postgres:warehouse.gold.{t}" for t in gold} <= documented
    lineage = {ref for ins, outs in ed.PIPELINES.values() for ref in ins + outs if not ref.startswith("s3:landing/")}
    assert lineage <= documented


def test_emit_table_docs():
    out = []
    ed.emit_table_docs(type("E", (), {"emit": lambda self, m: out.append(m)})())
    assert len(out) == 2 * sum(len(t) for t in ed.TABLES.values())
    assert out[0].entityUrn == "urn:li:dataset:(urn:li:dataPlatform:s3,lake/bronze/raw_quotes,PROD)"


def test_emit_validation_declares_assertion_then_result():
    """Tab Validation cần AssertionInfo (assertion gắn với dataset) trước AssertionRunEvent (kết quả lần chạy)."""
    out = []
    ed.emit_validation(type("E", (), {"emit": lambda self, m: out.append(m)})(),
                       "postgres:warehouse.gold.fact_bookings", "amount_positive", False)
    info, run = (m.aspect for m in out)
    assert out[0].entityUrn == out[1].entityUrn == run.assertionUrn
    assert info.datasetAssertion.dataset == run.asserteeUrn == ed.ds_urn("postgres:warehouse.gold.fact_bookings")
    assert run.result.type == "FAILURE"
