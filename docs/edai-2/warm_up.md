# Warm-up (Agent Substrate)

Giữ sẵn worker cho agent để giảm chi phí và độ trễ khởi động.

Mỗi mục dưới đây ứng với một dòng của rubric. Phần **Cách làm** mô tả giải pháp đã triển khai, đồng bộ từ
cột F của rubric. Phần **Kết quả** ghi test đã chạy, số liệu đo được hoặc ảnh chụp (`docs/images/`).

<a id="edai-2-27"></a>
## Cài đặt hệ thống ở chế độ Warm Up cho agent theo hướng dẫn sau để tối ưu chi phí, đồng…

**Rubric:** edai-2 · dòng 27 · 2 điểm · nhóm *Cài đặt hệ thống ở chế độ Warm Up cho agent theo hướng dẫn sau để tối ưu chi phí, đồng thời giảm thiểu thời gian startup. Cái này cũng chính là Agent Fleet Architecture!*

**Cần nộp (cả nhóm):** + Document link tới code setup Substrate + hình ảnh thể hiện hệ thống có khả năng handle nhiều agent với số worker ít ỏi

**Cách làm:** [Thiết kế] `k8s/agent-substrate.yaml`: WorkerPool giữ 2 worker warm, chụp snapshot actor khi rảnh; khi cần, HPA scale qua scale subresource của WorkerPool. [Cần làm] chụp nhiều agent chạy trên ít worker.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._
