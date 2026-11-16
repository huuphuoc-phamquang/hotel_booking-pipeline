"""Data versioning Iceberg (ml/data_version.py) trên catalog SQL sqlite + warehouse thư mục tạm.

  - Incremental : lần 2 chỉ đổi nhãn 1 dòng + thêm 1 dòng -> snapshot mới chỉ ghi phần thay đổi (không chép lại cả bảng)
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


def test_upsert_versions_and_time_travel(catalog):
    v1 = snapshot_training_set(catalog, frame(1000))
    tbl = catalog.load_table("ml.train_cancel_risk")
    files_v1 = len(tbl.inspect.files())
    df2 = pd.concat([frame(1000), frame(1)], ignore_index=True).drop_duplicates("booking_id")
    df2.loc[df2["booking_id"] == 5, "is_cancelled"] = 1                    # 1 nhãn đổi
    df2 = pd.concat([df2, pd.DataFrame({"booking_id": [1001], "lead_days": [3.0], "is_cancelled": [0]})])
    v2 = snapshot_training_set(catalog, df2)
    assert v2 != v1
    now = load_training_set(catalog, v2).set_index("booking_id")
    assert len(now) == 1001 and now.loc[5, "is_cancelled"] == 1
    old = load_training_set(catalog, v1).set_index("booking_id")
    assert len(old) == 1000 and old.loc[5, "is_cancelled"] == 0
    assert files_v1 >= 1 and len(tbl.refresh().inspect.snapshots()) >= 2


def test_same_data_adds_no_rows(catalog):
    v1 = snapshot_training_set(catalog, frame(50))
    v2 = snapshot_training_set(catalog, frame(50))                          # giống hệt: upsert không tạo snapshot mới
    assert v2 == v1 and len(load_training_set(catalog, v2)) == 50
