# MCP server & agent dùng tool

booking-mcp: FastAPI, async, helm; agent dùng MCP tool, sandbox, registry.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-2-16"></a>
## Có sử dụng FastAPI + data validation + healthcheck for k8s

**Rubric:** edai-2 · dòng 16 · 1 điểm · nhóm *Web API kéo dữ liệu user (đã lưu thông qua feature pipeline) và chunk (đã được lưu thông qua RAG pipeline)* › *Có sử dụng FastAPI + data validation (với pydantic)*

> Có sử dụng FastAPI + data validation (với pydantic) + healthcheck for k8s

**Cần nộp (cả nhóm):** Document phải show được Agent đã có trên registry, được deploy với multi-replica, giới hạn quyền thông qua Sandbox và màn hình UI chat với Agent + link tới YAML file deploy Agent

**Cách làm:** [Đã có] pydantic BookingFeatures / CancelRisk ở MCP, RiskRequest / CancelRisk ở risk-api; /healthz, /readyz.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-17"></a>
## Sử dụng async cho concurrent processing

**Rubric:** edai-2 · dòng 17 · 1 điểm · nhóm *Web API kéo dữ liệu user (đã lưu thông qua feature pipeline) và chunk (đã được lưu thông qua RAG pipeline)* › *Có sử dụng FastAPI + data validation (với pydantic)*

**Cách làm:** [Đã có] tool async def, Feast online async, httpx.AsyncClient.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-18"></a>
## Deploy in the form of MCP tool to k8s with helm + rollingupdate + auto fallback

**Rubric:** edai-2 · dòng 18 · 2 điểm · nhóm *Web API kéo dữ liệu user (đã lưu thông qua feature pipeline) và chunk (đã được lưu thông qua RAG pipeline)* › *Có sử dụng FastAPI + data validation (với pydantic)*

> Deploy in the form of MCP tool to k8s with helm + rollingupdate + auto fallback (see here) Remember, your MCP tool is not like normal API deployment, check it our how to deploy here.

**Cách làm:** [Đã có] chart chung helm/api (values-booking-mcp.yaml): RollingUpdate maxUnavailable 0 + Jenkins --atomic. [Cần làm] chụp helm history khi rollback tự động.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-19"></a>
## Deploy 1 Agent sử dụng MCP tool ở trên với multi-replica và auto-scale sử dụng cái này

**Rubric:** edai-2 · dòng 19 · 2 điểm · nhóm *Web API kéo dữ liệu user (đã lưu thông qua feature pipeline) và chunk (đã được lưu thông qua RAG pipeline)* › *Có sử dụng FastAPI + data validation (với pydantic)*

**Cách làm:** [Đã có] data-agent replicas 2. [Cần sửa] rubric dẫn KEDA: ScaledObject cho data-agent (Prometheus scaler theo request/s qua agentgateway, min 2). [Cần làm] chụp scale khi chạy locust.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-20"></a>
## Configure Agent chạy trong Sandbox để đảm bảo security

**Rubric:** edai-2 · dòng 20 · 1 điểm · nhóm *Web API kéo dữ liệu user (đã lưu thông qua feature pipeline) và chunk (đã được lưu thông qua RAG pipeline)* › *Có sử dụng FastAPI + data validation (với pydantic)*

**Cách làm:** [Thiết kế] Agent Substrate của kagent: agent chạy dạng SandboxAgent trong actor gVisor theo session (chart substrate >= 0.0.9, kagent >= 0.9.7, controller.substrate.enabled=true); thêm NetworkPolicy chỉ cho gọi agentgateway. Giới hạn: declarative runtime go. [Cần sửa] agents.yaml chưa khai runtime -> đặt runtime: go + substrate.workerPoolRef cho data-agent, policy-agent, coordinator. [Cần làm] chụp agent trên View -> Substrate.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-21"></a>
## Publish Agent ở trên lên registry đã deploy để đảm bảo governance

**Rubric:** edai-2 · dòng 21 · 1 điểm · nhóm *Web API kéo dữ liệu user (đã lưu thông qua feature pipeline) và chunk (đã được lưu thông qua RAG pipeline)* › *Có sử dụng FastAPI + data validation (với pydantic)*

**Cách làm:** [Đã có] ci/publish_agent_card.py (Jenkins gọi sau rollout từng agent). [Cần làm] publish data-agent, chụp registry UI.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
