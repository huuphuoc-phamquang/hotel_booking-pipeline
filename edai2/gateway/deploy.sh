#!/usr/bin/env bash
# Dựng Keycloak + agentgateway rồi cấp JWT cho kagent. Chạy từ thư mục edai2, kubectl trỏ cluster GKE:
#   LLM_URL=https://<tunnel>.trycloudflare.com VLLM_KEY=<khoá vLLM> gateway/deploy.sh
# Chạy lại khi tunnel đổi URL hoặc khi token sắp hết hạn (30 ngày): client secret giữ nguyên, token cấp mới.
set -euo pipefail
: "${LLM_URL:?thiếu LLM_URL}" "${VLLM_KEY:?thiếu VLLM_KEY}"
CLIENTS="kagent data-agent policy-agent coordinator-agent"

kubectl apply -f k8s/keycloak.yaml -f k8s/agentgateway.yaml --dry-run=client -o name >/dev/null   # kiểm cú pháp trước
kubectl create namespace auth --dry-run=client -o yaml | kubectl apply -f -
if ! kubectl -n auth get secret keycloak-clients >/dev/null 2>&1; then
  args=(--from-literal=KC_BOOTSTRAP_ADMIN_PASSWORD="$(openssl rand -hex 16)")
  for c in $CLIENTS; do
    v=$(echo "$c" | tr a-z- A-Z_)_SECRET
    args+=(--from-literal="$v=$(openssl rand -hex 24)")
  done
  kubectl -n auth create secret generic keycloak-clients "${args[@]}"
fi
kubectl apply -f k8s/keycloak.yaml
kubectl -n auth rollout status deploy/keycloak --timeout=300s

kubectl apply -f k8s/agentgateway.yaml
kubectl -n gateway create secret generic vllm-key --from-literal=key="$VLLM_KEY" --dry-run=client -o yaml | kubectl apply -f -
host=${LLM_URL#https://}; host=${host%%/*}
kubectl -n gateway create configmap agentgateway-config \
  --from-literal=config.yaml="$(sed "s/LLM_HOST/$host/g" gateway/agentgateway.yaml)" --dry-run=client -o yaml | kubectl apply -f -
kubectl -n gateway rollout restart deploy/agentgateway
kubectl -n gateway rollout status deploy/agentgateway --timeout=180s

# Cấp token qua port-forward; issuer vẫn là tên service nhờ KC_HOSTNAME
kubectl -n auth port-forward svc/keycloak 18080:8080 >/dev/null 2>&1 & pf=$!
trap 'kill $pf' EXIT
sleep 3
token() {
  local v; v=$(echo "$1" | tr a-z- A-Z_)_SECRET
  local secret; secret=$(kubectl -n auth get secret keycloak-clients -o jsonpath="{.data.$v}" | base64 -d)
  curl -sf -d grant_type=client_credentials -d client_id="$1" -d client_secret="$secret" \
    http://localhost:18080/realms/agents/protocol/openid-connect/token | python -c "import json,sys;print(json.load(sys.stdin)['access_token'])"
}
apply_secret() { kubectl -n kagent create secret generic "$1" --from-literal="$2=$3" --dry-run=client -o yaml | kubectl apply -f -; }
apply_secret llm-api api_key "$(token kagent)"                        # ModelConfig: Bearer <JWT> tới /v1 của gateway
apply_secret mcp-token-data Authorization "Bearer $(token data-agent)"
apply_secret mcp-token-policy Authorization "Bearer $(token policy-agent)"
echo "xong: gateway http://agentgateway.gateway.svc.cluster.local:3000 -> $host"
