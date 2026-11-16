# Hotel booking pipeline: dự báo cancellation để overbooking

Model `cancel-risk` dự báo xác suất huỷ (cancellation probability) của từng booking. Xác suất được cộng dồn theo
khách sạn × đêm nhận phòng để đề xuất số phòng bán vượt K (overbooking limit). Revenue manager duyệt đề xuất trước khi
áp dụng (human-in-the-loop). `edai1/` là data platform, `edai2/` là nền tảng ML và agent.

## Mục lục

- [Bài toán](#bài-toán)
- [Kiến trúc](#kiến-trúc)
- [Cấu trúc repo](#cấu-trúc-repo)
- [Luồng dữ liệu theo ngày](#luồng-dữ-liệu-theo-ngày-airflow)
- [Tài liệu theo rubric](docs/README.md)

## Bài toán

Khách sạn bán phòng theo đêm, và một phần booking sẽ huỷ hoặc không đến (no-show). Nếu chỉ bán đúng số phòng, khách
sạn chịu spoilage (phòng trống). Nếu bán vượt quá tay, khách sạn phải walk khách, tức chuyển khách sang khách sạn khác.

Số booking huỷ của một đêm là tổng các biến Bernoulli với xác suất lấy từ `cancel-risk`, nên tuân theo phân phối
Poisson-binomial. K là số lớn nhất thoả P(số huỷ < K) ≤ c_spoil / (c_spoil + c_walk), với chi phí spoilage là 1 và chi phí
walk là 3. Do K dùng trực tiếp xác suất, model được đánh giá chủ yếu qua calibration, không chỉ qua AUC.

Dữ liệu do một generator tái lập được sinh ra, khoảng 108GB mỗi năm gồm quote, booking, cancellation và event stream.
Generator cài sẵn các lỗi thường gặp: double submit, schema đổi giữa năm, event trễ, vi phạm data contract. Drift cũng được
cài từ một ngày biết trước (2025-06-01). Nhờ vậy, các kết quả như đối soát stream, DLQ, calibration, sai số K và độ trễ
phát hiện drift đều so được với ground truth.

## Kiến trúc

![Kiến trúc](docs/architecture/booking-overbooking.png)

Nguồn sơ đồ: `docs/architecture/booking-overbooking.drawio`. Trạng thái từng dòng rubric:
[docs/README.md](docs/README.md).

## Cấu trúc repo

```
.
├── docs/             tài liệu theo từng dòng rubric
├── edai1/            data platform
│   ├── generator/    sinh dữ liệu landing (~108GB/năm) và replay event lên Kafka
│   ├── spark_jobs/   landing → Bronze → Silver (Iceberg) → staging Gold
│   ├── flink_jobs/   window, event trễ, khử trùng, DLQ
│   ├── dags/         DP1, DP2, DP3
│   ├── sql/
│   ├── schema/
│   ├── storage/
│   ├── governance/
│   ├── docker/
│   ├── k8s/
│   └── tests/
├── edai2/            ML + agent platform
│   ├── ml/           training pipeline (KFP, MLflow)
│   ├── risk_api/     API dự báo cancel-risk
│   ├── drift_api/    phát hiện drift theo thời gian thực
│   ├── mcp_server/   MCP tool cho agent, tính số phòng bán vượt K
│   ├── dags/         materialize, score_bookings, drift_monitor, RAG
│   ├── serving/      KServe InferenceService
│   ├── feature_repo/
│   ├── llm_platform/
│   ├── agents/
│   ├── gateway/
│   ├── observability/
│   ├── policies/
│   ├── helm/
│   ├── k8s/
│   ├── iac/
│   ├── ci/
│   ├── docker/
│   └── tests/
├── notebooks/        notebook cancel-risk
├── ci/
└── tests/
```

## Luồng dữ liệu theo ngày (Airflow)

Nhánh batch: `dp1_ingest_bronze` → `dp2_bronze_to_gold` → `dp3_offline_features` —Dataset→ `feast_materialize_incremental`
—Dataset→ `score_bookings`. `score_bookings` chấm mỗi booking mới một lần và ghi vào `gold.booking_risk`. Mỗi ngày,
`drift_monitor` tính PSI, KS và độ lệch calibration, đẩy kết quả lên PushGateway và gọi KFP retrain khi cần.

Nhánh stream: `event-replayer` → Kafka → Flink → `gold.feat_hotel_realtime` → `feast_materialize_realtime` (5 phút một lần).

Mọi DAG đều backfill được bằng `airflow dags backfill`, vì các mốc thời gian lấy theo logical date chứ không theo giờ máy.
