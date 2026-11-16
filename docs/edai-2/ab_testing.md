# A/B testing

A/B testing cho agent, LLM và model inference.

Mỗi mục dưới đây ứng với một dòng của rubric. Phần **Cách làm** mô tả giải pháp đã triển khai, đồng bộ từ
cột F của rubric. Phần **Kết quả** ghi test đã chạy, số liệu đo được hoặc ảnh chụp (`docs/images/`).

<a id="edai-2-52"></a>
## Perform A/B test for agents with different model config and monitor them

**Rubric:** edai-2 · dòng 52 · 1 điểm · nhóm *A/B Testing* › *When you deploy a new model, don't replace the old one directly, you should do A/B test, monitor it, and deploy.*

**Cần nộp (cả nhóm):** Document về A/B test được implement như thế nào, dashboard như thế nào

**Cách làm:** [Đã có] Trong `agents.yaml`, policy-agent-v2 dùng ModelConfig `model-config-v2` (route `/llm-v2` chỉ tới qwen-v2) và prompt riêng; agentgateway chia `/a2a/policy-agent` 50/50. [Cần làm] dashboard so sánh latency, token, tỉ lệ tool lỗi và tỉ lệ đề xuất bị từ chối.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-2-53"></a>
## Perform A/B test for different LLM versions on the LLM inference platform

**Rubric:** edai-2 · dòng 53 · 1 điểm · nhóm *A/B Testing* › *When you deploy a new model, don't replace the old one directly, you should do A/B test, monitor it, and deploy.*

**Cách làm:** [Đã có] agentgateway chia trọng số 90/10 giữa qwen v1 và v2; dashboard `observability/dashboards/llm-agents.json` hiển thị token, TTFT, round-trip theo model. [Cần làm] chụp dashboard.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

## Bổ sung final-coursework

<a id="final-52"></a>
### Perform A/B traffic split for 2 versions of inference service

**Rubric:** final · dòng 52 · 1 điểm · nhóm *A/B Testing* › *When you deploy a new model, don't replace the old one directly, you should do A/B test, monitor it, and deploy. It's simple, take a look here*

> Perform A/B traffic split for 2 versions of inference service (deploy via CI/CD)

**Cần nộp (cả nhóm):** Capture màn hình thể hiện cách mọi người thực hiện A/B test và dashboard để đánh giá kết quả A/B test

**Cách làm:** [Đã có] Một InferenceService `cancel-risk` (`serving/kserve-cancel-risk.yaml`). `edai2/ci/Jenkinsfile.ml` dùng JSON patch đổi sang image v2 (retrain sau drift) với `canaryTrafficPercent: 50`; KServe giữ revision v1 (train trên [2025-01-01, 2025-06-01)) làm bản ổn định và chia 50/50 giữa hai revision. Promote bằng cách đặt 100, rollback bằng cách đặt 0. Khi promote, Jenkins đổi image của `cancel-risk-bulk` và gọi DAG `rescore_active` để chấm lại các booking đang giữ phòng bằng bản mới.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="final-53"></a>
### Setup monitoring dashboard to monitor 2 versions.

**Rubric:** final · dòng 53 · 1 điểm · nhóm *A/B Testing* › *When you deploy a new model, don't replace the old one directly, you should do A/B test, monitor it, and deploy. It's simple, take a look here*

> Setup monitoring dashboard to monitor 2 versions. Assumption: we also don't have groundtruth to monitor drift here!

**Cách làm:** [Đã có] `observability/dashboards/cancel-risk-ml.json` hiển thị p-value drift, PSI, lệch calibration, cùng request, latency p95 và lỗi theo revision của InferenceService `cancel-risk` (A/B canary); dashboard đã được nạp thử trong Grafana 12.2. Cột `gold.booking_risk.model_version` (do `serving/predictor.py` trả, risk-api chuyển tiếp) cho phép so calibration và Brier của từng revision. [Cần làm] thêm panel theo version vào dashboard; chụp dashboard.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._
