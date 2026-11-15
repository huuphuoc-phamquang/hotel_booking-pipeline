# Coordinator agent

Điều phối agent con; replica, autoscale, registry.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-2-25"></a>
## Deploy 1 Coordinator Agent với multi-replica và auto-scale sử dụng cái này

**Rubric:** edai-2 · dòng 25 · 2 điểm · nhóm *Deploy 1 Coordinator Agent* › *Điều phối 2 Agent ở trên*

**Cần nộp (cả nhóm):** + Document phải show được Agent đã có trên registry, được deploy với multi-replica, có khả năng scale (có hình ảnh thể hiện đã test thử) + Document show KAgent UI chat với Agent

**Cách làm:** [Đã có] coordinator: KEDA ScaledObject theo request/s qua agentgateway + trigger cpu 60% (k8s/keda.yaml), đã xoá HPA trong agents.yaml. [Cần làm] kiểm kagent có ghi đè replicas không; chụp scale.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-26"></a>
## Publish Agent ở này lên registry đã deploy để đảm bảo governance.

**Rubric:** edai-2 · dòng 26 · 2 điểm · nhóm *Deploy 1 Coordinator Agent* › *Điều phối 2 Agent ở trên*

**Cách làm:** [Đã có] ci/Jenkinsfile publish data-agent, policy-agent, policy-agent-v2, coordinator-agent lên registry sau rollout. [Cần làm] chụp registry.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
