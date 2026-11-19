# Coordinator agent

Coordinator điều phối các agent con; tài liệu gồm số replica, autoscale và registry.

Mỗi mục dưới đây ứng với một dòng của rubric. Phần **Cách làm** mô tả giải pháp đã triển khai, đồng bộ từ
cột F của rubric. Phần **Kết quả** ghi test đã chạy, số liệu đo được hoặc ảnh chụp (`docs/images/`).

<a id="edai-2-25"></a>
## Deploy 1 Coordinator Agent với multi-replica và auto-scale sử dụng cái này

**Rubric:** edai-2 · dòng 25 · 2 điểm · nhóm *Deploy 1 Coordinator Agent* › *Điều phối 2 Agent ở trên*

**Cần nộp (cả nhóm):** + Document phải show được Agent đã có trên registry, được deploy với multi-replica, có khả năng scale (có hình ảnh thể hiện đã test thử) + Document show KAgent UI chat với Agent

**Cách làm:** [Đã có] Coordinator scale bằng KEDA ScaledObject theo request/s qua agentgateway, cộng trigger CPU 60% (`k8s/keda.yaml`); HPA trong `agents.yaml` đã bị xoá. [Cần làm] kiểm xem kagent có ghi đè số replica không; chụp quá trình scale.

**Kết quả:** phần điều phối và chat trên kagent UI đã có; registry, multi-replica và auto-scale chưa làm.
coordinator-agent ([`agents/agents-gke.yaml`](../../edai2/agents/agents-gke.yaml)) có hai tool kiểu `Agent` là
data-agent và policy-agent, chạy 1 replica. Với câu hỏi gồm số liệu của khách 18766768 tại khách sạn 8528 và xác suất
huỷ của booking 90000919211, coordinator tách thành hai yêu cầu, giao cho từng agent con rồi tổng hợp: khách có
1 booking 90 ngày, tỉ lệ huỷ 0%, lead time trung bình 6 ngày; booking có xác suất huỷ 13,14% (model v1).

![kagent UI: coordinator-agent gọi data-agent và policy-agent](../images/edai-2/kagent-coordinator.png)

<a id="edai-2-26"></a>
## Publish Agent ở này lên registry đã deploy để đảm bảo governance.

**Rubric:** edai-2 · dòng 26 · 2 điểm · nhóm *Deploy 1 Coordinator Agent* › *Điều phối 2 Agent ở trên*

**Cách làm:** [Đã có] `ci/Jenkinsfile` đăng data-agent, policy-agent, policy-agent-v2 và coordinator-agent lên registry sau khi rollout. [Cần làm] chụp registry.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._
