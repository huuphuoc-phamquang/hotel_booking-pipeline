# Hotel booking pipeline: dự báo cancellation để overbooking

Một model `cancel-risk` dự báo cancellation probability của từng booking; cộng dồn theo hotel × stay date để đề xuất
overbooking limit K, revenue manager duyệt trước khi áp dụng (human-in-the-loop). `edai1/` là data platform, `edai2/` là
ML + agent platform.

## Mục lục

- [Bài toán](#bài-toán)
- [Kiến trúc](#kiến-trúc)
- [Cấu trúc repo](#cấu-trúc-repo)
- [Luồng dữ liệu theo ngày](#luồng-dữ-liệu-theo-ngày-airflow)
- [Tài liệu theo rubric](docs/README.md)

## Bài toán

Khách sạn bán theo đêm; một phần booking sẽ cancel hoặc no-show, nên giữ đúng số phòng thì bị spoilage (phòng trống),
overbooking quá tay thì phải walk khách sang khách sạn khác. Số cancellation của một đêm là tổng các biến Bernoulli với
probability từ `cancel-risk` (Poisson-binomial); K là số lớn nhất sao cho P(số cancellation < K) ≤ c_spoil / (c_spoil + c_walk)
(spoilage cost 1, walk cost 3). Vì K dùng thẳng probability, model được đánh giá bằng calibration chứ không chỉ AUC.

Dữ liệu sinh bằng generator reproducible (~108GB/năm quote, booking, cancellation, event stream) với lỗi cài sẵn
(double submit, schema evolution giữa năm, late event, contract violation) và drift biết trước từ 2025-06-01, nên mọi
kết quả (stream reconciliation, DLQ, calibration, sai số K, drift detection delay) so được với ground truth.

## Kiến trúc

![Kiến trúc](docs/architecture/booking-overbooking.png)

Nguồn sơ đồ: `docs/architecture/booking-overbooking.drawio`. Trạng thái từng dòng rubric:
[docs/README.md](docs/README.md).

## Cấu trúc repo

```
docs/               tài liệu theo từng dòng rubric (edai-1, edai-2, final), architecture/, images/
edai1/              data platform
  generator/        sinh dữ liệu landing (~108GB/năm) và replay event stream lên Kafka
  spark_jobs/       landing -> Bronze -> Silver (Iceberg) -> staging Gold
  sql/              upsert Gold (SCD2, fact) và offline features
  dags/             DP1, DP2, DP3
  flink_jobs/       window + late event + dedup + DLQ
  schema/           Gold schema, data contract của topic booking_events
  storage/          Iceberg DDL, compaction, z-order
  governance/       DataHub lineage, data validation
  docker/ k8s/      image và manifest (MinIO, Postgres, Kafka, Flink, generator)
  tests/
edai2/              ML + agent platform
  feature_repo/     Feast feature definitions
  ml/               training pipeline (KFP, MLflow)
  risk_api/         API dự báo cancel-risk
  drift_api/        realtime drift detection
  mcp_server/       MCP tool cho agent, tính overbooking limit K
  dags/             RAG pipeline, materialize, score_bookings, drift_monitor
  serving/          KServe InferenceService
  llm_platform/     LLM inference, fine-tune
  agents/ gateway/  kagent, agentgateway
  observability/    metrics, dashboard, logging, tracing
  policies/         tài liệu nguồn cho RAG
  helm/ k8s/ iac/   deploy, IaC
  ci/ docker/       CI/CD, image dùng chung cho 3 API
  tests/
notebooks/          cancel_risk.ipynb
ci/                 Jenkinsfile cho data pipeline, DAG integrity test
tests/              test_dag_integrity.py
```

## Luồng dữ liệu theo ngày (Airflow)

`dp1_ingest_bronze` → `dp2_bronze_to_gold` → `dp3_offline_features` —Dataset→ `feast_materialize_incremental`
—Dataset→ `score_bookings` (batch scoring booking mới 1 lần, ghi `gold.booking_risk`) ; `drift_monitor` mỗi ngày
(PSI/KS + calibration gap → PushGateway, trigger KFP retrain). Stream: `event-replayer` → Kafka → Flink →
`gold.feat_hotel_realtime` → `feast_materialize_realtime` (5 phút). Tất cả backfill được (`airflow dags backfill`),
vì mọi mốc thời gian lấy theo logical date, không theo wall-clock.
