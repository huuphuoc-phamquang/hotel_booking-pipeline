# MCP server & agent dùng tool

booking-mcp viết bằng FastAPI, xử lý bất đồng bộ, deploy bằng Helm; agent gọi MCP tool, chạy trong sandbox
và được đăng ký trên registry.

Mỗi mục ứng với một dòng của rubric. Mục đã hoàn thành ghi lại phần đã triển khai và kết quả (số liệu đo được,
ảnh chụp trong `docs/images/`). Mục chưa hoàn thành giữ trích rubric, phần **Cách làm** đồng bộ từ cột F của rubric
và phần **Kết quả** chờ bổ sung.

<a id="edai-2-16"></a>
## Có sử dụng FastAPI + data validation + healthcheck for k8s

booking-mcp viết bằng FastAPI; input và output của REST và MCP tool là model pydantic (`BookingFeatures`,
`RiskRequest`, `CancelRisk`, `BatchRisk`, `OverbookingProposal`). Tool `predict_cancellation` lấy feature theo
`booking_id` từ Feast online rồi gọi KServe `cancel-risk`; cùng logic mở REST `/v1/cancel-risk` và `/v1/cancel-risk/batch`.
`/healthz` là liveness probe; `/readyz` là readiness probe và chỉ trả 200 khi đọc được online store. booking-mcp chạy trên GKE ngày 2026-11-18 (namespace `agents`, chart `helm/api`, image `booking-mcp:e6e53e9-2`); các phép kiểm dưới đây chạy bằng `api_checks` trong chính pod, gọi qua tên service.

`/healthz` và `/readyz` đều trả 200, và Deployment dùng đúng hai đường dẫn này cho liveness và readiness probe. Request
sai schema bị pydantic chặn với mã 422 trước khi vào logic: `booking_id` âm ("Input should be greater than 0"), chuỗi
thay cho số ("Input should be a valid integer") và thiếu trường ("Field required").

![Healthcheck, validation và async của booking-mcp](../images/edai-2/booking-mcp-api-checks.png)

<a id="edai-2-17"></a>
## Sử dụng async cho concurrent processing

Mọi tool và endpoint là `async def`; Feast online được đọc bằng `get_online_features_async`, KServe được gọi bằng
`httpx.AsyncClient`, và warehouse dùng `psycopg.AsyncConnection`. Phép đo gọi 50 lần `get_booking_features` với các cặp
khách, khách sạn thật, một lần tuần tự và một lần đồng thời bằng `asyncio.gather` trên cùng một phiên MCP (cùng lần chạy
ở dòng 16).

50 lần gọi tuần tự mất 1,66 s, gọi đồng thời mất 1,19 s, tức nhanh hơn 1,4 lần và không lỗi lần nào. Mức tăng còn hạn
chế vì cả 50 lời gọi cùng đọc online store qua một pod và một kết nối PostgreSQL; ảnh ở dòng 16.

<a id="edai-2-18"></a>
## Deploy in the form of MCP tool to k8s with helm + rollingupdate + auto fallback

Chart chung `helm/api` (`values-booking-mcp.yaml`) dùng RollingUpdate với `maxSurge: 1`, `maxUnavailable: 0`, và
readiness probe `/readyz`: pod mới chỉ nhận traffic khi đọc được online store, pod cũ chỉ bị gỡ khi pod mới đã Ready.
Jenkins deploy bằng `helm upgrade --install --atomic --timeout 5m`, nên nếu pod mới không Ready kịp, Helm tự rollback về
revision trước. Phép thử chạy trên GKE ngày 2026-11-18: upgrade booking-mcp sang một image tag không tồn tại với
`--atomic --timeout 90s`.

Upgrade thất bại sau 90 giây vì pod mới không kéo được image, và Helm tự rollback: `helm history` ghi revision 3
`failed` và revision 4 "Rollback to 2". Trong suốt quá trình, pod cũ vẫn Running và phục vụ request nhờ
`maxUnavailable: 0`; sau rollback, Deployment trở lại image `booking-mcp:e6e53e9-2`.

![helm upgrade --atomic tự rollback](../images/edai-2/helm-atomic-rollback.png)

<a id="edai-2-19"></a>
## Deploy 1 Agent sử dụng MCP tool ở trên với multi-replica và auto-scale sử dụng cái này

**Rubric:** edai-2 · dòng 19 · 2 điểm · nhóm *Web API kéo dữ liệu user (đã lưu thông qua feature pipeline) và chunk (đã được lưu thông qua RAG pipeline)* › *Có sử dụng FastAPI + data validation (với pydantic)*

**Cách làm:** [Đã có] `k8s/keda.yaml` có ScaledObject cho data-agent theo request/s của route `a2a-data-agent` qua agentgateway, tối thiểu 2 replica; HPA theo CPU đã bỏ khỏi `agents.yaml`. [Cần làm] chụp quá trình scale khi chạy locust.

**Kết quả:** phần agent dùng MCP tool đã chạy; multi-replica và auto-scale chưa làm. data-agent
([`agents/agents-gke.yaml`](../../edai2/agents/agents-gke.yaml)) dùng RemoteMCPServer `booking-tools-data` (qua
agentgateway, token role `data-agent`) và chỉ được cấp tool `get_booking_features`; hiện chạy 1 replica, chưa có KEDA. Hỏi về cặp
khách 18766768 và khách sạn 8528, agent gọi tool với đúng hai mã rồi trả lời theo số liệu online store (44 booking
7 ngày, tỉ lệ huỷ 30 ngày 17,24%). Prompt yêu cầu hỏi lại khi thiếu mã; trong phạm vi thử nghiệm, model 3B vẫn có lúc
gọi tool với `customer_id` rỗng.

![kagent UI: data-agent gọi get_booking_features](../images/edai-2/kagent-data-agent.png)

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
