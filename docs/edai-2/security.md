# Security

Vault cho secret, Istio cho service-to-service.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-2-54"></a>
## Centralize secret management via Hashi Corp Vault so it will be used across the whole… · edai-2 · Security

**Rubric:** edai-2 · dòng 54 · 1 điểm · nhóm *Security* › *Centralize secret management*

> Centralize secret management via Hashi Corp Vault (or similar tools) so it will be used across the whole organization.

**Cần nộp (cả nhóm):** Document để prove HashiCorp đã được dùng

**Cách làm:** [Đã có] withVault trong Jenkins (registry, Langfuse), token gateway qua ExternalSecret. [Cần làm] chụp Vault UI + ExternalSecret synced.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

## Bổ sung final-coursework

<a id="final-54"></a>
### Centralize secret management via Hashi Corp Vault so it will be used across the whole… · final · Security

**Rubric:** final · dòng 54 · 1 điểm · nhóm *Security* › *Centralize secret management*

> Centralize secret management via Hashi Corp Vault (or similar tools) so it will be used across the whole organization.

**Cần nộp (cả nhóm):** Capture màn hình thể hiện cách mọi người thực hiện centrailize secret management

**Cách làm:** [Đã có] Jenkins lấy secret từ Vault; helm/api có Vault Agent Injector (values vault.role + path: sidecar export secret thành biến môi trường) cho risk-api và booking-mcp. [Cần làm] chụp pod có sidecar vault-agent.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-55"></a>
### Using service mesh to authorize access from service to service

**Rubric:** final · dòng 55 · 1 điểm · nhóm *Security* › *Service to service authentication*

**Cần nộp (cả nhóm):** Capture màn hình thể hiện cách mọi người thực hiện authorize service-to-service

**Cách làm:** [Đã có] k8s/istio-authz.yaml: PeerAuthentication STRICT mTLS; AuthorizationPolicy chỉ cho SA risk-api gọi InferenceService cancel-risk, chỉ namespace knative-eventing gọi drift-api (mỗi API có ServiceAccount riêng trong helm/api). [Cần làm] chụp 403 từ pod khác.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
