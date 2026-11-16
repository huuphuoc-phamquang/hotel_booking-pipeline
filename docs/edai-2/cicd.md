# CI/CD

Jenkins chạy test, build image và tự deploy. CI/CD cho DP1–DP3 nằm ở [edai-1/cicd.md](../edai-1/cicd.md).

Mỗi mục dưới đây ứng với một dòng của rubric. Phần **Cách làm** mô tả giải pháp đã triển khai, đồng bộ từ
cột F của rubric. Phần **Kết quả** ghi test đã chạy, số liệu đo được hoặc ảnh chụp (`docs/images/`).

<a id="edai-2-33"></a>
## RAG Data Pipeline

**Rubric:** edai-2 · dòng 33 · 2 điểm · nhóm *CI/CD* › *CI/CD cho data pipelines ở trên (chỉ cần demo RAG Data Pipeline là được vì mấy cái khác tương tự)*

**Cần nộp (cả nhóm):** Document show các CICD pipelines đã chạy và từng step trong component làm gì + link tới các Jenkinsfile tương ứng

**Cách làm:** [Đã có] `ci/Jenkinsfile.data` chạy DAG integrity test (có `rag_data_pipeline`) trong image Airflow, rồi deploy DAG qua git-sync và đợi Airflow parse không lỗi. [Cần làm] chụp lần chạy và giải thích từng stage.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-2-34"></a>
## Agent kéo dữ liệu

**Rubric:** edai-2 · dòng 34 · 2 điểm · nhóm *CI/CD* › *CI/CD cho các MCP Servers & Agents ở trên (Build & package xong MCP Servers => Deploy Agent with the corresponding MCP Servers) (Agent cần sử dụng System Prompt từ một Prompt Management tool như Langfuse)*

**Cách làm:** [Đã có] Jenkinsfile gồm các bước test → build (secret từ Vault) → helm → `ci/render_agents.py` (lấy prompt từ Langfuse) → deploy agent; agent build chạy trên `ci/pod-template.yaml` và `ci/tools.Dockerfile`. [Cần làm] chụp lần chạy.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-2-35"></a>
## Agent để làm coordinator

**Rubric:** edai-2 · dòng 35 · 2 điểm · nhóm *CI/CD* › *CI/CD cho các MCP Servers & Agents ở trên (Build & package xong MCP Servers => Deploy Agent with the corresponding MCP Servers) (Agent cần sử dụng System Prompt từ một Prompt Management tool như Langfuse)*

**Cách làm:** [Đã có] `ci/Jenkinsfile`: `render_agents.py` lấy prompt từ Langfuse → apply agent → kiểm rollout status từng agent (có coordinator) → `publish_agent_card.py`. [Cần làm] chụp lần chạy.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-2-36"></a>
## CI/CD cho stream feature jobs

**Rubric:** edai-2 · dòng 36 · 2 điểm · nhóm *CI/CD*

**Cách làm:** [Đã có] `ci/Jenkinsfile.data` build image Flink, chạy e2e stream trên Docker (Kafka → Flink → Postgres), rồi apply FlinkDeployment (offline). Job 2 cho online là DAG `feast_materialize_realtime`, deploy cùng các DAG khác. [Cần làm] chụp lần chạy.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

## Bổ sung final-coursework

<a id="final-28"></a>
### Materialize Pipeline

**Rubric:** final · dòng 28 · 2 điểm · nhóm *CI/CD* › *CI/CD cho pipelines*

**Cần nộp (cả nhóm):** Capture màn hình từng CI/CD pipeline đã run thành công

**Cách làm:** [Đã có] `ci/Jenkinsfile.data` chạy DAG integrity test trong image Airflow, deploy DAG qua git-sync rồi đợi Airflow parse không lỗi (`list-import-errors` rỗng); 2 DAG materialize đi cùng pipeline này. [Cần làm] chụp lần chạy.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="final-29"></a>
### Training Pipeline

**Rubric:** final · dòng 29 · 2 điểm · nhóm *CI/CD* › *CI/CD cho pipelines*

**Cách làm:** [Đã có] `ci/Jenkinsfile.ml` test component (data versioning, train phân tán), build image train-base (`ml/Dockerfile`), rồi dùng `ci/kfp_run.py` để compile, upload version và tạo run qua KFP API. [Cần làm] chụp lần chạy.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="final-33"></a>
### Web API

**Rubric:** final · dòng 33 · 2 điểm · nhóm *CI/CD* › *CI/CD cho API (CI/CD cần kéo model ở trạng thái production hoặc được gắn tag production từ model registry về, đóng gói và deploy)*

> Web API (với FastAPI)

**Cần nộp (cả nhóm):** Capture màn hình từng CI/CD pipeline đã run thành công

**Cách làm:** [Đã có] `ci/Jenkinsfile` test, build image risk-api (`docker/api.Dockerfile`, đẩy lên Artifact Registry) rồi chạy `helm --atomic`. risk-api không chứa model; model production nằm trong image KServe. [Cần làm] chụp lần chạy.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="final-34"></a>
### Inference Engine

**Rubric:** final · dòng 34 · 1 điểm · nhóm *CI/CD* › *CI/CD cho API (CI/CD cần kéo model ở trạng thái production hoặc được gắn tag production từ model registry về, đóng gói và deploy)*

> Inference Engine (ví dụ KServe)

**Cách làm:** [Đã có] `serving/Dockerfile` dựa trên image sklearnserver, thêm xgboost 3.2.0, model ở `/mnt/models` và entrypoint `serving/predictor.py` trả xác suất kèm `model_version` (build arg `MODEL_VERSION`). `ci/fetch_model.py` kéo alias `production` từ MLflow; `ci/Jenkinsfile.ml` build image với tag là version MLflow. Đã build và gọi `:predict` cục bộ: response gồm `[[P(không huỷ), P(huỷ)]]` và `model_version`, đúng dạng risk-api đọc. [Cần làm] chụp bước apply trên cluster.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="final-35"></a>
### Cho real-time drift detection Web API

**Rubric:** final · dòng 35 · 1 điểm · nhóm *CI/CD* › *CI/CD cho API (CI/CD cần kéo model ở trạng thái production hoặc được gắn tag production từ model registry về, đóng gói và deploy)*

> Cho real-time drift detection Web API (sử dụng KNative Eventing kết hợp với KServe)

**Cách làm:** [Đã có] `ci/Jenkinsfile` tải `reference_lead_days.npy` của model production từ MLflow, build image drift-api rồi chạy `helm --atomic` (`MODEL_VERSION` theo model); `k8s/drift-eventing.yaml` tạo Broker và Trigger. [Cần làm] chụp lần chạy.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="final-36"></a>
### Job 1: Push stream feature to OFFLINE store

**Rubric:** final · dòng 36 · 1 điểm · nhóm *CI/CD* › *CI/CD cho jobs*

**Cách làm:** [Đã có] `ci/Jenkinsfile.data` build image Flink (`k8s/flink.Dockerfile`), chạy e2e stream trên Docker, rồi apply FlinkDeployment và đợi trạng thái STABLE. [Cần làm] chụp lần chạy.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="final-37"></a>
### Job 2: Push stream feature to ONLINE store

**Rubric:** final · dòng 37 · 1 điểm · nhóm *CI/CD* › *CI/CD cho jobs*

**Cách làm:** [Đã có] Job 2 là DAG `feast_materialize_realtime`: `ci/Jenkinsfile.data` chạy DAG integrity test trong image Airflow, đẩy qua git-sync, đợi commit xuất hiện và kiểm không có import error (cùng pipeline materialize). [Cần làm] chụp lần chạy.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._
