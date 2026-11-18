"""Great Expectations (API 1.x) cho Bronze của DP1: kiểm 1 partition ngày của từng bảng landing.

Rubric edai-1 › Data Pipeline › DP1 Validate stage. Chỉ đọc các cột cần kiểm (quotes 1 ngày ~34 triệu dòng).
Bản gửi trùng (double submit) là lỗi có chủ đích nên bookings không kiểm unique idempotency_key ở Bronze; Silver dedup.
"""
import great_expectations as gx
import great_expectations.expectations as gxe

# (lớp expectation, tham số): mỗi lần validate dựng object mới vì suite giữ tham chiếu tới expectation đã thêm
EXPECTATIONS = {
    "quotes": [(gxe.ExpectColumnValuesToNotBeNull, dict(column="quote_id")),
               (gxe.ExpectColumnValuesToBeUnique, dict(column="quote_id")),
               (gxe.ExpectColumnValuesToNotBeNull, dict(column="hotel_id")),
               (gxe.ExpectColumnValuesToBeBetween, dict(column="price", min_value=0, strict_min=True)),
               (gxe.ExpectColumnValuesToBeBetween, dict(column="nights", min_value=1))],
    "bookings": [(gxe.ExpectColumnValuesToBeUnique, dict(column="booking_id")),
                 (gxe.ExpectColumnValuesToNotBeNull, dict(column="idempotency_key")),
                 (gxe.ExpectColumnValuesToNotBeNull, dict(column="customer_id")),
                 (gxe.ExpectColumnValuesToBeInSet, dict(column="cancellation_policy", value_set=["flexible", "non_refundable"])),
                 (gxe.ExpectColumnValuesToBeBetween, dict(column="price", min_value=0, strict_min=True))],
    "cancellations": [(gxe.ExpectColumnValuesToBeUnique, dict(column="idempotency_key")),
                      (gxe.ExpectColumnValuesToNotBeNull, dict(column="cancelled_at"))],
    "payments": [(gxe.ExpectColumnValuesToBeUnique, dict(column="payment_id")),
                 (gxe.ExpectColumnValuesToBeBetween, dict(column="amount", min_value=0, strict_min=True)),
                 (gxe.ExpectColumnValuesToBeInSet, dict(column="status", value_set=["success", "failed"]))],
}


def columns(table: str) -> list[str]:
    return sorted({kw["column"] for _, kw in EXPECTATIONS[table]})


def validate_frame(table: str, df) -> gx.core.ExpectationSuiteValidationResult:
    """Chạy bộ expectation của bảng trên 1 DataFrame pandas (context ephemeral: không cần thư mục gx/)."""
    ctx = gx.get_context(mode="ephemeral")
    batch = (ctx.data_sources.add_pandas("bronze").add_dataframe_asset(f"raw_{table}")
             .add_batch_definition_whole_dataframe("partition").get_batch(batch_parameters={"dataframe": df}))
    suite = ctx.suites.add(gx.ExpectationSuite(name=f"bronze_{table}", expectations=[
        gxe.ExpectTableRowCountToBeBetween(min_value=1), *[cls(**kw) for cls, kw in EXPECTATIONS[table]]]))
    return batch.validate(suite)


def validate_shards(table: str, dataset, shards: int) -> list:
    """Validate 1 partition ngày của Bronze theo từng shard (cột shard Spark lấy từ đường dẫn landing) để bộ nhớ chỉ
    chứa 1 shard: quotes 1 ngày ~34 triệu dòng, 1 shard ~2,4 triệu. Kiểm unique theo shard tương đương cả partition vì
    id mang số shard (generator make_ids) và idempotency_key nằm cùng shard với booking gốc. Shard rỗng bỏ qua (lần huỷ
    của 1 ngày có thể không rơi vào mọi shard); cả partition rỗng thì kiểm row count trên DataFrame rỗng -> fail."""
    import pyarrow.dataset as pads
    results = []
    for s in range(shards):
        df = dataset.to_table(columns=columns(table), filter=pads.field("shard") == s).to_pandas()
        if len(df):
            results.append(validate_frame(table, df))
    return results or [validate_frame(table, dataset.schema.empty_table().select(columns(table)).to_pandas())]
