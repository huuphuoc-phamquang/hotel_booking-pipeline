"""Data versioning cho tập train của cancel-risk: Iceberg ml.train_cancel_risk, upsert theo booking_id.

Rubric final › Data versioning (incremental): mỗi lần train ghi tập train vào cùng bảng bằng upsert (chỉ dòng mới hoặc
đổi nhãn sinh file mới, dòng giống hệt không ghi lại), MLflow log snapshot_id; tái lập đúng tập đã train bằng
scan(snapshot_id=...) (= VERSION AS OF của Spark SQL). Catalog `lake` = Iceberg JDBC/SQL catalog trên PostgreSQL như Spark.
"""
import pandas as pd
import pyarrow as pa
from pyiceberg.catalog import Catalog
from pyiceberg.exceptions import NoSuchTableError

TABLE = "ml.train_cancel_risk"


def snapshot_training_set(catalog: Catalog, df: pd.DataFrame, table: str = TABLE) -> int:
    """Upsert df vào bảng (tạo nếu chưa có) và trả snapshot_id hiện hành sau khi ghi."""
    data = pa.Table.from_pandas(df, preserve_index=False)
    try:
        tbl = catalog.load_table(table)
    except NoSuchTableError:
        catalog.create_namespace_if_not_exists(table.split(".")[0])
        tbl = catalog.create_table(table, schema=data.schema)
    tbl.upsert(data.cast(tbl.schema().as_arrow()), join_cols=["booking_id"])
    return tbl.refresh().current_snapshot().snapshot_id


def load_training_set(catalog: Catalog, snapshot_id: int, table: str = TABLE) -> pd.DataFrame:
    """Đọc lại đúng tập đã train ở snapshot_id (time travel)."""
    return catalog.load_table(table).scan(snapshot_id=snapshot_id).to_pandas()
