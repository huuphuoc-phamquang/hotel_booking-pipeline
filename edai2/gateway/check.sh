#!/usr/bin/env bash
# Kiểm security & policy của agentgateway từ 1 pod curl trong cluster (chạy từ thư mục edai2): bash gateway/check.sh
# Token lấy từ Secret do gateway/deploy.sh tạo; token coordinator-agent cấp mới qua Keycloak trong pod.
set -euo pipefail
export MSYS_NO_PATHCONV=1
sec() { kubectl -n "$1" get secret "$2" -o jsonpath="{.data.$3}" | base64 -d; }
kubectl -n gateway run gw-check --rm -i --restart=Never --quiet --image=curlimages/curl:8.11.1 \
  --env=LLM_TOKEN="$(sec kagent llm-api api_key)" \
  --env=DATA_TOKEN="$(sec kagent mcp-token-data Authorization)" \
  --env=POLICY_TOKEN="$(sec kagent mcp-token-policy Authorization)" \
  --env=COORD_SECRET="$(sec auth keycloak-clients COORDINATOR_AGENT_SECRET)" --command -- sh <<'EOF'
G=http://agentgateway.gateway.svc.cluster.local:3000
code() { curl -s -o /dev/null -w '%{http_code}' "$@"; }
llm='{"model":"qwen-3b","max_tokens":5,"messages":[{"role":"user","content":"hi"}]}'
echo "== LLM /v1 (jwtAuth strict)"
echo "  không token       : $(code -H 'Content-Type: application/json' -d "$llm" $G/v1/chat/completions)"
echo "  token giả mạo     : $(code -H 'Authorization: Bearer abc.def.ghi' -H 'Content-Type: application/json' -d "$llm" $G/v1/chat/completions)"
echo "  token kagent      : $(code -H "Authorization: Bearer $LLM_TOKEN" -H 'Content-Type: application/json' -d "$llm" $G/v1/chat/completions)"
mcp() { h=$1; shift; curl -s -H "Authorization: $h" -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' "$@"; }
session() {
  sid=$(mcp "$1" -D - -o /dev/null -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"check","version":"1"}}}' $G/mcp | tr -d '\r' | awk -F': ' 'tolower($1)=="mcp-session-id"{print $2}')
  mcp "$1" -H "Mcp-Session-Id: $sid" -d '{"jsonrpc":"2.0","method":"notifications/initialized"}' $G/mcp >/dev/null
}
tools() { session "$1"; mcp "$1" -H "Mcp-Session-Id: $sid" -d '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' $G/mcp | grep -o '"name":"[a-z_]*"' | sort -u | cut -d'"' -f4 | tr '\n' ' '; }
echo "== MCP /mcp (mcpAuthorization theo claim role)"
echo "  không token        : $(code -H 'Content-Type: application/json' -d '{}' $G/mcp)"
echo "  tool của data-agent  : $(tools "$DATA_TOKEN")"
echo "  tool của policy-agent: $(tools "$POLICY_TOKEN")"
session "$DATA_TOKEN"
echo "  data-agent gọi predict_cancellation: $(mcp "$DATA_TOKEN" -H "Mcp-Session-Id: $sid" -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"predict_cancellation","arguments":{"booking_id":1}}}' $G/mcp)"
coord=$(curl -s -d grant_type=client_credentials -d client_id=coordinator-agent -d client_secret="$COORD_SECRET" \
  http://keycloak.auth.svc.cluster.local:8080/realms/agents/protocol/openid-connect/token | sed 's/.*"access_token":"\([^"]*\)".*/\1/')
echo "== A2A /a2a/<agent> (jwtAuth, token coordinator-agent)"
for a in data-agent policy-agent coordinator-agent; do
  echo "  $a agent card: không token $(code $G/a2a/$a/.well-known/agent.json), có token $(code -H "Authorization: Bearer $coord" $G/a2a/$a/.well-known/agent.json)"
done
EOF
