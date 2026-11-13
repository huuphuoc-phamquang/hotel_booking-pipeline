# Tài liệu

Tài liệu của đồ án EDAI K11: nền tảng dữ liệu và AI cho ứng dụng đặt phòng khách sạn với định giá động.

- [architecture/](architecture/): sơ đồ triển khai tổng thể (`booking-pricing.drawio`, `booking-pricing.png`) và sơ đồ bảng (`booking-schema.drawio`).
- [edai-1/](edai-1/README.md): data platform. [edai-2/](edai-2/README.md): AI / agent platform. Các dòng của final-coursework nằm trong file cùng chủ đề ở hai thư mục này.
- `images/edai-1/`, `images/edai-2/`: ảnh chụp minh chứng.

Bảng dưới tra ngược từ dòng rubric (file `EDAI K11.xlsx`) sang mục tài liệu. Trạng thái lấy từ cột F lúc tạo khung; cập nhật khi điền kết quả.

## edai-1

| Dòng | Điểm | Mục | Tài liệu | Trạng thái |
|---|---|---|---|---|
| 3 | 2 | Có sử dụng Docker & Docker Compose | [edai-1/docker.md](edai-1/docker.md#edai-1-3) | Đã có · Cần làm |
| 4 | 3 | Optimize Dockerfile | [edai-1/docker.md](edai-1/docker.md#edai-1-4) | Đã có · Cần làm |
| 5 | 2 | Simulate skew | [edai-1/data_generator.md](edai-1/data_generator.md#edai-1-5) | Đã có · Cần làm |
| 6 | 2 | Simulate schema evolution | [edai-1/data_generator.md](edai-1/data_generator.md#edai-1-6) | Đã có · Cần làm |
| 7 | 2 | Simulate another offline data problem | [edai-1/data_generator.md](edai-1/data_generator.md#edai-1-7) | Đã có · Thêm cho novelty |
| 8 | 2 | Store data after generating so that we can ingest to Bronze zone later | [edai-1/data_generator.md](edai-1/data_generator.md#edai-1-8) | Đã có · Cần làm |
| 9 | 2 | Simulate late arrivals | [edai-1/data_generator.md](edai-1/data_generator.md#edai-1-9) | Đã có · Cần làm |
| 10 | 2 | Simulate another streaming data problem | [edai-1/data_generator.md](edai-1/data_generator.md#edai-1-10) | Đã có |
| 11 | 2 | Baseline | [edai-1/processing_jobs.md](edai-1/processing_jobs.md#edai-1-11) | Đã có · Cần sửa · Thiết kế · Cần làm |
| 12 | 3 | Handle skew with explanation | [edai-1/processing_jobs.md](edai-1/processing_jobs.md#edai-1-12) | Đã có · Thiết kế · Cần làm |
| 13 | 3 | Handle schema evolution with explanation | [edai-1/processing_jobs.md](edai-1/processing_jobs.md#edai-1-13) | Đã có · Cần làm |
| 14 | 3 | Handle other offline data problem with explanation | [edai-1/processing_jobs.md](edai-1/processing_jobs.md#edai-1-14) | Đã có · Cần làm |
| 15 | 2 | Spark job được tích hợp vào các data pipeline | [edai-1/processing_jobs.md](edai-1/processing_jobs.md#edai-1-15) | Cần làm |
| 16 | 2 | Baseline | [edai-1/processing_jobs.md](edai-1/processing_jobs.md#edai-1-16) | Đã có · Cần làm |
| 17 | 3 | Handle late arrival with explanation | [edai-1/processing_jobs.md](edai-1/processing_jobs.md#edai-1-17) | Đã có · Cần làm |
| 18 | 3 | Handle other streaming problem with explanation | [edai-1/processing_jobs.md](edai-1/processing_jobs.md#edai-1-18) | Đã có · Cần làm |
| 19 | 2 | Window processing | [edai-1/processing_jobs.md](edai-1/processing_jobs.md#edai-1-19) | Đã có |
| 20 | 3 | Lakehouse | [edai-1/data_storage.md](edai-1/data_storage.md#edai-1-20) | Đã có · Thiết kế · Cần làm |
| 21 | 3 | Datawarehouse | [edai-1/data_storage.md](edai-1/data_storage.md#edai-1-21) | Cần làm |
| 22 | 2 | Ingest stage | [edai-1/data_pipeline.md](edai-1/data_pipeline.md#edai-1-22) | Đã có · Cần sửa |
| 23 | 2 | Validate stage | [edai-1/data_pipeline.md](edai-1/data_pipeline.md#edai-1-23) | Đã có · Cần sửa |
| 24 | 2 | Ingest stage | [edai-1/data_pipeline.md](edai-1/data_pipeline.md#edai-1-24) | Cần làm |
| 25 | 2 | Validate stage | [edai-1/data_pipeline.md](edai-1/data_pipeline.md#edai-1-25) | Cần làm |
| 26 | 2 | Ingest stage | [edai-1/data_pipeline.md](edai-1/data_pipeline.md#edai-1-26) | Cần làm |
| 27 | 2 | Validate stage | [edai-1/data_pipeline.md](edai-1/data_pipeline.md#edai-1-27) | Cần làm |
| 28 | 2 | Lineage between the pipeline and tables | [edai-1/data_governance.md](edai-1/data_governance.md#edai-1-28) | Đã có · Cần làm |
| 29 | 2 | Data validation | [edai-1/data_governance.md](edai-1/data_governance.md#edai-1-29) | Đã có · Cần làm |
| 30 | 2 | Lineage between the pipeline and tables | [edai-1/data_governance.md](edai-1/data_governance.md#edai-1-30) | Đã có · Cần làm |
| 31 | 2 | Data validation | [edai-1/data_governance.md](edai-1/data_governance.md#edai-1-31) | Cần làm |
| 32 | 2 | Lineage between the pipeline and tables | [edai-1/data_governance.md](edai-1/data_governance.md#edai-1-32) | Đã có · Cần làm |
| 33 | 2 | Data validation | [edai-1/data_governance.md](edai-1/data_governance.md#edai-1-33) | Cần làm |
| 34 | 2 | Visualize tables on all zones | [edai-1/schema_design.md](edai-1/schema_design.md#edai-1-34) | Cần làm |
| 35 | 2 | Dim table with SCD 2 | [edai-1/schema_design.md](edai-1/schema_design.md#edai-1-35) | Đã có · Cần làm |
| 36 | 2 | Feature tables with 2 columns event_timestamp and created | [edai-1/schema_design.md](edai-1/schema_design.md#edai-1-36) | Đã có |
| 37 | 2 | Relationship between dim & fact tables | [edai-1/schema_design.md](edai-1/schema_design.md#edai-1-37) | Cần làm |
| 38 | 2 | Naming convention | [edai-1/schema_design.md](edai-1/schema_design.md#edai-1-38) | Đã có · Cần làm |
| 39 | 10 | Idea 1 | [edai-1/novel_ideas.md](edai-1/novel_ideas.md#edai-1-39) | — |
| 40 | 10 | Idea 2 | [edai-1/novel_ideas.md](edai-1/novel_ideas.md#edai-1-40) | — |

## edai-2

| Dòng | Điểm | Mục | Tài liệu | Trạng thái |
|---|---|---|---|---|
| 3 | 2 | Deploy LLM inference platform | [edai-2/llm_inference_platform.md](edai-2/llm_inference_platform.md#edai-2-3) | Thiết kế · Cần làm |
| 4 | 2 | Setup a custom LLM model | [edai-2/llm_inference_platform.md](edai-2/llm_inference_platform.md#edai-2-4) | Cần làm |
| 5 | 1 | Setup agent gateway theo hướng dẫn và thiết lập security & policy phù hợp | [edai-2/llm_inference_platform.md](edai-2/llm_inference_platform.md#edai-2-5) | Đã có · Cần làm |
| 6 | 2 | Benchmark model server and optimize the platform | [edai-2/llm_inference_platform.md](edai-2/llm_inference_platform.md#edai-2-6) | Đã có · Thiết kế · Cần làm |
| 7 | 2 | Deploy 1 global model config để các Agent có thể dùng follow tutorial này, config này sẽ… | [edai-2/global_model_config.md](edai-2/global_model_config.md#edai-2-7) | Đã có · Cần làm |
| 8 | 2 | Deploy registry for agent theo tutorial này | [edai-2/agent_registry.md](edai-2/agent_registry.md#edai-2-8) | Thiết kế · Cần làm |
| 9 | 2 | Build data pipeline với ít nhất các step sau: kéo dữ liệu từ text => chia chunk => lưu… | [edai-2/rag_pipeline.md](edai-2/rag_pipeline.md#edai-2-9) | Đã có · Cần sửa |
| 10 | 2 | Đảm bảo data governance cho pipeline | [edai-2/rag_pipeline.md](edai-2/rag_pipeline.md#edai-2-10) | Thiết kế · Cần làm |
| 11 | 2 | Build data pipeline để incremental materialize dữ liệu mới nhất từ OFFLINE qua ONLINE… | [edai-2/feature_store.md](edai-2/feature_store.md#edai-2-11) | Đã có · Cần sửa · Cần làm |
| 12 | 2 | Deploy các jobs chịu trách nhiệm push streaming feature vào OFFLINE & ONLINE store | [edai-2/feature_store.md](edai-2/feature_store.md#edai-2-12) | Đã có · Thiết kế · Cần làm |
| 13 | 2 | Build 1 training pipeline với ít nhất 4 steps: load data từ offline feature store, data… | [edai-2/ml_pipeline.md](edai-2/ml_pipeline.md#edai-2-13) | Đã có · Cần sửa |
| 14 | 2 | Lưu model, data và các metadata liên quan khác ở mỗi training run lên MLFlow, tự động gắn… | [edai-2/ml_pipeline.md](edai-2/ml_pipeline.md#edai-2-14) | Đã có |
| 15 | 2 | Sử dụng KServe để serve model vừa train ở bên trên, dùng model-inside-image pattern | [edai-2/ml_inference_service.md](edai-2/ml_inference_service.md#edai-2-15) | Đã có · Cần làm |
| 16 | 1 | Có sử dụng FastAPI + data validation + healthcheck for k8s | [edai-2/mcp_server.md](edai-2/mcp_server.md#edai-2-16) | Đã có |
| 17 | 1 | Sử dụng async cho concurrent processing | [edai-2/mcp_server.md](edai-2/mcp_server.md#edai-2-17) | Đã có |
| 18 | 2 | Deploy in the form of MCP tool to k8s with helm + rollingupdate + auto fallback | [edai-2/mcp_server.md](edai-2/mcp_server.md#edai-2-18) | Đã có · Cần làm |
| 19 | 2 | Deploy 1 Agent sử dụng MCP tool ở trên với multi-replica và auto-scale sử dụng cái này | [edai-2/mcp_server.md](edai-2/mcp_server.md#edai-2-19) | Đã có · Cần sửa · Cần làm |
| 20 | 1 | Configure Agent chạy trong Sandbox để đảm bảo security | [edai-2/mcp_server.md](edai-2/mcp_server.md#edai-2-20) | Thiết kế · Cần sửa · Cần làm |
| 21 | 1 | Publish Agent ở trên lên registry đã deploy để đảm bảo governance | [edai-2/mcp_server.md](edai-2/mcp_server.md#edai-2-21) | Cần làm |
| 22 | 8 | Làm tương tự, thêm 1 Agent nhận dữ liệu từ Online Feature Store, và có 2 tools: | [edai-2/second_agent.md](edai-2/second_agent.md#edai-2-22) | Đã có · Thiết kế · Cần làm |
| 23 | 2 | MCP Gateway | [edai-2/mcp_gateway.md](edai-2/mcp_gateway.md#edai-2-23) | Đã có |
| 24 | 2 | A2A Gateway | [edai-2/a2a_gateway.md](edai-2/a2a_gateway.md#edai-2-24) | Một phần · Cần làm |
| 25 | 2 | Deploy 1 Coordinator Agent với multi-replica và auto-scale sử dụng cái này | [edai-2/coordinator_agent.md](edai-2/coordinator_agent.md#edai-2-25) | Đã có · Cần sửa · Cần làm |
| 26 | 2 | Publish Agent ở này lên registry đã deploy để đảm bảo governance. | [edai-2/coordinator_agent.md](edai-2/coordinator_agent.md#edai-2-26) | Cần làm |
| 27 | 2 | Cài đặt hệ thống ở chế độ Warm Up cho agent theo hướng dẫn sau để tối ưu chi phí, đồng… | [edai-2/warm_up.md](edai-2/warm_up.md#edai-2-27) | Thiết kế · Cần làm |
| 28 | 1 | Unit test với Test Coverage > 90% | [edai-2/testing.md](edai-2/testing.md#edai-2-28) | Đã có |
| 29 | 2 | Có sử dụng kỹ thuật equivalence partitioning vs boundary value analysis khi thiết kế test… | [edai-2/testing.md](edai-2/testing.md#edai-2-29) | Đã có · Thiết kế |
| 30 | 2 | Có sử dụng mutation testing để đánh giá hiệu quả của các test | [edai-2/testing.md](edai-2/testing.md#edai-2-30) | Đã có · Cần làm |
| 31 | 2 | Idempotency testing sử dụng property-based testing | [edai-2/testing.md](edai-2/testing.md#edai-2-31) | Đã có |
| 32 | 2 | Load test the Web API to understand throughput and latency | [edai-2/testing.md](edai-2/testing.md#edai-2-32) | Đã có · Cần làm |
| 33 | 2 | RAG Data Pipeline | [edai-2/cicd.md](edai-2/cicd.md#edai-2-33) | Thiết kế · Cần làm |
| 34 | 2 | Agent kéo dữ liệu | [edai-2/cicd.md](edai-2/cicd.md#edai-2-34) | Đã có · Cần làm |
| 35 | 2 | Agent để làm coordinator | [edai-2/cicd.md](edai-2/cicd.md#edai-2-35) | Thiết kế · Cần làm |
| 36 | 2 | CI/CD cho stream feature jobs | [edai-2/cicd.md](edai-2/cicd.md#edai-2-36) | Thiết kế · Cần làm |
| 37 | 2 | Service để coi metric | [edai-2/routing_gateway.md](edai-2/routing_gateway.md#edai-2-37) | Đã có · Cần làm |
| 38 | 2 | Service để coi log | [edai-2/routing_gateway.md](edai-2/routing_gateway.md#edai-2-38) | Đã có · Cần làm |
| 39 | 2 | Service để coi trace | [edai-2/routing_gateway.md](edai-2/routing_gateway.md#edai-2-39) | Đã có · Cần làm |
| 40 | 2 | UI để test agent | [edai-2/routing_gateway.md](edai-2/routing_gateway.md#edai-2-40) | Đã có · Cần làm |
| 41 | 2 | UI cho agent registry | [edai-2/routing_gateway.md](edai-2/routing_gateway.md#edai-2-41) | Đã có · Cần làm |
| 42 | 2 | Setup authentication cho UI test agent ở trên | [edai-2/routing_gateway.md](edai-2/routing_gateway.md#edai-2-42) | Đã có · Cần làm |
| 43 | 1 | Làm cái này cho Web API kéo dữ liệu | [edai-2/routing_gateway.md](edai-2/routing_gateway.md#edai-2-43) | Đã có · Cần làm |
| 44 | 1 | Dùng Terraform để setup GKE hoặc các cloud services | [edai-2/iac.md](edai-2/iac.md#edai-2-44) | Đã có · Cần làm |
| 45 | 1 | Dùng Ansible để configure và deploy các service lên VM | [edai-2/iac.md](edai-2/iac.md#edai-2-45) | Cần làm |
| 46 | 1 | Web API monitoring metrics such as req/s, num of reqs, num of failures, etc. | [edai-2/observability.md](edai-2/observability.md#edai-2-46) | Thiết kế · Cần làm |
| 47 | 1 | Collect và visualize metrics với Prometheus + Grafana | [edai-2/observability.md](edai-2/observability.md#edai-2-47) | Thiết kế · Cần làm |
| 48 | 1 | Tương tự cho logs | [edai-2/observability.md](edai-2/observability.md#edai-2-48) | Thiết kế · Cần làm |
| 49 | 1 | Tương tự cho traces | [edai-2/observability.md](edai-2/observability.md#edai-2-49) | Thiết kế · Cần làm |
| 50 | 2 | Đảm bảo ít nhất các metrics | [edai-2/observability.md](edai-2/observability.md#edai-2-50) | Đã có · Cần sửa · Cần làm |
| 51 | 2 | Đảm bảo ít nhất các metrics | [edai-2/observability.md](edai-2/observability.md#edai-2-51) | Đã có · Cần làm |
| 52 | 1 | Perform A/B test for agents with different model config and monitor them | [edai-2/ab_testing.md](edai-2/ab_testing.md#edai-2-52) | Thiết kế · Cần làm |
| 53 | 1 | Perform A/B test for different LLM versions on the LLM inference platform | [edai-2/ab_testing.md](edai-2/ab_testing.md#edai-2-53) | Đã có · Cần làm |
| 54 | 1 | Centralize secret management via Hashi Corp Vault so it will be used across the whole… | [edai-2/security.md](edai-2/security.md#edai-2-54) | Đã có · Cần làm |
| 55 | 2 | README.md và documentation follow rule ở ô A2 | [edai-2/ml_design.md](edai-2/ml_design.md#edai-2-55) | Cần làm |
| 56 | 2 | Idea 1 | [edai-2/novel_ideas.md](edai-2/novel_ideas.md#edai-2-56) | — |
| 57 | 2 | Idea 2 | [edai-2/novel_ideas.md](edai-2/novel_ideas.md#edai-2-57) | — |

## final

| Dòng | Điểm | Mục | Tài liệu | Trạng thái |
|---|---|---|---|---|
| 3 | 2 | Có sử dụng FastAPI + data validation + healthcheck for k8s | [edai-2/web_api.md](edai-2/web_api.md#final-3) | Đã có · Cần làm |
| 4 | 2 | Sử dụng async | [edai-2/web_api.md](edai-2/web_api.md#final-4) | Đã có |
| 5 | 2 | Deploy to k8s with helm + rollingupdate + auto fallback | [edai-2/web_api.md](edai-2/web_api.md#final-5) | Đã có · Cần làm |
| 6 | 2 | Có sử dụng FastAPI + data validation + healthcheck for k8s | [edai-2/web_api.md](edai-2/web_api.md#final-6) | Thiết kế |
| 7 | 2 | Sử dụng async | [edai-2/web_api.md](edai-2/web_api.md#final-7) | Thiết kế |
| 8 | 2 | Deploy to k8s with helm + rollingupdate + auto fallback | [edai-2/web_api.md](edai-2/web_api.md#final-8) | Thiết kế · Cần làm |
| 9 | 2 | Web API kéo dữ liệu | [edai-2/web_api.md](edai-2/web_api.md#final-9) | Thiết kế · Cần làm |
| 10 | 2 | Web API cho drift detection | [edai-2/web_api.md](edai-2/web_api.md#final-10) | Thiết kế · Cần làm |
| 11 | 2 | Unit test với Test Coverage > 90% | [edai-2/testing.md](edai-2/testing.md#final-11) | Đã có · Thiết kế · Cần làm |
| 12 | 2 | Có sử dụng kỹ thuật equivalence partitioning vs boundary value analysis khi thiết kế test… | [edai-2/testing.md](edai-2/testing.md#final-12) | Thiết kế |
| 13 | 2 | Có sử dụng mutation testing để đánh giá hiệu quả của các test | [edai-2/testing.md](edai-2/testing.md#final-13) | Đã có · Cần làm |
| 14 | 2 | Idempotency testing sử dụng property-based testing | [edai-2/testing.md](edai-2/testing.md#final-14) | Đã có · Thiết kế |
| 15 | 2 | Load test the Web API to understand throughput and latency | [edai-2/testing.md](edai-2/testing.md#final-15) | Đã có · Cần làm |
| 16 | 2 | Simulate data drift | [edai-1/data_generator.md](edai-1/data_generator.md#final-16) | Đã có · Thiết kế |
| 17 | 2 | Using generator configuration | [edai-1/data_generator.md](edai-1/data_generator.md#final-17) | Đã có · Cần làm |
| 18 | 2 | Tạo bảng label có 2 cột id và label | [edai-1/data_generator.md](edai-1/data_generator.md#final-18) | Đã có · Cần làm |
| 19 | 2 | Build data pipeline để incremental materialize dữ liệu mới nhất từ offline qua online… | [edai-2/feature_store.md](edai-2/feature_store.md#final-19) | Đã có · Thiết kế · Cần làm |
| 20 | 1 | Deploy job chịu trách nhiệm push streaming feature vào OFFLINE store | [edai-2/feature_store.md](edai-2/feature_store.md#final-20) | Thiết kế |
| 21 | 1 | Deploy job chịu trách nhiệm push streaming feature vào ONLINE store | [edai-2/feature_store.md](edai-2/feature_store.md#final-21) | Đã có · Thiết kế |
| 22 | 2 | Define TTL cho từng bảng feature, giải thích tại sao chọn TTL như thế | [edai-2/feature_store.md](edai-2/feature_store.md#final-22) | Đã có · Thiết kế |
| 23 | 2 | Jupyter notebook để kéo dữ liệu từ offline store để tạo ra model. | [edai-2/ml_pipeline.md](edai-2/ml_pipeline.md#final-23) | Thiết kế |
| 24 | 2 | Chuyển đổi code từ Jupyter notebook thành training pipeline với số lượng step giống ở… | [edai-2/ml_pipeline.md](edai-2/ml_pipeline.md#final-24) | Đã có · Cần làm |
| 25 | 2 | Trong training pipeline, ở step train, thay bằng distributed training | [edai-2/ml_pipeline.md](edai-2/ml_pipeline.md#final-25) | Thiết kế · Cần làm |
| 26 | 2 | Khi training pipeline hoàn tất, thông tin của MODEL cần được lưu trữ lại ở Model Registry | [edai-2/ml_pipeline.md](edai-2/ml_pipeline.md#final-26) | Đã có |
| 27 | 2 | Mỗi lần kéo dữ liệu từ Feast về để training, cần version lại DATA theo cơ chế incremental | [edai-2/ml_pipeline.md](edai-2/ml_pipeline.md#final-27) | Thiết kế · Cần làm |
| 28 | 2 | Materialize Pipeline | [edai-2/cicd.md](edai-2/cicd.md#final-28) | Thiết kế · Cần làm |
| 29 | 2 | Training Pipeline | [edai-2/cicd.md](edai-2/cicd.md#final-29) | Thiết kế · Cần làm |
| 30 | 2 | DP 1 | [edai-1/cicd.md](edai-1/cicd.md#final-30) | Thiết kế |
| 31 | 2 | DP 2 | [edai-1/cicd.md](edai-1/cicd.md#final-31) | Thiết kế |
| 32 | 2 | DP 3 | [edai-1/cicd.md](edai-1/cicd.md#final-32) | Thiết kế |
| 33 | 2 | Web API | [edai-2/cicd.md](edai-2/cicd.md#final-33) | Thiết kế |
| 34 | 1 | Inference Engine | [edai-2/cicd.md](edai-2/cicd.md#final-34) | Đã có · Thiết kế |
| 35 | 1 | Cho real-time drift detection Web API | [edai-2/cicd.md](edai-2/cicd.md#final-35) | Thiết kế |
| 36 | 1 | Job 1: Push stream feature to OFFLINE store | [edai-2/cicd.md](edai-2/cicd.md#final-36) | Thiết kế |
| 37 | 1 | Job 2: Push stream feature to ONLINE store | [edai-2/cicd.md](edai-2/cicd.md#final-37) | Thiết kế |
| 38 | 2 | Service để coi metric | [edai-2/routing_gateway.md](edai-2/routing_gateway.md#final-38) | Đã có · Cần làm |
| 39 | 2 | Service để coi log | [edai-2/routing_gateway.md](edai-2/routing_gateway.md#final-39) | Đã có · Cần làm |
| 40 | 2 | Service để coi trace | [edai-2/routing_gateway.md](edai-2/routing_gateway.md#final-40) | Đã có · Cần làm |
| 41 | 2 | Web API kéo dữ liệu | [edai-2/routing_gateway.md](edai-2/routing_gateway.md#final-41) | Thiết kế |
| 42 | 2 | Setup authentication & rate limit cho Web API kéo dữ liệu | [edai-2/routing_gateway.md](edai-2/routing_gateway.md#final-42) | Thiết kế |
| 43 | 1 | Làm cái này cho Web API kéo dữ liệu | [edai-2/routing_gateway.md](edai-2/routing_gateway.md#final-43) | Đã có · Cần làm |
| 44 | 2 | Dùng Terraform để setup GKE hoặc các cloud services | [edai-2/iac.md](edai-2/iac.md#final-44) | Đã có · Thiết kế |
| 45 | 2 | Dùng Ansible để configure và deploy các service lên VM | [edai-2/iac.md](edai-2/iac.md#final-45) | Thiết kế · Cần làm |
| 46 | 2 | Web API monitoring metrics such as req/s, num | [edai-2/observability.md](edai-2/observability.md#final-46) | Thiết kế |
| 47 | 2 | Collect và visualize metrics với Prometheus + Grafana | [edai-2/observability.md](edai-2/observability.md#final-47) | Thiết kế |
| 48 | 2 | Tương tự cho logs | [edai-2/observability.md](edai-2/observability.md#final-48) | Thiết kế |
| 49 | 2 | Tương tự cho traces | [edai-2/observability.md](edai-2/observability.md#final-49) | Thiết kế |
| 50 | 1 | Airflow data drift pipeline to periodically pull data from offline feature store and… | [edai-2/observability.md](edai-2/observability.md#final-50) | Thiết kế |
| 51 | 1 | Trigger retrain by calling Kubeflow API | [edai-2/observability.md](edai-2/observability.md#final-51) | Thiết kế |
| 52 | 1 | Perform A/B traffic split for 2 versions of inference service | [edai-2/ab_testing.md](edai-2/ab_testing.md#final-52) | Thiết kế |
| 53 | 1 | Setup monitoring dashboard to monitor 2 versions. | [edai-2/ab_testing.md](edai-2/ab_testing.md#final-53) | Thiết kế |
| 54 | 1 | Centralize secret management via Hashi Corp Vault so it will be used across the whole… | [edai-2/security.md](edai-2/security.md#final-54) | Đã có · Thiết kế |
| 55 | 1 | Using service mesh to authorize access from service to service | [edai-2/security.md](edai-2/security.md#final-55) | Thiết kế · Cần làm |
| 56 | 2 | Clean Code + clean repo + demonstrate the use of Design Pattern | [edai-2/ml_design.md](edai-2/ml_design.md#final-56) | Thiết kế |
| 57 | 1 | Propose 5 key classes to present our main focus: | [edai-2/ml_design.md](edai-2/ml_design.md#final-57) | Thiết kế |
| 58 | 2 | Idea 1 | [edai-2/novel_ideas.md](edai-2/novel_ideas.md#final-58) | — |
| 59 | 2 | Idea 2 | [edai-2/novel_ideas.md](edai-2/novel_ideas.md#final-59) | — |
