# Coordinator agent

Coordinator điều phối các agent con; tài liệu gồm số replica, autoscale và registry.

Mỗi mục dưới đây ứng với một dòng của rubric. Phần **Cách làm** mô tả giải pháp đã triển khai, đồng bộ từ
cột F của rubric. Phần **Kết quả** ghi test đã chạy, số liệu đo được hoặc ảnh chụp (`docs/images/`).

<a id="edai-2-25"></a>
## Deploy 1 Coordinator Agent với multi-replica và auto-scale sử dụng cái này

**Rubric:** edai-2 · dòng 25 · 2 điểm · nhóm *Deploy 1 Coordinator Agent* › *Điều phối 2 Agent ở trên*

**Cần nộp (cả nhóm):** + Document phải show được Agent đã có trên registry, được deploy với multi-replica, có khả năng scale (có hình ảnh thể hiện đã test thử) + Document show KAgent UI chat với Agent

**Cách làm:** [Đã có] Coordinator scale bằng KEDA ScaledObject theo request/s qua agentgateway, cộng trigger CPU 60% (`k8s/keda.yaml`); HPA trong `agents.yaml` đã bị xoá. [Cần làm] kiểm xem kagent có ghi đè số replica không; chụp quá trình scale.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-2-26"></a>
## Publish Agent ở này lên registry đã deploy để đảm bảo governance.

**Rubric:** edai-2 · dòng 26 · 2 điểm · nhóm *Deploy 1 Coordinator Agent* › *Điều phối 2 Agent ở trên*

**Cách làm:** [Đã có] `ci/Jenkinsfile` đăng data-agent, policy-agent, policy-agent-v2 và coordinator-agent lên registry sau khi rollout. [Cần làm] chụp registry.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._
