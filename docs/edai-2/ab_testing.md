# A/B testing

A/B cho agent, LLM và model inference.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-2-52"></a>
## Perform A/B test for agents with different model config and monitor them

**Rubric:** edai-2 · dòng 52 · 1 điểm · nhóm *A/B Testing* › *When you deploy a new model, don't replace the old one directly, you should do A/B test, monitor it, and deploy.*

**Cần nộp (cả nhóm):** Document về A/B test được implement như thế nào, dashboard như thế nào

**Cách làm:** [Đã có] agents.yaml: policy-agent-v2 dùng ModelConfig model-config-v2 (route /llm-v2 chỉ tới qwen-v2) + prompt riêng; agentgateway chia /a2a/policy-agent 50/50. [Cần làm] dashboard so latency, token, tỉ lệ tool lỗi, tỉ lệ đề xuất bị Reject.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-53"></a>
## Perform A/B test for different LLM versions on the LLM inference platform

**Rubric:** edai-2 · dòng 53 · 1 điểm · nhóm *A/B Testing* › *When you deploy a new model, don't replace the old one directly, you should do A/B test, monitor it, and deploy.*

**Cách làm:** [Đã có] agentgateway chia weight 90/10 qwen v1 / v2; dashboard observability/dashboards/llm-agents.json (token, TTFT, round-trip theo model). [Cần làm] chụp dashboard.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

## Bổ sung final-coursework

<a id="final-52"></a>
### Perform A/B traffic split for 2 versions of inference service

**Rubric:** final · dòng 52 · 1 điểm · nhóm *A/B Testing* › *When you deploy a new model, don't replace the old one directly, you should do A/B test, monitor it, and deploy. It's simple, take a look here*

> Perform A/B traffic split for 2 versions of inference service (deploy via CI/CD)

**Cần nộp (cả nhóm):** Capture màn hình thể hiện cách mọi người thực hiện A/B test và dashboard để đánh giá kết quả A/B test

**Cách làm:** [Đã có] 1 InferenceService cancel-risk (serving/kserve-cancel-risk.yaml), edai2/ci/Jenkinsfile.ml JSON patch image v2 (retrain sau drift) với canaryTrafficPercent: 50, KServe giữ revision v1 (train [2025-01-01, 2025-06-01)) làm stable và chia 50/50 giữa 2 revision; promote = bỏ canaryTrafficPercent, rollback = đặt 0.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-53"></a>
### Setup monitoring dashboard to monitor 2 versions.

**Rubric:** final · dòng 53 · 1 điểm · nhóm *A/B Testing* › *When you deploy a new model, don't replace the old one directly, you should do A/B test, monitor it, and deploy. It's simple, take a look here*

> Setup monitoring dashboard to monitor 2 versions. Assumption: we also don't have groundtruth to monitor drift here!

**Cách làm:** [Đã có] observability/dashboards/cancel-risk-ml.json: drift p-value, PSI, lệch calibration, request / latency p95 / lỗi theo revision của InferenceService cancel-risk (A/B canary). Đã nạp thử trong Grafana 12.2. gold.booking_risk.model_version (serving/predictor.py trả version, risk-api chuyển tiếp) để so calibration / Brier từng revision. [Cần làm] panel theo version trong dashboard; chụp dashboard.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
