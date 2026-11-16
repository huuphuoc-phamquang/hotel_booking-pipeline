"""Thay systemMessage của từng Agent trong agents/agents.yaml bằng prompt Langfuse (label --prompt-label) rồi ghi ra --out.
Tên prompt như placeholder trong agents.yaml: data-agent, policy-agent, policy-agent-v2, coordinator. Khoá Langfuse lấy từ biến môi trường
LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY / LANGFUSE_HOST (Jenkins nạp từ Vault)."""
import argparse
import os

import yaml
from langfuse import Langfuse


def render(docs: list[dict], fetch) -> list[dict]:
    for d in docs:
        if d and d.get("kind") == "Agent":
            name = d["metadata"]["name"]
            d["spec"]["declarative"]["systemMessage"] = fetch(name.removesuffix("-agent") if name == "coordinator-agent" else name)
    return docs


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="agents/agents.yaml")
    ap.add_argument("--prompt-label", default="production")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    lf = Langfuse()
    with open(a.src, encoding="utf-8") as f:
        docs = render(list(yaml.safe_load_all(f)), lambda n: lf.get_prompt(n, label=a.prompt_label).prompt)
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        yaml.safe_dump_all(docs, f, allow_unicode=True, sort_keys=False)
