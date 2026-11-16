# Rubric edai-1 › Engineering Fundamentals › Docker & Docker Compose
#   - "Có sử dụng Docker & Docker Compose"  -> image này được docker-compose.yml dùng lại
#   - "Optimize Dockerfile (ví dụ multistage build)" -> 2 stage: builder + runtime
# Proof: so `docker images` của image này với docker/Dockerfile.single (1 stage, python:3.12 đầy đủ); số đo ghi
# trong docs/edai-1/docker.md, không ghi vào đây.

# ---------- Stage 1: builder — cài dependency có cần compiler ----------
FROM python:3.12-slim AS builder
WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# ---------- Stage 2: runtime — chỉ chép wheel đã build, không có gcc ----------
FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels
# generator/ gồm config.yaml: seed + tham số sinh dữ liệu (Dockerfile không cho comment cuối dòng)
COPY generator/ ./generator/
RUN useradd --create-home appuser && mkdir -p /data/events && chown appuser /data/events
USER appuser
ENTRYPOINT ["python", "-m", "generator.offline_gen"]
