"""Load test Web API kéo dữ liệu (booking-mcp: REST /v1/cancel-risk, cùng logic tool predict_cancellation:
feature theo booking_id từ Feast online + KServe cancel-risk).

Rubric edai-2 › Validation & Verification › Load test (locust HTML làm SLA):
  locust -f locustfile.py --host https://api.booking.local --headless -u 200 -r 20 -t 5m --html sla_report.html
Đọc trong report: RPS, p50/p95/p99 latency, tỉ lệ lỗi. booking_id lấy từ dải ID của generator
(ngày·10^10 + shard·10^7 + i); booking không có trên online store trả 404, tính là lỗi trong report.
BOOKING_IDS=<file> (mỗi dòng 1 booking_id, vd lấy từ gold.fact_bookings) thì chỉ gửi các ID đó: dữ liệu ít ngày.
"""
import os
import random

from locust import HttpUser, between, task

IDS = [int(x) for x in open(os.environ["BOOKING_IDS"]).read().split()] if os.environ.get("BOOKING_IDS") else None


class BookingMcpUser(HttpUser):
    """Mô phỏng revenue manager chấm điểm booking của các ngày gần đây."""
    wait_time = between(0.1, 0.5)

    @task(5)
    def cancel_risk(self):
        booking_id = random.choice(IDS) if IDS else \
            random.randint(380, 394) * 10**10 + random.randint(0, 15) * 10**7 + random.randint(0, 20_000)
        self.client.post("/v1/cancel-risk", json={"booking_id": booking_id}, name="POST /v1/cancel-risk")

    @task(1)
    def health(self):
        self.client.get("/healthz")
