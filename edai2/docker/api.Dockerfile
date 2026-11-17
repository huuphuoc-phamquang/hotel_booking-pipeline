# Image dùng chung cho FastAPI; build từ thư mục edai2:
#   docker build -f docker/api.Dockerfile --build-arg APP=mcp_server -t REGISTRY/agents/booking-mcp:TAG .
# drift_api: CI tải reference_lead_days.npy của model production vào drift_api/reference/ trước khi build.
FROM python:3.12-slim
ARG APP
WORKDIR /app
COPY ${APP}/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ${APP}/ .
RUN useradd -u 1000 app
USER 1000
EXPOSE 8000
