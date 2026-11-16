"""Đăng agent card (A2A) của 1 agent kagent lên agent registry.
Card lấy từ endpoint A2A của chính agent qua agentgateway (/.well-known/agent-card.json), version = commit đang deploy.
shortcut: đường dẫn API của registry (/v0/agents) theo bản aregistry đã cài; đổi --path nếu bản khác."""
import argparse
import os

import requests

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", required=True)
    ap.add_argument("--registry", required=True)
    ap.add_argument("--gateway", default="http://agentgateway.gateway.svc.cluster.local:3000")
    ap.add_argument("--path", default="/v0/agents")
    a = ap.parse_args()
    card = requests.get(f"{a.gateway}/a2a/{a.agent}/.well-known/agent-card.json", timeout=10)
    card.raise_for_status()
    body = {**card.json(), "version": os.environ.get("TAG", "dev")}
    r = requests.put(f"{a.registry}{a.path}/{a.agent}", json=body, timeout=10)
    r.raise_for_status()
    print(f"published {a.agent} {body['version']} -> {a.registry}")
