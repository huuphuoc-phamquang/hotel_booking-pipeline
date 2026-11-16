"""Kiểm data contract (schema/contracts/booking_event.json) cho từng event trước khi Flink gán watermark.

Không dùng Schema Registry: contract là JSON Schema trong repo; event sai -> DLQ kèm reason = tên trường sai đầu tiên,
để đối chiếu với đúng số lỗi generator cài (cột violation trong event log) theo từng loại.
"""
import json
import os

from jsonschema import Draft202012Validator

CONTRACT = os.environ.get("CONTRACT_PATH", os.path.join(os.path.dirname(__file__), "..", "schema", "contracts",
                                                        "booking_event.json"))
_validator = Draft202012Validator(json.load(open(CONTRACT, encoding="utf-8")))


def violation(event: dict) -> str | None:
    """None nếu event đúng contract, ngược lại tên trường vi phạm (thiếu trường cũng trả tên trường đó)."""
    err = next(iter(sorted(_validator.iter_errors(event), key=lambda e: list(e.path))), None)
    if err is None:
        return None
    return str(err.path[0]) if err.path else err.message.split("'")[1]
