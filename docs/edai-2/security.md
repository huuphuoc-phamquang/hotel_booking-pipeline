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

## Bổ sung final-coursework

<a id="final-54"></a>
### Centralize secret management via Hashi Corp Vault so it will be used across the whole… · final · Security

**Rubric:** final · dòng 54 · 1 điểm · nhóm *Security* › *Centralize secret management*

> Centralize secret management via Hashi Corp Vault (or similar tools) so it will be used across the whole organization.

**Cần nộp (cả nhóm):** Capture màn hình thể hiện cách mọi người thực hiện centrailize secret management

**Cách làm:** [Đã có] Jenkins lấy secret từ Vault; chart `helm/api` có Vault Agent Injector (giá trị `vault.role` và `path`: sidecar xuất secret thành biến môi trường) cho risk-api và booking-mcp. [Cần làm] chụp pod có sidecar `vault-agent`.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="final-55"></a>
### Using service mesh to authorize access from service to service

**Rubric:** final · dòng 55 · 1 điểm · nhóm *Security* › *Service to service authentication*

**Cần nộp (cả nhóm):** Capture màn hình thể hiện cách mọi người thực hiện authorize service-to-service

**Cách làm:** [Đã có] `k8s/istio-authz.yaml` bật PeerAuthentication mTLS STRICT. AuthorizationPolicy chỉ cho ServiceAccount của risk-api gọi InferenceService `cancel-risk`, và chỉ namespace `knative-eventing` gọi drift-api; mỗi API có ServiceAccount riêng trong `helm/api`. [Cần làm] chụp phản hồi 403 khi gọi từ pod khác.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._
