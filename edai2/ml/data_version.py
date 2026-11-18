"""Data versioning cho tập train của cancel-risk: Iceberg ml.train_cancel_risk, mỗi lần train là 1 snapshot.

Rubric edai-2 › MLflow lưu data + metadata của mỗi run: mỗi lần train ghi đè (overwrite) bảng bằng đúng tập vừa train,
MLflow log snapshot_id; tái lập đúng tập đã train bằng scan(snapshot_id=...) (= VERSION AS OF của Spark SQL).
Không dùng upsert: v2 train trên cửa sổ sau drift sẽ giữ lại các dòng của v1 trong snapshot, snapshot không còn bằng
tập v2 đã train. Snapshot cũ vẫn đọc được tới khi expire_snapshots. Catalog `lake` = Iceberg SQL catalog trên PostgreSQL.
"""
import pandas as pd
import pyarrow as pa
from pyiceberg.catalog import Catalog
from pyiceberg.exceptions import NoSuchTableError

TABLE = "ml.train_cancel_risk"


def snapshot_training_set(catalog: Catalog, df: pd.DataFrame, table: str = TABLE) -> int:
    """Ghi đè bảng bằng df (tạo nếu chưa có) và trả snapshot_id hiện hành sau khi ghi."""
    data = pa.Table.from_pandas(df, preserve_index=False)
    try:
        tbl = catalog.load_table(table)
    except NoSuchTableError:
        catalog.create_namespace_if_not_exists(table.split(".")[0])
        tbl = catalog.create_table(table, schema=data.schema)
    tbl.overwrite(data.cast(tbl.schema().as_arrow()))
    return tbl.refresh().current_snapshot().snapshot_id


def load_training_set(catalog: Catalog, snapshot_id: int, table: str = TABLE) -> pd.DataFrame:
    """Đọc lại đúng tập đã train ở snapshot_id (time travel)."""
    return catalog.load_table(table).scan(snapshot_id=snapshot_id).to_pandas()
