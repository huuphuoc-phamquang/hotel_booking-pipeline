# Validation & verification

Unit test, phân lớp tương đương và giá trị biên (EP/BVA), mutation test, property-based test và load test.

Mỗi mục dưới đây ứng với một dòng của rubric. Phần **Cách làm** mô tả giải pháp đã triển khai, đồng bộ từ
cột F của rubric. Phần **Kết quả** ghi test đã chạy, số liệu đo được hoặc ảnh chụp (`docs/images/`).

<a id="edai-2-28"></a>
## Unit test với Test Coverage > 90% · edai-2 · Validation & Verification

**Rubric:** edai-2 · dòng 28 · 1 điểm · nhóm *Validation & Verification*

> PR Testing Unit test với Test Coverage > 90% (với proof bằng screenshot thể hiện khả năng test Web API, và sử dụng fixture, mock)

**Cần nộp (cả nhóm):** Document show kết quả test + link tới các file code có dùng kỹ thuật này (nếu có nhiều file thì chỉ cần link tới 1 file là được)

**Cách làm:** [Đã có] `tests/test_server.py` và `tests/test_risk_api.py` gồm 31 test, dùng fixture, monkeypatch và respx; coverage của `server.py` đạt 94%, `risk_api.py` đạt 95%.

**Kết quả:** các test `edai2/tests/test_server.py`, `edai2/tests/test_risk_api.py` chạy cục bộ và đạt (2026-11-16). Chưa có ảnh chụp trên cluster.

<a id="edai-2-29"></a>
## Có sử dụng kỹ thuật equivalence partitioning vs boundary value analysis khi thiết kế test… · edai-2 · Validation & Verification

**Rubric:** edai-2 · dòng 29 · 2 điểm · nhóm *Validation & Verification*

> PR Testing Có sử dụng kỹ thuật equivalence partitioning vs boundary value analysis khi thiết kế test cases để parametrize. (Cái này chưa được dạy, nhưng đơn giản lắm, cả nhà coi ở đây)

**Cách làm:** [Đã có] Test tham số hoá các giá trị biên: xác suất [0, 1] (MCP và risk-api), `booking_id`, và K (p = 0 hoặc 1, không có booking, chi phí ≤ 0). `tests/test_overbooking.py` dùng hypothesis so K với định nghĩa trực tiếp.

**Kết quả:** các test `edai2/tests/test_overbooking.py` chạy cục bộ và đạt (2026-11-16). Chưa có ảnh chụp trên cluster.

<a id="edai-2-30"></a>
## Có sử dụng mutation testing để đánh giá hiệu quả của các test · edai-2 · Validation & Verification

**Rubric:** edai-2 · dòng 30 · 2 điểm · nhóm *Validation & Verification*

> PR Testing Có sử dụng mutation testing để đánh giá hiệu quả của các test (cái này đã dạy ở lớp rồi nha cả nhà, là cái https://mutmut.readthedocs.io/). Note that you mutate only code changed, not the whole code base everytime you push your commit! Mutation score > 80%.

**Cách làm:** [Đã có] Jenkins chạy mutmut chỉ trên các file thay đổi; `ci/check_mutation_score.py` chặn build khi score dưới 80%. [Cần làm] chụp score trên 80%.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-2-31"></a>
## Idempotency testing sử dụng property-based testing · edai-2 · Validation & Verification

**Rubric:** edai-2 · dòng 31 · 2 điểm · nhóm *Validation & Verification*

> PR Testing Idempotency testing sử dụng property-based testing (chuyên để tìm ra cái test case có thể tạo ra bug), ví dụ, để kiểm tra xem model prediction có generate ra kết quả consistent sau nhiều lần chạy không. You can use the library hypothesis for property-based testing, combine with crosshair backend to find bugs easier.

**Cách làm:** [Đã có] Hypothesis kiểm `test_predict_idempotent` (MCP) và `test_cancel_risk_idempotent` (risk-api): cùng một booking gọi hai lần cho cùng kết quả.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-2-32"></a>
## Load test the Web API to understand throughput and latency · edai-2 · Validation & Verification

**Rubric:** edai-2 · dòng 32 · 2 điểm · nhóm *Validation & Verification*

> Local Testing Load test the Web API (cái Web API kéo dữ liệu) to understand throughput (req/s) and latency (generate a html file with locust as SLA)

**Cách làm:** [Đã có] `tests/locustfile.py` gửi tải tới `POST /v1/cancel-risk` của risk-api. [Cần làm] chạy với `--html`, chụp RPS và p95.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._
