"""server.py và risk_api.py tạo FeatureStore lúc import; test trỏ FEAST_REPO tới repo tạm (sqlite) để import được.
Mọi lời gọi online store trong test đều được mock, repo tạm không chứa dữ liệu."""
import os
import tempfile
from pathlib import Path

_repo = Path(tempfile.mkdtemp(prefix="feast-test-"))
(_repo / "feature_store.yaml").write_text(
    "project: test\nregistry: registry.db\nprovider: local\n"
    "online_store:\n  type: sqlite\n  path: online.db\nentity_key_serialization_version: 3\n")
os.environ.setdefault("FEAST_REPO", str(_repo))
