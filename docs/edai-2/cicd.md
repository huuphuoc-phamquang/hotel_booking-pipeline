# CI/CD

Jenkins: test + build + auto-deploy. CI/CD cho DP1–DP3 ở [edai-1/cicd.md](../edai-1/cicd.md).

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-2-33"></a>
## RAG Data Pipeline

**Rubric:** edai-2 · dòng 33 · 2 điểm · nhóm *CI/CD* › *CI/CD cho data pipelines ở trên (chỉ cần demo RAG Data Pipeline là được vì mấy cái khác tương tự)*

**Cần nộp (cả nhóm):** Document show các CICD pipelines đã chạy và từng step trong component làm gì + link tới các Jenkinsfile tương ứng

**Cách làm:** [Thiết kế] Jenkinsfile RAG: test chunk/validate -> build image (secret từ Vault) -> deploy DAG lên Airflow. [Cần làm] chụp run + giải thích từng stage.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-34"></a>
## Agent kéo dữ liệu

**Rubric:** edai-2 · dòng 34 · 2 điểm · nhóm *CI/CD* › *CI/CD cho các MCP Servers & Agents ở trên (Build & package xong MCP Servers => Deploy Agent with the corresponding MCP Servers) (Agent cần sử dụng System Prompt từ một Prompt Management tool như Langfuse)*

**Cách làm:** [Đã có] Jenkinsfile test -> build (Vault) -> helm -> ci/render_agents.py (prompt Langfuse) -> deploy agents; ci/pod-template.yaml + ci/tools.Dockerfile. [Cần làm] chụp run.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-35"></a>
## Agent để làm coordinator

**Rubric:** edai-2 · dòng 35 · 2 điểm · nhóm *CI/CD* › *CI/CD cho các MCP Servers & Agents ở trên (Build & package xong MCP Servers => Deploy Agent with the corresponding MCP Servers) (Agent cần sử dụng System Prompt từ một Prompt Management tool như Langfuse)*

**Cách làm:** [Thiết kế] stage deploy coordinator-agent (prompt từ Langfuse) -> rollout status -> publish lên registry. [Cần làm] chụp run.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-36"></a>
## CI/CD cho stream feature jobs

**Rubric:** edai-2 · dòng 36 · 2 điểm · nhóm *CI/CD*

**Cách làm:** [Thiết kế] Jenkinsfile build image Flink job -> apply FlinkDeployment (offline); Job 2 online là DAG feast_materialize_realtime, deploy cùng pipeline DAG. [Cần làm] chụp run.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

## Bổ sung final-coursework

<a id="final-28"></a>
### Materialize Pipeline

**Rubric:** final · dòng 28 · 2 điểm · nhóm *CI/CD* › *CI/CD cho pipelines*

**Cần nộp (cả nhóm):** Capture màn hình từng CI/CD pipeline đã run thành công

**Cách làm:** [Thiết kế] Jenkinsfile: test import DAG -> sync DAG materialize lên Airflow; secret từ Jenkins Credentials + Vault. [Cần làm] chụp run.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-29"></a>
### Training Pipeline

**Rubric:** final · dòng 29 · 2 điểm · nhóm *CI/CD* › *CI/CD cho pipelines*

**Cách làm:** [Thiết kế] Jenkinsfile: test component -> build image train -> compile KFP -> upload + tạo run qua KFP API. [Cần làm] chụp run.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-33"></a>
### Web API

**Rubric:** final · dòng 33 · 2 điểm · nhóm *CI/CD* › *CI/CD cho API (CI/CD cần kéo model ở trạng thái production hoặc được gắn tag production từ model registry về, đóng gói và deploy)*

> Web API (với FastAPI)

**Cần nộp (cả nhóm):** Capture màn hình từng CI/CD pipeline đã run thành công

**Cách làm:** [Đã có] ci/Jenkinsfile: test -> build image risk-api (docker/api.Dockerfile, Artifact Registry) -> helm --atomic. risk-api không chứa model; model production nằm trong image KServe. [Cần làm] chụp run.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-34"></a>
### Inference Engine

**Rubric:** final · dòng 34 · 1 điểm · nhóm *CI/CD* › *CI/CD cho API (CI/CD cần kéo model ở trạng thái production hoặc được gắn tag production từ model registry về, đóng gói và deploy)*

> Inference Engine (ví dụ KServe)

**Cách làm:** [Đã có] serving/kserve-cancel-risk.yaml. [Thiết kế] stage kéo model alias production của cancel-risk từ MLflow, build image (model-inside-image) rồi apply InferenceService.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-35"></a>
### Cho real-time drift detection Web API

**Rubric:** final · dòng 35 · 1 điểm · nhóm *CI/CD* › *CI/CD cho API (CI/CD cần kéo model ở trạng thái production hoặc được gắn tag production từ model registry về, đóng gói và deploy)*

> Cho real-time drift detection Web API (sử dụng KNative Eventing kết hợp với KServe)

**Cách làm:** [Đã có] ci/Jenkinsfile: tải reference_lead_days.npy của model production từ MLflow -> build image drift-api -> helm --atomic (MODEL_VERSION theo model); k8s/drift-eventing.yaml (Broker + Trigger). [Cần làm] chụp run.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-36"></a>
### Job 1: Push stream feature to OFFLINE store

**Rubric:** final · dòng 36 · 1 điểm · nhóm *CI/CD* › *CI/CD cho jobs*

**Cách làm:** [Thiết kế] Jenkinsfile Job 1: build image Flink -> apply FlinkDeployment.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-37"></a>
### Job 2: Push stream feature to ONLINE store

**Rubric:** final · dòng 37 · 1 điểm · nhóm *CI/CD* › *CI/CD cho jobs*

**Cách làm:** [Thiết kế] Job 2 là DAG feast_materialize_realtime: Jenkinsfile test import DAG -> sync DAG lên Airflow (cùng pipeline materialize). [Cần làm] chụp run.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
