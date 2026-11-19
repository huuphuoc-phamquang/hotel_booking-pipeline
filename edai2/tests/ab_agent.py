"""A/B agent: gửi N câu hỏi tới /a2a/policy-agent/ của agentgateway (chia 50/50 giữa policy-agent và policy-agent-v2),
ghi bản nào trả lời (metadata kagent_app_name), thời gian, số tool gọi, tool lỗi và token; in bảng so sánh, lưu JSON.
Dùng: python tests/ab_agent.py <gateway_url> <jwt> [số lượt] [file_json]   (jwt: client coordinator-agent của Keycloak)
"""
import json
import statistics
import sys
import time
import urllib.request
import uuid

QUESTIONS = [
    "Booking 90000919211 có khả năng bị huỷ bao nhiêu?",
    "Giá linh hoạt được huỷ miễn phí đến khi nào, giá không hoàn tiền thì sao?",
    "Khách sạn 8528 đêm 2025-01-29 nên bán vượt bao nhiêu phòng?",
    "Booking 100001035698 có khả năng bị huỷ bao nhiêu?",
]


def ask(url: str, token: str, text: str) -> dict:
    msg = {"role": "user", "messageId": str(uuid.uuid4()), "parts": [{"kind": "text", "text": text}]}
    body = json.dumps({"jsonrpc": "2.0", "id": "1", "method": "message/send", "params": {"message": msg}}).encode()
    req = urllib.request.Request(url, body, {"Content-Type": "application/json", "Authorization": f"Bearer {token}"})
    t0 = time.perf_counter()
    res = json.load(urllib.request.urlopen(req, timeout=300)).get("result", {})
    parts = [p for m in res.get("history", []) for p in m.get("parts", []) if p.get("kind") == "data"]
    kinds = [p.get("metadata", {}).get("kagent_type") for p in parts]
    errors = sum(1 for p in parts if p.get("metadata", {}).get("kagent_type") == "function_response"
                 and (p["data"].get("response") or {}).get("isError"))
    usage = res.get("metadata", {}).get("kagent_usage_metadata") or {}
    return {"variant": res.get("metadata", {}).get("kagent_app_name", "?"), "question": text,
            "seconds": round(time.perf_counter() - t0, 2), "state": res.get("status", {}).get("state"),
            "tool_calls": kinds.count("function_call"), "tool_errors": errors,
            "prompt_tokens": usage.get("promptTokenCount"), "output_tokens": usage.get("candidatesTokenCount")}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    url, token = sys.argv[1].rstrip("/") + "/a2a/policy-agent/", sys.argv[2]
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 20
    rows = []
    for i in range(n):
        try:
            rows.append(ask(url, token, QUESTIONS[i % len(QUESTIONS)]))
        except Exception as e:   # lượt lỗi vẫn tính vào bảng (state=error)
            rows.append({"variant": "?", "question": QUESTIONS[i % len(QUESTIONS)], "seconds": None, "state": f"error: {e}",
                         "tool_calls": 0, "tool_errors": 0, "prompt_tokens": None, "output_tokens": None})
        r = rows[-1]
        print(f"{i + 1:>2} {r['variant']:<32} {r['seconds']!s:>6}s {r['state']:<10} tools={r['tool_calls']}")
    print(f"\n{'variant':<32} {'n':>3} {'p50 s':>6} {'max s':>6} {'ok':>4} {'tool err':>8} {'out tok':>8}")
    for v in sorted({r["variant"] for r in rows}):
        g = [r for r in rows if r["variant"] == v]
        secs = [r["seconds"] for r in g if r["seconds"] is not None]
        out = [r["output_tokens"] for r in g if r["output_tokens"] is not None]
        print(f"{v:<32} {len(g):>3} {statistics.median(secs) if secs else 0:>6.1f} {max(secs) if secs else 0:>6.1f} "
              f"{sum(r['state'] == 'completed' for r in g):>4} {sum(r['tool_errors'] for r in g):>8} "
              f"{statistics.mean(out) if out else 0:>8.0f}")
    if len(sys.argv) > 4:
        json.dump(rows, open(sys.argv[4], "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
