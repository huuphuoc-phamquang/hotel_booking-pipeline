# Security

Vault quản lý secret; Istio bảo vệ giao tiếp giữa các service.

Mỗi mục dưới đây ứng với một dòng của rubric. Phần **Cách làm** mô tả giải pháp đã triển khai, đồng bộ từ
cột F của rubric. Phần **Kết quả** ghi test đã chạy, số liệu đo được hoặc ảnh chụp (`docs/images/`).

<a id="edai-2-54"></a>
## Centralize secret management via Hashi Corp Vault so it will be used across the whole… · edai-2 · Security

**Rubric:** edai-2 · dòng 54 · 1 điểm · nhóm *Security* › *Centralize secret management*

> Centralize secret management via Hashi Corp Vault (or similar tools) so it will be used across the whole organization.

**Cần nộp (cả nhóm):** Document để prove HashiCorp đã được dùng

**Cách làm:** [Đã có] Jenkins lấy secret qua `withVault` (registry, Langfuse); token gateway đồng bộ bằng ExternalSecret. [Cần làm] chụp Vault UI và ExternalSecret ở trạng thái synced.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._
