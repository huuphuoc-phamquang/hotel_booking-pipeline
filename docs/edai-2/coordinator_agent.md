# Coordinator agent

Điều phối agent con; replica, autoscale, registry.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-2-25"></a>
## Deploy 1 Coordinator Agent với multi-replica và auto-scale sử dụng cái này

**Rubric:** edai-2 · dòng 25 · 2 điểm · nhóm *Deploy 1 Coordinator Agent* › *Điều phối 2 Agent ở trên*

**Cần nộp (cả nhóm):** + Document phải show được Agent đã có trên registry, được deploy với multi-replica, có khả năng scale (có hình ảnh thể hiện đã test thử) + Document show KAgent UI chat với Agent

**Cách làm:** [Đã có] coordinator 2 replica + HPA 2-6 theo CPU 60%. [Cần sửa] HPA là trạng thái mẫu; đổi sang KEDA ScaledObject theo request/s như agent con và xoá HPA (KEDA tự tạo HPA, không để 2 HPA cùng target); cần kiểm kagent có ghi đè replicas không. [Cần làm] chụp scale khi load test + kagent UI chat.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-26"></a>
## Publish Agent ở này lên registry đã deploy để đảm bảo governance.

**Rubric:** edai-2 · dòng 26 · 2 điểm · nhóm *Deploy 1 Coordinator Agent* › *Điều phối 2 Agent ở trên*

**Cách làm:** [Cần làm] publish coordinator lên registry (Jenkins hiện chỉ publish data-agent).

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
