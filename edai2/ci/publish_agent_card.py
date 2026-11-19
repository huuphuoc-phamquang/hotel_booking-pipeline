"""Đăng 1 agent kagent (kèm MCP server nó dùng) lên agentregistry v0.4.0 (aregistry.ai) để quản lý tập trung.
Agent card A2A lấy từ kagent controller (/api/a2a/kagent/<agent>/.well-known/agent-card.json): không lấy qua agentgateway
vì /a2a/policy-agent chia 50/50 v1/v2, card trả về có thể là của bản kia. Tag = commit đang deploy (TAG).
Registry nhận YAML resource ar.dev/v1alpha1 qua POST /v0/apply (idempotent: apply lại cùng tag thì cập nhật).
Dùng: python ci/publish_agent_card.py --agent data-agent --tools get_booking_features \
        --registry http://agentregistry.agentregistry.svc.cluster.local:12121 [--kagent ...] [--dry-run]
"""
import argparse
import json
import os
import urllib.request

import yaml

REPO = "https://github.com/huuphuoc-phamquang/hotel_booking-pipeline"


def http(url: str, data: bytes | None = None, headers: dict | None = None) -> dict:
    req = urllib.request.Request(url, data, headers or {}, method="POST" if data else "GET")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def resources(card: dict, a: argparse.Namespace) -> list[dict]:
    meta = lambda name: {"name": name, "tag": a.tag, "labels": {"app": "booking", "platform": "kagent"}}
    mcp = {"apiVersion": "ar.dev/v1alpha1", "kind": "MCPServer", "metadata": meta("booking-tools"),
           "spec": {"title": "booking-tools (booking-mcp qua agentgateway)",
                    "description": "Feature store online, dự đoán huỷ (KServe), RAG chính sách, đề xuất/ghi bán vượt",
                    "remote": {"type": "streamable-http", "url": f"{a.gateway}/mcp"}}}
    agent = {"apiVersion": "ar.dev/v1alpha1", "kind": "Agent",
             "metadata": {**meta(a.agent), "annotations": {
                 "a2a.url": f"{a.gateway}/a2a/{a.agent}/", "a2a.protocolVersion": str(card.get("protocolVersion", "")),
                 "mcp.tools": ",".join(a.tools), "kagent.namespace": "kagent"}},
             "spec": {"title": card.get("name", a.agent), "description": card.get("description", ""),
                      "modelProvider": "openai", "modelName": a.model,
                      "source": {"protocol": "A2A", "repository": {"url": REPO, "commit": a.tag, "subfolder": "edai2/agents"}}}}
    if a.tools:
        agent["spec"]["mcpServers"] = [{"kind": "MCPServer", "name": "booking-tools", "tag": a.tag}]
    return [mcp, agent] if a.tools else [agent]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", required=True)
    ap.add_argument("--registry", required=True)
    ap.add_argument("--kagent", default="http://kagent-controller.kagent.svc.cluster.local:8083",
                    help="kagent controller để lấy agent card (vd port-forward khi chạy ngoài cluster)")
    ap.add_argument("--gateway", default="http://agentgateway.gateway.svc.cluster.local:3000",
                    help="địa chỉ A2A / MCP ghi vào registry (người dùng gọi agent qua gateway)")
    ap.add_argument("--tools", default="", help="tool MCP của agent, cách nhau bằng dấu phẩy")
    ap.add_argument("--model", default="qwen-3b")
    ap.add_argument("--tag", default=os.environ.get("TAG", "dev"))
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    a.tools = [t for t in a.tools.split(",") if t]
    card = http(f"{a.kagent}/api/a2a/kagent/{a.agent}/.well-known/agent-card.json")
    if card.get("name") != a.agent.replace("-", "_"):      # chặn đăng nhầm card của agent khác
        raise SystemExit(f"card {card.get('name')!r} không khớp agent {a.agent!r}")
    # registry đọc JSON thì dừng sau object đầu, nên gửi YAML nhiều document thật
    body = yaml.safe_dump_all(resources(card, a), allow_unicode=True, sort_keys=False).encode()
    out = http(f"{a.registry}/v0/apply" + ("?dryRun=true" if a.dry_run else ""), body, {"Content-Type": "application/yaml"})
    failed = [r for r in out["results"] if r.get("status") == "failed"]
    for r in out["results"]:
        print(f"{r.get('kind', '?'):<10} {r.get('name', '?'):<20} {r.get('tag', ''):<10} {r.get('status')} {r.get('error', '')}")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
