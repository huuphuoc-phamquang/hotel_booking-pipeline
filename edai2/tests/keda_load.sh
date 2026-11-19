#!/usr/bin/env bash
# Tạo tải lên route A2A của 1 agent qua agentgateway để KEDA scale (k8s/keda.yaml, ngưỡng 1 req/s/replica) và in HPA mỗi 20 s.
# Tải là GET agent card ~10 req/s: đi qua gateway tới pod agent (được tính vào agentgateway_requests_total) nhưng không
# gọi LLM, nên không dồn GPU. Chạy từ thư mục edai2:  bash tests/keda_load.sh [agent] [giây]
set -euo pipefail
AGENT=${1:-data-agent}; DURATION=${2:-150}
KC=$((20000 + RANDOM % 5000)); GW=$((25000 + RANDOM % 5000))   # port ngẫu nhiên: tránh đụng port-forward đang chạy
kubectl -n auth port-forward svc/keycloak $KC:8080 >/dev/null 2>&1 & p1=$!
kubectl -n gateway port-forward svc/agentgateway $GW:3000 >/dev/null 2>&1 & p2=$!
trap 'kill $p1 $p2 2>/dev/null' EXIT
sleep 4
sec=$(kubectl -n auth get secret keycloak-clients -o jsonpath="{.data.COORDINATOR_AGENT_SECRET}" | base64 -d)
TOK=$(curl -sf -d grant_type=client_credentials -d client_id=coordinator-agent -d client_secret="$sec" \
  http://localhost:$KC/realms/agents/protocol/openid-connect/token | sed 's/.*"access_token":"\([^"]*\)".*/\1/')
URL="http://localhost:$GW/a2a/$AGENT/.well-known/agent-card.json"
code=$(curl -s -o /dev/null -w '%{http_code}' -H "Authorization: Bearer $TOK" "$URL")
[ "$code" = 200 ] || { echo "gateway trả $code cho $URL, dừng"; exit 1; }
args=(); for _ in $(seq 10); do args+=(-o /dev/null "$URL"); done
( end=$((SECONDS + DURATION)); while [ $SECONDS -lt "$end" ]; do curl -s --parallel -H "Authorization: Bearer $TOK" "${args[@]}"; sleep 1; done ) &
load=$!
for _ in $(seq $((DURATION / 20 + 3))); do
  sleep 20
  hpa=$(kubectl -n kagent get hpa "keda-hpa-$AGENT" -o jsonpath='{.status.currentMetrics[0].external.current.averageValue} {.status.desiredReplicas}')
  echo "$(date +%T)  req/s mỗi replica ${hpa% *} (ngưỡng 1)  desired ${hpa#* }  ready $(kubectl -n kagent get deploy "$AGENT" -o jsonpath='{.status.readyReplicas}/{.spec.replicas}')  nodes $(kubectl get nodes --no-headers | wc -l)"
done
wait $load
