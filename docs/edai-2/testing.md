# Validation & verification

Unit test, EP/BVA, mutation, property-based, load test.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-2-28"></a>
## Unit test với Test Coverage > 90% · edai-2 · Validation & Verification

**Rubric:** edai-2 · dòng 28 · 1 điểm · nhóm *Validation & Verification*

> PR Testing Unit test với Test Coverage > 90% (với proof bằng screenshot thể hiện khả năng test Web API, và sử dụng fixture, mock)

**Cần nộp (cả nhóm):** Document show kết quả test + link tới các file code có dùng kỹ thuật này (nếu có nhiều file thì chỉ cần link tới 1 file là được)

**Cách làm:** [Đã có] 25 test (sau khi bỏ test cọc), fixture + monkeypatch; coverage 95% đo trước lần sửa, cần chạy lại. [Pricing] test cho optimizer, guardrails; giữ > 90%.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-29"></a>
## Có sử dụng kỹ thuật equivalence partitioning vs boundary value analysis khi thiết kế test… · edai-2 · Validation & Verification

**Rubric:** edai-2 · dòng 29 · 2 điểm · nhóm *Validation & Verification*

> PR Testing Có sử dụng kỹ thuật equivalence partitioning vs boundary value analysis khi thiết kế test cases để parametrize. (Cái này chưa được dạy, nhưng đơn giản lắm, cả nhà coi ở đây)

**Cách làm:** [Đã có] đã bỏ DEPOSIT_THRESHOLD: parametrize biên xác suất [0, 1] của predict_cancellation và biên BookingRequest. [Cần làm] test biên overbooking (K tại ngưỡng c_spoil/(c_spoil+c_walk)). [Pricing] EP/BVA cho guardrails: sàn, trần, ±15%/ngày.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-30"></a>
## Có sử dụng mutation testing để đánh giá hiệu quả của các test · edai-2 · Validation & Verification

**Rubric:** edai-2 · dòng 30 · 2 điểm · nhóm *Validation & Verification*

> PR Testing Có sử dụng mutation testing để đánh giá hiệu quả của các test (cái này đã dạy ở lớp rồi nha cả nhà, là cái https://mutmut.readthedocs.io/). Note that you mutate only code changed, not the whole code base everytime you push your commit! Mutation score > 80%.

**Cách làm:** [Đã có] mutmut chỉ trên file thay đổi trong Jenkins. [Cần làm] ci/check_mutation_score.py chưa có; chụp score > 80%.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-31"></a>
## Idempotency testing sử dụng property-based testing · edai-2 · Validation & Verification

**Rubric:** edai-2 · dòng 31 · 2 điểm · nhóm *Validation & Verification*

> PR Testing Idempotency testing sử dụng property-based testing (chuyên để tìm ra cái test case có thể tạo ra bug), ví dụ, để kiểm tra xem model prediction có generate ra kết quả consistent sau nhiều lần chạy không. You can use the library hypothesis for property-based testing, combine with crosshair backend to find bugs easier.

**Cách làm:** [Đã có] hypothesis test_predict_idempotent. [Pricing] property: giá luôn trong [sàn, trần]; đổi customer_id thì giá không đổi.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-32"></a>
## Load test the Web API to understand throughput and latency · edai-2 · Validation & Verification

**Rubric:** edai-2 · dòng 32 · 2 điểm · nhóm *Validation & Verification*

> Local Testing Load test the Web API (cái Web API kéo dữ liệu) to understand throughput (req/s) and latency (generate a html file with locust as SLA)

**Cách làm:** [Đã có] tests/locustfile.py. [Cần làm] chạy --html, chụp RPS / p95; [Pricing] kiểm ngân sách 30-50ms cho quote_price.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

## Bổ sung final-coursework

<a id="final-11"></a>
### Unit test với Test Coverage > 90% · final · Validation & Verification

**Rubric:** final · dòng 11 · 2 điểm · nhóm *Validation & Verification*

> Unit test với Test Coverage > 90% (với proof bằng screenshot thể hiện khả năng test Web API, và sử dụng fixture, mock)

**Cần nộp (cả nhóm):** Capture màn hình đã chạy test với test coverage thoả mãn yêu cầu

**Cách làm:** [Thiết kế] pytest cho pricing-api và drift-api: fixture TestClient, mock Feast + KServe (respx/monkeypatch), coverage > 90% (test MCP hiện có đạt 95% làm mẫu). [Cần làm] chụp coverage.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-12"></a>
### Có sử dụng kỹ thuật equivalence partitioning vs boundary value analysis khi thiết kế test… · final · Validation & Verification

**Rubric:** final · dòng 12 · 2 điểm · nhóm *Validation & Verification*

> Có sử dụng kỹ thuật equivalence partitioning vs boundary value analysis khi thiết kế test cases để parametrize. (Cái này chưa được dạy, nhưng đơn giản lắm, cả nhà coi ở đây)

**Cần nộp (cả nhóm):** Capture màn hình để thể hiện đã sử dụng các kỹ thuật này

**Cách làm:** [Thiết kế] parametrize theo lớp: stay_date hôm qua/hôm nay/+365/+366, rate_plan hợp lệ/lạ, giá đúng sàn/trần, đổi giá 14,9%/15%/15,1%; drift-api: p_val 0,049/0,05/0,051.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-13"></a>
### Có sử dụng mutation testing để đánh giá hiệu quả của các test · final · Validation & Verification

**Rubric:** final · dòng 13 · 2 điểm · nhóm *Validation & Verification*

> Có sử dụng mutation testing để đánh giá hiệu quả của các test (cái này đã dạy ở lớp rồi nha cả nhà, là cái https://mutmut.readthedocs.io/). Note that you mutate only code changed, not the whole code base everytime you push your commit! Mutation score > 80%.

**Cách làm:** [Đã có] Jenkinsfile chạy mutmut cho file đổi. [Cần làm] ci/check_mutation_score.py (chưa có) chặn khi score < 80%; mutate theo git diff --name-only.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-14"></a>
### Idempotency testing sử dụng property-based testing · final · Validation & Verification

**Rubric:** final · dòng 14 · 2 điểm · nhóm *Validation & Verification*

> Idempotency testing sử dụng property-based testing (chuyên để tìm ra cái test case có thể tạo ra bug), ví dụ, để kiểm tra xem model prediction có generate ra kết quả consistent sau nhiều lần chạy không. You can use the library hypothesis for property-based testing, combine with crosshair backend to find bugs easier.

**Cách làm:** [Đã có] hypothesis idempotency trong tests/test_server.py. [Thiết kế] thêm hypothesis-crosshair (settings(backend="crosshair")): cùng input gọi /v1/quote 2 lần ra cùng giá; giá luôn trong [sàn, trần]; đổi customer_id không đổi giá.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-15"></a>
### Load test the Web API to understand throughput and latency · final · Validation & Verification

**Rubric:** final · dòng 15 · 2 điểm · nhóm *Validation & Verification*

> Load test the Web API (cái Web API kéo dữ liệu) to understand throughput (req/s) and latency (generate a html file with locust as SLA)

**Cần nộp (cả nhóm):** Capture màn hình HTML output

**Cách làm:** [Đã có] tests/locustfile.py. [Thiết kế] thêm task /v1/quote, chạy locust --headless --html docs/sla_pricing_api.html, SLA p95 ≤ 50ms. [Cần làm] chụp HTML.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
