# MCP server & agent dùng tool

booking-mcp viết bằng FastAPI, xử lý bất đồng bộ, deploy bằng Helm; agent gọi MCP tool, chạy trong sandbox
và được đăng ký trên registry.

Mỗi mục dưới đây ứng với một dòng của rubric. Phần **Cách làm** mô tả giải pháp đã triển khai, đồng bộ từ
cột F của rubric. Phần **Kết quả** ghi test đã chạy, số liệu đo được hoặc ảnh chụp (`docs/images/`).

<a id="edai-2-16"></a>
## Có sử dụng FastAPI + data validation + healthcheck for k8s

**Rubric:** edai-2 · dòng 16 · 1 điểm · nhóm *Web API kéo dữ liệu user (đã lưu thông qua feature pipeline) và chunk (đã được lưu thông qua RAG pipeline)* › *Có sử dụng FastAPI + data validation (với pydantic)*

> Có sử dụng FastAPI + data validation (với pydantic) + healthcheck for k8s

**Cần nộp (cả nhóm):** Document phải show được Agent đã có trên registry, được deploy với multi-replica, giới hạn quyền thông qua Sandbox và màn hình UI chat với Agent + link tới YAML file deploy Agent

**Cách làm:** [Đã có] Model pydantic `BookingFeatures`, `CancelRisk` ở MCP và `RiskRequest`, `CancelRisk` ở risk-api; có `/healthz`, `/readyz`.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-2-17"></a>
## Sử dụng async cho concurrent processing

**Rubric:** edai-2 · dòng 17 · 1 điểm · nhóm *Web API kéo dữ liệu user (đã lưu thông qua feature pipeline) và chunk (đã được lưu thông qua RAG pipeline)* › *Có sử dụng FastAPI + data validation (với pydantic)*

**Cách làm:** [Đã có] Tool viết bằng `async def`, đọc Feast online bất đồng bộ, gọi HTTP bằng `httpx.AsyncClient`.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-2-18"></a>
## Deploy in the form of MCP tool to k8s with helm + rollingupdate + auto fallback

**Rubric:** edai-2 · dòng 18 · 2 điểm · nhóm *Web API kéo dữ liệu user (đã lưu thông qua feature pipeline) và chunk (đã được lưu thông qua RAG pipeline)* › *Có sử dụng FastAPI + data validation (với pydantic)*

> Deploy in the form of MCP tool to k8s with helm + rollingupdate + auto fallback (see here) Remember, your MCP tool is not like normal API deployment, check it our how to deploy here.

**Cách làm:** [Đã có] Chart chung `helm/api` (`values-booking-mcp.yaml`) dùng RollingUpdate `maxUnavailable: 0`, kết hợp `--atomic` trong Jenkins. [Cần làm] chụp `helm history` khi rollback tự động.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-2-19"></a>
## Deploy 1 Agent sử dụng MCP tool ở trên với multi-replica và auto-scale sử dụng cái này

**Rubric:** edai-2 · dòng 19 · 2 điểm · nhóm *Web API kéo dữ liệu user (đã lưu thông qua feature pipeline) và chunk (đã được lưu thông qua RAG pipeline)* › *Có sử dụng FastAPI + data validation (với pydantic)*

**Cách làm:** [Đã có] `k8s/keda.yaml` có ScaledObject cho data-agent theo request/s của route `a2a-data-agent` qua agentgateway, tối thiểu 2 replica; HPA theo CPU đã bỏ khỏi `agents.yaml`. [Cần làm] chụp quá trình scale khi chạy locust.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-2-20"></a>
## Configure Agent chạy trong Sandbox để đảm bảo security

**Rubric:** edai-2 · dòng 20 · 1 điểm · nhóm *Web API kéo dữ liệu user (đã lưu thông qua feature pipeline) và chunk (đã được lưu thông qua RAG pipeline)* › *Có sử dụng FastAPI + data validation (với pydantic)*

**Cách làm:** [Thiết kế] `k8s/agent-substrate.yaml`: WorkerPool gVisor, SandboxAgent runtime go cho data-agent và NetworkPolicy chỉ cho agent gọi agentgateway và DNS. Các field của Substrate cần kiểm bằng `kubectl explain` với bản đã cài. [Cần làm] chụp agent chạy trong sandbox.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-2-21"></a>
## Publish Agent ở trên lên registry đã deploy để đảm bảo governance

**Rubric:** edai-2 · dòng 21 · 1 điểm · nhóm *Web API kéo dữ liệu user (đã lưu thông qua feature pipeline) và chunk (đã được lưu thông qua RAG pipeline)* › *Có sử dụng FastAPI + data validation (với pydantic)*

**Cách làm:** [Đã có] `ci/publish_agent_card.py`, Jenkins gọi sau khi rollout từng agent. [Cần làm] publish data-agent, chụp registry UI.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._
