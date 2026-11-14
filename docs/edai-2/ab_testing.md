# A/B testing

A/B cho agent, LLM và model inference.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-2-52"></a>
## Perform A/B test for agents with different model config and monitor them

**Rubric:** edai-2 · dòng 52 · 1 điểm · nhóm *A/B Testing* › *When you deploy a new model, don't replace the old one directly, you should do A/B test, monitor it, and deploy.*

**Cần nộp (cả nhóm):** Document về A/B test được implement như thế nào, dashboard như thế nào

**Cách làm:** [Thiết kế] 2 ModelConfig (v1/v2) cho 2 bản policy-agent, agentgateway chia A2A 50/50; Grafana so latency, token, tỉ lệ tool lỗi, tỉ lệ đề xuất bị Reject. [Cần làm] dashboard.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-53"></a>
## Perform A/B test for different LLM versions on the LLM inference platform

**Rubric:** edai-2 · dòng 53 · 1 điểm · nhóm *A/B Testing* › *When you deploy a new model, don't replace the old one directly, you should do A/B test, monitor it, and deploy.*

**Cách làm:** [Đã có] agentgateway chia weight 90/10 qwen v1 / v2. [Cần làm] dashboard latency / token / lỗi theo version.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

## Bổ sung final-coursework

<a id="final-52"></a>
### Perform A/B traffic split for 2 versions of inference service

**Rubric:** final · dòng 52 · 1 điểm · nhóm *A/B Testing* › *When you deploy a new model, don't replace the old one directly, you should do A/B test, monitor it, and deploy. It's simple, take a look here*

> Perform A/B traffic split for 2 versions of inference service (deploy via CI/CD)

**Cần nộp (cả nhóm):** Capture màn hình thể hiện cách mọi người thực hiện A/B test và dashboard để đánh giá kết quả A/B test

**Cách làm:** [Thiết kế] 1 InferenceService cancel-risk: Jenkins apply image v2 (retrain sau drift) với canaryTrafficPercent: 50, KServe giữ revision v1 (train tháng 1-6/2025) làm stable và chia 50/50 giữa 2 revision; promote = bỏ canaryTrafficPercent, rollback = đặt 0.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-53"></a>
### Setup monitoring dashboard to monitor 2 versions.

**Rubric:** final · dòng 53 · 1 điểm · nhóm *A/B Testing* › *When you deploy a new model, don't replace the old one directly, you should do A/B test, monitor it, and deploy. It's simple, take a look here*

> Setup monitoring dashboard to monitor 2 versions. Assumption: we also don't have groundtruth to monitor drift here!

**Cách làm:** [Thiết kế] Grafana theo revision của InferenceService cancel-risk: latency, phân bố xác suất dự báo, tỉ lệ huỷ dự báo, drift p-value; kèm Brier so với xác suất thật (bucket truth của generator, join gold.booking_risk) (Idea 2).

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
