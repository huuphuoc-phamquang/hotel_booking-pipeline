# Security

Quản lý secret tập trung bằng HashiCorp Vault.

<a id="edai-2-54"></a>
## Quản lý secret tập trung với HashiCorp Vault

Vault 1.20.1 cài bằng Helm trên GKE (`edai2/k8s/vault-values.yaml`): 1 server standalone lưu file
trên PVC, kèm Vault Agent Injector. `edai2/k8s/vault-setup.sh` init và unseal lần đầu (khoá lưu ngoài repo), bật KV v2
tại `secret/`, bật xác thực Kubernetes, tạo policy `booking-mcp` chỉ có quyền `read` trên đúng path
`secret/data/agents/booking-mcp`, và role `booking-mcp` gắn với ServiceAccount `booking-mcp` của namespace `agents`.

Secret của booking-mcp (DSN warehouse, thông tin kết nối Feast, endpoint OTLP) chuyển từ Kubernetes Secret sang Vault.
Chart `helm/api` bật `vault.role`, nên Injector bơm init container `vault-agent-init` và sidecar `vault-agent` vào pod;
secret được ghi ra `/vault/secrets/env` và nạp lúc container khởi động. Sau khi chuyển, Kubernetes Secret
`booking-mcp-env` đã bị xoá: pod vẫn Ready, và 12/12 lời gọi thử (MCP tool và REST) thành công, tức booking-mcp chỉ còn
lấy secret từ Vault.

Phạm vi hiện mới là booking-mcp. Các service khác (MLflow, Job train, Postgres) vẫn dùng Kubernetes Secret; Jenkins lấy
secret qua `withVault` và token gateway đồng bộ bằng ExternalSecret chưa dựng. Bản standalone
một key share chưa có HA hay auto-unseal (cần Raft + GCP KMS khi dùng thật).

![Vault: pod và trạng thái unseal](../images/edai-2/vault-cli-1.png)

![Vault: metadata của secret/agents/booking-mcp (không in giá trị)](../images/edai-2/vault-cli-2.png)

![Vault: policy chỉ đọc và role Kubernetes của booking-mcp](../images/edai-2/vault-cli-3.png)

![booking-mcp có vault-agent, Kubernetes Secret cũ không còn](../images/edai-2/vault-cli-4.png)

![Vault UI: secret/agents/booking-mcp](../images/edai-2/vault-ui.png)

## Service-to-service mTLS & AuthorizationPolicy (Istio)

Namespace `ml` bật `istio-injection=enabled`, áp dụng [`edai2/k8s/istio-authz.yaml`](../../edai2/k8s/istio-authz.yaml) (`PeerAuthentication` chế độ `STRICT` và `AuthorizationPolicy` chỉ cho `knative-eventing` gọi `drift-api`, chỉ `agents/sa/booking-mcp` gọi `cancel-risk`). Khi gọi thử từ pod không được cấp quyền trong `ml`, Envoy trả **`HTTP/1.1 403 Forbidden`** (`RBAC: access denied`):

![Istio AuthorizationPolicy trả 403 RBAC: access denied](../images/edai-2/istio-authz-403.png)
