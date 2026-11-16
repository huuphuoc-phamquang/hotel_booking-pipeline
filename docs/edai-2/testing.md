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

## Bổ sung final-coursework

<a id="final-11"></a>
### Unit test với Test Coverage > 90% · final · Validation & Verification

**Rubric:** final · dòng 11 · 2 điểm · nhóm *Validation & Verification*

> Unit test với Test Coverage > 90% (với proof bằng screenshot thể hiện khả năng test Web API, và sử dụng fixture, mock)

**Cần nộp (cả nhóm):** Capture màn hình đã chạy test với test coverage thoả mãn yêu cầu

**Cách làm:** [Đã có] `tests/test_risk_api.py` (coverage `risk_api` 97%) và `tests/test_drift_api.py` (coverage `drift_api` 100%, chạy KSDrift thật trên lead time phân phối gamma như generator) dùng fixture `TestClient`, mock Feast bằng monkeypatch và KServe bằng respx. [Cần làm] chụp coverage.

**Kết quả:** các test `edai2/tests/test_risk_api.py`, `edai2/tests/test_drift_api.py` chạy cục bộ và đạt (2026-11-16). Chưa có ảnh chụp trên cluster.

<a id="final-12"></a>
### Có sử dụng kỹ thuật equivalence partitioning vs boundary value analysis khi thiết kế test… · final · Validation & Verification

**Rubric:** final · dòng 12 · 2 điểm · nhóm *Validation & Verification*

> Có sử dụng kỹ thuật equivalence partitioning vs boundary value analysis khi thiết kế test cases để parametrize. (Cái này chưa được dạy, nhưng đơn giản lắm, cả nhà coi ở đây)

**Cần nộp (cả nhóm):** Capture màn hình để thể hiện đã sử dụng các kỹ thuật này

**Cách làm:** [Đã có] Các giá trị biên được kiểm: risk-api với `booking_id`, xác suất [0, 1], kích thước lô 0/1/1000/1001; drift-api với `WINDOW`−1 và `WINDOW` dòng, số cột sai, body rỗng; `drift_monitor` với lệch calibration đúng bằng ngưỡng 0,03. [Cần làm] chụp kết quả test.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="final-13"></a>
### Có sử dụng mutation testing để đánh giá hiệu quả của các test · final · Validation & Verification

**Rubric:** final · dòng 13 · 2 điểm · nhóm *Validation & Verification*

> Có sử dụng mutation testing để đánh giá hiệu quả của các test (cái này đã dạy ở lớp rồi nha cả nhà, là cái https://mutmut.readthedocs.io/). Note that you mutate only code changed, not the whole code base everytime you push your commit! Mutation score > 80%.

**Cách làm:** [Đã có] Jenkinsfile chạy mutmut chỉ cho các file thay đổi (`git diff --name-only`); `ci/check_mutation_score.py` chặn build khi score dưới 80%. [Cần làm] chụp score.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="final-14"></a>
### Idempotency testing sử dụng property-based testing · final · Validation & Verification

**Rubric:** final · dòng 14 · 2 điểm · nhóm *Validation & Verification*

> Idempotency testing sử dụng property-based testing (chuyên để tìm ra cái test case có thể tạo ra bug), ví dụ, để kiểm tra xem model prediction có generate ra kết quả consistent sau nhiều lần chạy không. You can use the library hypothesis for property-based testing, combine with crosshair backend to find bugs easier.

**Cách làm:** [Đã có] Hypothesis kiểm `test_cancel_risk_idempotent` (risk-api) và `test_predict_idempotent` (MCP): cùng một booking gọi hai lần cho cùng kết quả. [Thiết kế] Thêm backend crosshair (`settings(backend="crosshair")`).

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="final-15"></a>
### Load test the Web API to understand throughput and latency · final · Validation & Verification

**Rubric:** final · dòng 15 · 2 điểm · nhóm *Validation & Verification*

> Load test the Web API (cái Web API kéo dữ liệu) to understand throughput (req/s) and latency (generate a html file with locust as SLA)

**Cần nộp (cả nhóm):** Capture màn hình HTML output

**Cách làm:** [Đã có] `tests/locustfile.py` gửi tải tới `POST /v1/cancel-risk` của risk-api. [Cần làm] chạy `locust --headless --html docs/sla_risk_api.html`, chụp báo cáo HTML.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._
