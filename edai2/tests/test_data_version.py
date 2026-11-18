"""Data versioning Iceberg (ml/data_version.py) trên catalog SQL sqlite + warehouse thư mục tạm.

  - Mỗi lần train 1 snapshot đúng bằng tập đã train: v2 train trên cửa sổ khác thì snapshot v2 không chứa dòng của v1
  - Tái lập     : scan(snapshot_id) của lần 1 trả đúng tập lần 1 dù bảng đã đổi
"""
import pandas as pd
import pytest

pyiceberg = pytest.importorskip("pyiceberg")
from pyiceberg.catalog.sql import SqlCatalog  # noqa: E402

from data_version import load_training_set, snapshot_training_set  # noqa: E402


@pytest.fixture
def catalog(tmp_path):
    return SqlCatalog("lake", uri=f"sqlite:///{tmp_path}/catalog.db", warehouse=f"file://{tmp_path}")


def frame(n, cancelled=0):
    return pd.DataFrame({"booking_id": range(1, n + 1), "lead_days": [10.0] * n, "is_cancelled": [cancelled] * n})


def test_each_snapshot_is_exactly_the_training_set(catalog):
    v1 = snapshot_training_set(catalog, frame(1000))                      # cửa sổ trước drift
    v2_df = pd.DataFrame({"booking_id": range(5000, 5300), "lead_days": [30.0] * 300, "is_cancelled": [1] * 300})
    v2 = snapshot_training_set(catalog, v2_df)                            # retrain trên cửa sổ sau drift, không giao v1
    assert v2 != v1
    assert set(load_training_set(catalog, v2)["booking_id"]) == set(v2_df["booking_id"])
    old = load_training_set(catalog, v1).set_index("booking_id")
    assert len(old) == 1000 and (old["is_cancelled"] == 0).all()


def test_relabel_creates_new_version(catalog):
    v1 = snapshot_training_set(catalog, frame(50))
    df = frame(50)
    df.loc[df["booking_id"] == 5, "is_cancelled"] = 1                     # nhãn chín thêm sau lần train trước
    v2 = snapshot_training_set(catalog, df)
    assert load_training_set(catalog, v2).set_index("booking_id").loc[5, "is_cancelled"] == 1
    assert load_training_set(catalog, v1).set_index("booking_id").loc[5, "is_cancelled"] == 0
