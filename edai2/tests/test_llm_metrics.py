"""detect_pii: chặn số thẻ thật (qua Luhn) nhưng không chặn mã booking (BK-<id> hoặc số không qua Luhn)."""
import pytest

from llm_metrics import detect_pii, luhn_ok


@pytest.mark.parametrize("text, pii", [
    ("thẻ của tôi 4111 1111 1111 1111", "card"),            # số thẻ test Visa, qua Luhn
    ("4111-1111-1111-1111 hết hạn 12/28", "card"),
    ("booking BK-3650000000123 bị huỷ chưa?", None),         # mã booking hiển thị dạng BK-
    ("BK-4111111111111111", None),                           # kể cả số qua Luhn, đứng sau BK- là mã booking
    ("số 4111 1111 1111 1112", None),                        # không qua Luhn
    ("gọi 0912345678", "phone_vn"),
    ("cccd 012345678901", "cccd"),
    ("mail a.b@example.com", "email"),
    ("đêm 30/4 nên bán vượt bao nhiêu phòng?", None),
])
def test_detect_pii(text, pii):
    assert detect_pii(text) == pii


def test_luhn():
    assert luhn_ok("4111111111111111") and luhn_ok("5555 5555 5555 4444") and not luhn_ok("4111111111111112")


async def test_chat_streams_and_records_metrics():
    """chat(): ghép nội dung stream, đếm token từ usage, đo TTFT; prompt có PII bị chặn trước khi gọi gateway."""
    import httpx
    import respx
    import llm_metrics as m
    sse = "\n".join([
        'data: {"choices":[{"delta":{"content":"Nên "}}]}',
        'data: {"choices":[{"delta":{"content":"bán vượt 3 phòng"}}]}',
        'data: {"choices":[],"usage":{"prompt_tokens":12,"completion_tokens":5,"total_tokens":17}}',
        "data: [DONE]", ""])
    with respx.mock:
        respx.post(m.GATEWAY).mock(return_value=httpx.Response(200, text=sse))
        async with httpx.AsyncClient() as client:
            before = m.TOKENS.labels("qwen", "total")._value.get()
            out = await m.chat("policy-agent", "qwen", [{"role": "user", "content": "đêm 30/4?"}], client)
            assert out == "Nên bán vượt 3 phòng"
            assert m.TOKENS.labels("qwen", "total")._value.get() == before + 17
            with pytest.raises(ValueError):
                await m.chat("policy-agent", "qwen", [{"role": "user", "content": "thẻ 4111 1111 1111 1111"}], client)
