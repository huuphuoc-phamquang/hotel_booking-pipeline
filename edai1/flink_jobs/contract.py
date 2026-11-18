"""Kiểm data contract (schema/contracts/booking_event.json) cho từng event trước khi Flink gán watermark.

Không dùng Schema Registry: contract là JSON Schema trong repo; event sai -> DLQ kèm reason = tên trường sai đầu tiên,
để đối chiếu với đúng số lỗi generator cài (cột violation trong event log) theo từng loại.
"""
import json
import os
import time

from jsonschema import Draft202012Validator

CONTRACT = os.environ.get("CONTRACT_PATH", os.path.join(os.path.dirname(__file__), "..", "schema", "contracts",
                                                        "booking_event.json"))
# FORMAT_CHECKER: mặc định jsonschema bỏ qua "format" (vd checkin dạng date) nếu không truyền checker
_validator = Draft202012Validator(json.load(open(CONTRACT, encoding="utf-8")),
                                  format_checker=Draft202012Validator.FORMAT_CHECKER)


MAX_FUTURE_MS = 24 * 3600 * 1000                         # event_time quá giờ máy > 1 ngày: sai đơn vị/đồng hồ


def violation(event: dict) -> str | None:
    """None nếu event đúng contract, ngược lại tên trường vi phạm (thiếu trường cũng trả tên trường đó).
    JSON Schema không có cận động: event_time ở tương lai (so với giờ máy) kiểm riêng, để không đẩy watermark của Flink."""
    err = next(iter(sorted(_validator.iter_errors(event), key=lambda e: list(e.path))), None)
    if err is None:
        return "event_time" if event["event_time"] > time.time() * 1000 + MAX_FUTURE_MS else None
    if err.path:
        return str(err.path[0])
    if err.validator == "required":                         # "'event_time' is a required property"
        return err.message.split("'")[1]
    return err.validator                                     # payload không phải object (vd 123, []): "type"
