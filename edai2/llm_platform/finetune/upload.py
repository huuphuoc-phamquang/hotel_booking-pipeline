"""Đẩy thư mục model đã gộp lên MinIO để InferenceService qwen-booking nạp (storageUri s3://models/<tên>/).

Chạy: python upload.py <thư mục model> <tên> ; tên = prefix trong bucket models, vd qwen2.5-1.5b-booking-sft
"""
import os
import sys
from pathlib import Path

from minio import Minio

BUCKET = "models"

if __name__ == "__main__":
    src, name = Path(sys.argv[1]), sys.argv[2]
    client = Minio(os.environ["MINIO_ENDPOINT"], access_key=os.environ["MINIO_ACCESS_KEY"],
                   secret_key=os.environ["MINIO_SECRET_KEY"], secure=False)
    if not client.bucket_exists(BUCKET):
        client.make_bucket(BUCKET)
    files = [p for p in src.rglob("*") if p.is_file()]
    assert any(p.suffix == ".safetensors" for p in files), f"không thấy weights trong {src}"
    for p in files:
        client.fput_object(BUCKET, f"{name}/{p.relative_to(src).as_posix()}", str(p))
    print(f"{len(files)} file -> s3://{BUCKET}/{name}/")
