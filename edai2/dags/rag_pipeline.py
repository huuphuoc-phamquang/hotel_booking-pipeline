"""Ba DAG Airflow: RAG data pipeline (text -> chunk -> embedding -> Feast) và 2 DAG materialize.

Rubric edai-2:
  - RAG › RAG Data Pipeline        : load_docs -> chunk_docs -> embed_and_push (3 step bắt buộc)
  - RAG › data governance          : inlets/outlets -> DataHub lineage, validate_chunks trước khi push, embed_and_push
                                     kiểm đúng EMBED_DIM chiều; mỗi chunk ghi doc_sha256 (version tài liệu) + embed_model
  - Feature Store › materialize    : feast_materialize_incremental chạy khi DP3 xong (Airflow Dataset FEAT_BATCH),
                                     bắn Dataset ONLINE_BATCH -> DAG score_bookings; feast_materialize_realtime mỗi 5 phút
                                     cho hotel_realtime (Flink chỉ ghi offline gold.feat_hotel_realtime)
Connection/Variable (minio_docs, warehouse, feast_repo_path) đặt trong Airflow, không hard-code.
"""
from datetime import datetime, timedelta

import pandas as pd
from airflow.datasets import Dataset as AirflowDataset
from airflow.decorators import dag, task
from airflow.models import Variable
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from kubernetes.client import models as k8s
from datahub_airflow_plugin.entities import Dataset

CHUNK_TOKENS, OVERLAP_TOKENS = 512, 64
EMBED_MODEL = "BAAI/bge-m3"                  # 1024 chiều, đa ngôn ngữ: tài liệu tiếng Việt không cần tách từ
EMBED_DIM = 1024                              # = vector_length của policy_chunks (feature_repo/features.py)
# bge-m3 ~2,2GB trong RAM: pod riêng cho task embed (KubernetesExecutor), không chạy trong worker mặc định 1Gi
EMBED_POD = {"pod_override": k8s.V1Pod(spec=k8s.V1PodSpec(containers=[k8s.V1Container(
    name="base", resources=k8s.V1ResourceRequirements(requests={"memory": "4Gi", "cpu": "1"}, limits={"memory": "6Gi"}))]))}
# Feast materialize kéo cả cửa sổ ngày vào pandas: worker mặc định 2Gi bị OOMKilled sau ~45 s
MATERIALIZE_POD = {"pod_override": k8s.V1Pod(spec=k8s.V1PodSpec(containers=[k8s.V1Container(
    name="base", resources=k8s.V1ResourceRequirements(requests={"memory": "2Gi"}, limits={"memory": "8Gi"}))]))}
FEAT_BATCH = AirflowDataset("postgres://postgres:5432/warehouse/gold/feat_hotel_demand")   # do dp3_offline_features (edai1) bắn
ONLINE_BATCH = AirflowDataset("feast://online/batch")   # score_bookings lắng nghe Dataset này
BATCH_VIEWS = ["booking_attributes", "customer_booking_stats", "hotel_demand"]
REALTIME_TTL = timedelta(hours=2)            # = ttl của hotel_realtime (feature_repo/features.py)


@dag(dag_id="rag_data_pipeline", start_date=datetime(2025, 1, 1), schedule="@daily", catchup=False, tags=["rag"])
def rag_data_pipeline():
    """Đọc chính sách huỷ/hoàn tiền, quy định khách sạn, FAQ; chia chunk, embed và lưu vào policy_chunks."""

    @task(inlets=[Dataset("s3", "docs/policies")])
    def load_docs() -> list[dict]:
        """Kéo file .md từ MinIO bucket docs."""
        hook = S3Hook(aws_conn_id="minio_docs")
        keys = hook.list_keys(bucket_name="docs", prefix="policies/")
        import hashlib
        docs = [{"source": k, "text": hook.read_key(k, bucket_name="docs")} for k in keys
                if k.endswith(".md") and not k.endswith("README.md")]           # README mô tả thư mục, không phải chính sách
        return [{**d, "doc_sha256": hashlib.sha256(d["text"].encode()).hexdigest()} for d in docs]   # version tài liệu

    @task
    def chunk_docs(docs: list[dict]) -> list[dict]:
        """Chia theo token với overlap để câu ở biên chunk không mất ngữ cảnh."""
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained(EMBED_MODEL)
        chunks = []
        for d in docs:
            ids = tok.encode(d["text"], add_special_tokens=False)
            for i, start in enumerate(range(0, len(ids), CHUNK_TOKENS - OVERLAP_TOKENS)):
                chunks.append({"chunk_id": f"{d['source']}#{i}", "source": d["source"], "doc_sha256": d["doc_sha256"],
                               "text": tok.decode(ids[start:start + CHUNK_TOKENS])})
        return chunks

    @task
    def validate_chunks(chunks: list[dict]) -> list[dict]:
        """Data validation: không rỗng, chunk_id duy nhất; từng kết quả lên tab Validation của feat_policy_chunks."""
        from governance.emit_datahub import emit_from_airflow
        df = pd.DataFrame(chunks)
        checks = {"has_chunks": len(df) > 0,
                  "chunk_id_unique": len(df) == 0 or df["chunk_id"].is_unique,
                  "no_empty_chunk": len(df) == 0 or bool((df["text"].str.len() > 0).all())}
        for name, ok in checks.items():
            emit_from_airflow("postgres:warehouse.gold.feat_policy_chunks", name, ok)
        failed = [n for n, ok in checks.items() if not ok]
        if failed:
            raise ValueError(f"policy chunks fail {failed}")
        return chunks

    @task(outlets=[Dataset("postgres", "warehouse.gold.feat_policy_chunks")], executor_config=EMBED_POD)
    def embed_and_push(chunks: list[dict]) -> None:
        """Embed bằng sentence-transformers rồi ghi vào Feast (online + offline)."""
        from feast import FeatureStore
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(EMBED_MODEL)
        df = pd.DataFrame(chunks)
        vectors = model.encode(df["text"].tolist(), normalize_embeddings=True)
        assert vectors.shape == (len(df), EMBED_DIM), f"embedding {vectors.shape}, cần ({len(df)}, {EMBED_DIM})"
        df["embedding"] = vectors.tolist()
        df["embed_model"] = EMBED_MODEL
        df["event_timestamp"] = df["created"] = pd.Timestamp.now(tz="UTC")
        store = FeatureStore(repo_path=Variable.get("feast_repo_path"))
        # shortcut: chỉ ghi đè chunk_id còn tồn tại; tài liệu bị rút ngắn hoặc xoá để lại chunk cũ tới khi hết TTL 365
        # ngày. Cần xoá theo source trên online store trước khi ghi khi tài liệu chính sách hay đổi.
        store.write_to_online_store("policy_chunks", df)
        # Feast 0.68 không ghi được offline store PostgreSQL (thiếu offline_write_batch): upsert thẳng bảng nguồn của view
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        cols = ["chunk_id", "text", "source", "doc_sha256", "embed_model", "embedding", "event_timestamp", "created"]
        PostgresHook(postgres_conn_id="warehouse").insert_rows(
            "gold.feat_policy_chunks", list(df[cols].itertuples(index=False, name=None)), target_fields=cols,
            replace=True, replace_index="chunk_id")

    embed_and_push(validate_chunks(chunk_docs(load_docs())))


@dag(dag_id="feast_materialize_incremental", start_date=datetime(2025, 1, 1),
     schedule=[FEAT_BATCH], catchup=False, max_active_runs=1, tags=["feature-store"])
def feast_materialize_incremental():
    """Đẩy feature batch (snapshot hằng ngày) từ offline store (PostgreSQL) sang online store (PostgreSQL + pgvector).
    max_active_runs=1: khi backfill DP1-DP3, online store đi tuần tự từng ngày để score_bookings chấm đúng as-of.
    Backfill: online store mới (feast teardown + apply), `feast materialize` 1 lần tới ngày đầu, rồi backfill DP1-DP3."""

    @task(outlets=[ONLINE_BATCH], executor_config=MATERIALIZE_POD)
    def materialize(triggering_dataset_events=None) -> None:
        """Materialize đúng cửa sổ ngày logic của các run DP3 vừa xong (không dùng mốc incremental chung của Feast,
        không dùng giờ máy) nên backfill được; Feast lấy event_timestamp trong [start, end] gồm cả 2 đầu."""
        from feast import FeatureStore
        runs = [e.source_dag_run for evs in triggering_dataset_events.values() for e in evs]
        FeatureStore(repo_path=Variable.get("feast_repo_path")).materialize(
            start_date=min(r.data_interval_start for r in runs), end_date=max(r.data_interval_end for r in runs),
            feature_views=BATCH_VIEWS)

    materialize()


@dag(dag_id="feast_materialize_realtime", start_date=datetime(2025, 1, 1),
     schedule=timedelta(minutes=5), catchup=False, max_active_runs=1, tags=["feature-store"])
def feast_materialize_realtime():
    """Job 2 của nhánh stream: đưa cửa sổ mới nhất của gold.feat_hotel_realtime (Flink trượt mỗi 5 phút) lên online.
    shortcut: trễ tới 5 phút so với Flink, thay bằng store.push(ONLINE) trong Flink khi cần độ tươi tính bằng giây."""

    @task
    def materialize() -> None:
        """Cửa sổ [max(event_timestamp) - ttl, max] theo dữ liệu Flink đã ghi, không theo giờ máy: replay chạy giờ giả
        lập (01/2026) nên materialize_incremental (bắt đầu từ utcnow - ttl) không lấy được dòng nào."""
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from feast import FeatureStore
        latest = PostgresHook(postgres_conn_id="warehouse").get_first(
            "SELECT max(event_timestamp) FROM gold.feat_hotel_realtime")[0]
        if latest is None:                                  # Flink chưa đóng cửa sổ nào
            return
        FeatureStore(repo_path=Variable.get("feast_repo_path")).materialize(
            start_date=latest - REALTIME_TTL, end_date=latest, feature_views=["hotel_realtime"])

    materialize()


rag_data_pipeline()
feast_materialize_incremental()
feast_materialize_realtime()
