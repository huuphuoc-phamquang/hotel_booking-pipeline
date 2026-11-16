# Validation & verification

Unit test, EP/BVA, mutation, property-based, load test.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-2-28"></a>
## Unit test với Test Coverage > 90% · edai-2 · Validation & Verification

**Rubric:** edai-2 · dòng 28 · 1 điểm · nhóm *Validation & Verification*

> PR Testing Unit test với Test Coverage > 90% (với proof bằng screenshot thể hiện khả năng test Web API, và sử dụng fixture, mock)

**Cần nộp (cả nhóm):** Document show kết quả test + link tới các file code có dùng kỹ thuật này (nếu có nhiều file thì chỉ cần link tới 1 file là được)

**Cách làm:** [Đã có] tests/test_server.py + tests/test_risk_api.py: 31 test, fixture + monkeypatch + respx; coverage server.py 94%, risk_api.py 95%.

**Kết quả:** chạy cục bộ, pass (2026-11-16): `edai2/tests/test_server.py`, `edai2/tests/test_risk_api.py`. _Chưa có ảnh chụp trên cluster._

<a id="edai-2-29"></a>
## Có sử dụng kỹ thuật equivalence partitioning vs boundary value analysis khi thiết kế test… · edai-2 · Validation & Verification

**Rubric:** edai-2 · dòng 29 · 2 điểm · nhóm *Validation & Verification*

> PR Testing Có sử dụng kỹ thuật equivalence partitioning vs boundary value analysis khi thiết kế test cases để parametrize. (Cái này chưa được dạy, nhưng đơn giản lắm, cả nhà coi ở đây)

**Cách làm:** [Đã có] parametrize biên xác suất [0, 1] (MCP và risk-api), biên booking_id, biên K (p = 0 / 1, không có booking, chi phí <= 0) và K so với định nghĩa trực tiếp qua hypothesis (tests/test_overbooking.py).

**Kết quả:** chạy cục bộ, pass (2026-11-16): `edai2/tests/test_overbooking.py`. _Chưa có ảnh chụp trên cluster._

<a id="edai-2-30"></a>
## Có sử dụng mutation testing để đánh giá hiệu quả của các test · edai-2 · Validation & Verification

**Rubric:** edai-2 · dòng 30 · 2 điểm · nhóm *Validation & Verification*

> PR Testing Có sử dụng mutation testing để đánh giá hiệu quả của các test (cái này đã dạy ở lớp rồi nha cả nhà, là cái https://mutmut.readthedocs.io/). Note that you mutate only code changed, not the whole code base everytime you push your commit! Mutation score > 80%.

**Cách làm:** [Đã có] mutmut chỉ trên file thay đổi trong Jenkins + ci/check_mutation_score.py chặn khi < 80%. [Cần làm] chụp score > 80%.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-31"></a>
## Idempotency testing sử dụng property-based testing · edai-2 · Validation & Verification

**Rubric:** edai-2 · dòng 31 · 2 điểm · nhóm *Validation & Verification*

> PR Testing Idempotency testing sử dụng property-based testing (chuyên để tìm ra cái test case có thể tạo ra bug), ví dụ, để kiểm tra xem model prediction có generate ra kết quả consistent sau nhiều lần chạy không. You can use the library hypothesis for property-based testing, combine with crosshair backend to find bugs easier.

**Cách làm:** [Đã có] hypothesis test_predict_idempotent (MCP) và test_cancel_risk_idempotent (risk-api): cùng booking gọi 2 lần ra cùng kết quả.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-32"></a>
## Load test the Web API to understand throughput and latency · edai-2 · Validation & Verification

**Rubric:** edai-2 · dòng 32 · 2 điểm · nhóm *Validation & Verification*

> Local Testing Load test the Web API (cái Web API kéo dữ liệu) to understand throughput (req/s) and latency (generate a html file with locust as SLA)

**Cách làm:** [Đã có] tests/locustfile.py nhắm POST /v1/cancel-risk của risk-api. [Cần làm] chạy --html, chụp RPS / p95.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

## Bổ sung final-coursework

<a id="final-11"></a>
### Unit test với Test Coverage > 90% · final · Validation & Verification

**Rubric:** final · dòng 11 · 2 điểm · nhóm *Validation & Verification*

> Unit test với Test Coverage > 90% (với proof bằng screenshot thể hiện khả năng test Web API, và sử dụng fixture, mock)

**Cần nộp (cả nhóm):** Capture màn hình đã chạy test với test coverage thoả mãn yêu cầu

**Cách làm:** [Đã có] tests/test_risk_api.py (risk_api 97%) và tests/test_drift_api.py (drift_api 100%, KSDrift thật trên lead time gamma như generator): fixture TestClient, mock Feast (monkeypatch) + KServe (respx). [Cần làm] chụp coverage.

**Kết quả:** chạy cục bộ, pass (2026-11-16): `edai2/tests/test_risk_api.py`, `edai2/tests/test_drift_api.py`. _Chưa có ảnh chụp trên cluster._

<a id="final-12"></a>
### Có sử dụng kỹ thuật equivalence partitioning vs boundary value analysis khi thiết kế test… · final · Validation & Verification

**Rubric:** final · dòng 12 · 2 điểm · nhóm *Validation & Verification*

> Có sử dụng kỹ thuật equivalence partitioning vs boundary value analysis khi thiết kế test cases để parametrize. (Cái này chưa được dạy, nhưng đơn giản lắm, cả nhà coi ở đây)

**Cần nộp (cả nhóm):** Capture màn hình để thể hiện đã sử dụng các kỹ thuật này

**Cách làm:** [Đã có] risk-api: biên booking_id, xác suất [0, 1], kích thước lô 0/1/1000/1001; drift-api: WINDOW-1 / WINDOW dòng, số cột sai, body rỗng; drift_monitor: lệch calibration đúng bằng ngưỡng 0,03. [Cần làm] chụp kết quả test.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-13"></a>
### Có sử dụng mutation testing để đánh giá hiệu quả của các test · final · Validation & Verification

**Rubric:** final · dòng 13 · 2 điểm · nhóm *Validation & Verification*

> Có sử dụng mutation testing để đánh giá hiệu quả của các test (cái này đã dạy ở lớp rồi nha cả nhà, là cái https://mutmut.readthedocs.io/). Note that you mutate only code changed, not the whole code base everytime you push your commit! Mutation score > 80%.

**Cách làm:** [Đã có] Jenkinsfile chạy mutmut chỉ cho file đổi (git diff --name-only), ci/check_mutation_score.py chặn khi score < 80%. [Cần làm] chụp score.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-14"></a>
### Idempotency testing sử dụng property-based testing · final · Validation & Verification

**Rubric:** final · dòng 14 · 2 điểm · nhóm *Validation & Verification*

> Idempotency testing sử dụng property-based testing (chuyên để tìm ra cái test case có thể tạo ra bug), ví dụ, để kiểm tra xem model prediction có generate ra kết quả consistent sau nhiều lần chạy không. You can use the library hypothesis for property-based testing, combine with crosshair backend to find bugs easier.

**Cách làm:** [Đã có] hypothesis: test_cancel_risk_idempotent (risk-api) và test_predict_idempotent (MCP), cùng booking gọi 2 lần ra cùng kết quả. [Thiết kế] thêm backend crosshair (settings(backend="crosshair")).

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-15"></a>
### Load test the Web API to understand throughput and latency · final · Validation & Verification

**Rubric:** final · dòng 15 · 2 điểm · nhóm *Validation & Verification*

> Load test the Web API (cái Web API kéo dữ liệu) to understand throughput (req/s) and latency (generate a html file with locust as SLA)

**Cần nộp (cả nhóm):** Capture màn hình HTML output

**Cách làm:** [Đã có] tests/locustfile.py nhắm POST /v1/cancel-risk của risk-api. [Cần làm] locust --headless --html docs/sla_risk_api.html, chụp HTML.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
