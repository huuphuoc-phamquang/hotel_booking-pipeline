# Warm-up (Agent Substrate)

Giữ sẵn worker cho agent để giảm chi phí và độ trễ.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-2-27"></a>
## Cài đặt hệ thống ở chế độ Warm Up cho agent theo hướng dẫn sau để tối ưu chi phí, đồng…

**Rubric:** edai-2 · dòng 27 · 2 điểm · nhóm *Cài đặt hệ thống ở chế độ Warm Up cho agent theo hướng dẫn sau để tối ưu chi phí, đồng thời giảm thiểu thời gian startup. Cái này cũng chính là Agent Fleet Architecture!*

**Cần nộp (cả nhóm):** + Document link tới code setup Substrate + hình ảnh thể hiện hệ thống có khả năng handle nhiều agent với số worker ít ỏi

**Cách làm:** [Thiết kế] k8s/agent-substrate.yaml: WorkerPool giữ 2 worker warm, actor snapshot khi rảnh; HPA trên scale subresource của WorkerPool khi cần. [Cần làm] chụp nhiều agent chạy trên ít worker.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
