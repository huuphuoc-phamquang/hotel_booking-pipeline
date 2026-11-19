#!/usr/bin/env bash
# Thiết lập Vault sau khi cài chart (k8s/vault-values.yaml); chạy lại được (bỏ qua bước đã làm).
#   VAULT_INIT_FILE=<file ngoài repo> bash k8s/vault-setup.sh
# 1. init (1 key share) lần đầu, ghi unseal key + root token ra VAULT_INIT_FILE; unseal sau mỗi lần pod khởi động lại
# 2. KV v2 tại secret/; secret của booking-mcp chuyển từ Kubernetes Secret booking-mcp-env sang secret/agents/booking-mcp
# 3. auth kubernetes: pod dùng ServiceAccount booking-mcp (namespace agents) chỉ đọc được đúng path của nó
set -euo pipefail
export MSYS_NO_PATHCONV=1
INIT=${VAULT_INIT_FILE:?đặt VAULT_INIT_FILE tới file ngoài repo để giữ unseal key và root token}
json() { python -c "import json,sys; print(json.load(sys.stdin)$1)"; }
v() { kubectl -n vault exec -i vault-0 -- env VAULT_TOKEN="${ROOT:-}" vault "$@"; }

if [ "$(v status -format=json | json "['initialized']")" = False ]; then
  v operator init -key-shares=1 -key-threshold=1 -format=json > "$INIT"
  echo "đã init, khoá lưu ở $INIT"
fi
if [ "$(v status -format=json | json "['sealed']")" = True ]; then
  v operator unseal "$(json "['unseal_keys_b64'][0]" < "$INIT")" > /dev/null
fi
ROOT=$(json "['root_token']" < "$INIT")

v secrets list -format=json | grep -q '"secret/"' || v secrets enable -path=secret kv-v2
sec() { kubectl -n agents get secret booking-mcp-env -o jsonpath="{.data.$1}" | base64 -d; }
# chuyển 1 lần: sau khi xoá Secret booking-mcp-env, Vault là nơi duy nhất giữ các giá trị này
if kubectl -n agents get secret booking-mcp-env > /dev/null 2>&1; then
  v kv put secret/agents/booking-mcp \
    WAREHOUSE_DSN="$(sec WAREHOUSE_DSN)" FEAST_PG_HOST="$(sec FEAST_PG_HOST)" FEAST_PG_USER="$(sec FEAST_PG_USER)" \
    FEAST_PG_PASSWORD="$(sec FEAST_PG_PASSWORD)" OTEL_EXPORTER_OTLP_ENDPOINT="$(sec OTEL_EXPORTER_OTLP_ENDPOINT)" > /dev/null
fi

v auth list -format=json | grep -q '"kubernetes/"' || v auth enable kubernetes
v write auth/kubernetes/config kubernetes_host=https://kubernetes.default.svc > /dev/null
echo 'path "secret/data/agents/booking-mcp" { capabilities = ["read"] }' | v policy write booking-mcp - > /dev/null
v write auth/kubernetes/role/booking-mcp bound_service_account_names=booking-mcp \
  bound_service_account_namespaces=agents policies=booking-mcp ttl=1h > /dev/null
echo "Vault sẵn sàng: secret/agents/booking-mcp, role booking-mcp"
