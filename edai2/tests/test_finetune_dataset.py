"""Bộ SFT (llm_platform/finetune/build_dataset.py): đúng định dạng chat, tất định, K trong câu trả lời = limit()."""
import re
import sys

sys.path.insert(0, "llm_platform/finetune")
from build_dataset import build  # noqa: E402

from overbooking import limit  # noqa: E402


def test_format_and_determinism():
    rows = build(50)
    assert rows == build(50)
    for r in rows:
        roles = [m["role"] for m in r["messages"]]
        assert roles == ["system", "user", "assistant"] and all(m["content"].strip() for m in r["messages"])
    kinds = {r["kind"] for r in rows}
    assert kinds == {"policy", "overbook", "safety"}


def test_overbook_answers_use_system_formula():
    for r in build(100):
        if r["kind"] != "overbook":
            continue
        q, a = r["messages"][1]["content"], r["messages"][2]["content"]
        probs = [float(x) for x in re.search(r"\[(.*)\]", q).group(1).split(",")]
        assert f"K = {limit(probs, 1.0, 3.0)} phòng" in a and "duyệt" in a


def test_safety_answers_never_echo_card():
    for r in build(0):
        if r["kind"] == "safety":
            assert "4111" not in r["messages"][2]["content"] and "BK-" in r["messages"][2]["content"]
