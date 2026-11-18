# Tài liệu

Tài liệu của đồ án EDAI K11: nền tảng dữ liệu và AI cho ứng dụng đặt phòng khách sạn, dự báo cancellation của từng
booking để đề xuất số phòng overbooking (revenue manager duyệt).

- [problem_design.md](problem_design.md): thiết kế bài toán, từ xác suất huỷ tới số phòng bán vượt K.
- [architecture/](architecture/): sơ đồ triển khai tổng thể (`booking-overbooking.drawio`, `booking-overbooking.png`).
- [edai-1/](edai-1/README.md): data platform. [edai-2/](edai-2/README.md): nền tảng AI và agent.
- `images/edai-1/`, `images/edai-2/`: ảnh chụp minh chứng.

Tình trạng chạy thực tế:

- edai-1 đã chạy trên GKE (2026-11-17/18): generator 111 GiB, Kafka + Flink, Airflow DP1–DP3, DataHub và Spark trên
  105 GiB; ảnh ở `images/edai-1/`.
- edai-2: hạ tầng (Terraform) và observability (Prometheus, Grafana, EFK, Jaeger, ingress) đã chạy trên cluster
  (`images/edai-2/`). booking-mcp (MCP server) và online store Feast cũng đã chạy trên cluster. Các phần ML (Kubeflow,
  MLflow, KServe), LLM serving và agent mới chạy cục bộ hoặc mới có manifest.
