# AI / agent platform (edai-2)

| Tài liệu | Nội dung |
|---|---|
| [llm_inference_platform.md](llm_inference_platform.md) | llm-d + vLLM, custom LLM, agentgateway, benchmark. |
| [global_model_config.md](global_model_config.md) | ModelConfig dùng chung cho các agent. |
| [agent_registry.md](agent_registry.md) | Registry cho agent và MCP server. |
| [rag_pipeline.md](rag_pipeline.md) | Tài liệu chính sách -> chunk -> embedding -> Feast, kèm governance. |
| [feature_store.md](feature_store.md) | Materialize offline -> online, push stream feature, TTL. |
| [ml_pipeline.md](ml_pipeline.md) | Notebook, Kubeflow pipeline, training phân tán, MLflow, version dữ liệu. |
| [ml_inference_service.md](ml_inference_service.md) | KServe model-inside-image. |
| [mcp_server.md](mcp_server.md) | booking-mcp: FastAPI, async, helm; agent dùng MCP tool, sandbox, registry. |
| [web_api.md](web_api.md) | Web API kéo dữ liệu, drift detection realtime, autoscale bằng KEDA. |
| [second_agent.md](second_agent.md) | Agent có tool ML và RAG. |
| [mcp_gateway.md](mcp_gateway.md) | agentgateway làm entrypoint cho MCP server. |
| [a2a_gateway.md](a2a_gateway.md) | agentgateway làm entrypoint cho agent. |
| [coordinator_agent.md](coordinator_agent.md) | Điều phối agent con; replica, autoscale, registry. |
| [warm_up.md](warm_up.md) | Giữ sẵn worker cho agent để giảm chi phí và độ trễ. |
| [testing.md](testing.md) | Unit test, EP/BVA, mutation, property-based, load test. |
| [cicd.md](cicd.md) | Jenkins: test + build + auto-deploy. CI/CD cho DP1–DP3 ở [edai-1/cicd.md](../edai-1/cicd.md). |
| [routing_gateway.md](routing_gateway.md) | Ẩn service sau ingress, basic auth, rate limit, domain + HTTPS. |
| [iac.md](iac.md) | Terraform cho GKE, Ansible cho VM. |
| [observability.md](observability.md) | Metric Web API, telemetry hệ thống, log, trace, LLM/agent, drift theo lịch. |
| [ab_testing.md](ab_testing.md) | A/B cho agent, LLM và model inference. |
| [security.md](security.md) | Vault cho secret, Istio cho service-to-service. |
| [ml_design.md](ml_design.md) | README/documentation, design pattern, 5 class chính. |
| [novel_ideas.md](novel_ideas.md) | Mỗi ý tưởng: vấn đề, cách làm, bằng chứng đã chạy. |

## Dòng rubric edai-2

| Dòng | Điểm | Mục | Tài liệu | Trạng thái |
|---|---|---|---|---|
| 3 | 2 | Deploy LLM inference platform | [llm_inference_platform.md](llm_inference_platform.md#edai-2-3) | Thiết kế · Cần làm |
| 4 | 2 | Setup a custom LLM model | [llm_inference_platform.md](llm_inference_platform.md#edai-2-4) | Cần làm |
| 5 | 1 | Setup agent gateway theo hướng dẫn và thiết lập security & policy phù hợp | [llm_inference_platform.md](llm_inference_platform.md#edai-2-5) | Đã có · Cần làm |
| 6 | 2 | Benchmark model server and optimize the platform | [llm_inference_platform.md](llm_inference_platform.md#edai-2-6) | Đã có · Thiết kế · Cần làm |
| 7 | 2 | Deploy 1 global model config để các Agent có thể dùng follow tutorial này, config này sẽ… | [global_model_config.md](global_model_config.md#edai-2-7) | Đã có · Cần làm |
| 8 | 2 | Deploy registry for agent theo tutorial này | [agent_registry.md](agent_registry.md#edai-2-8) | Đã có · Thiết kế · Cần làm |
| 9 | 2 | Build data pipeline với ít nhất các step sau: kéo dữ liệu từ text => chia chunk => lưu… | [rag_pipeline.md](rag_pipeline.md#edai-2-9) | Đã có · Cần sửa |
| 10 | 2 | Đảm bảo data governance cho pipeline | [rag_pipeline.md](rag_pipeline.md#edai-2-10) | Thiết kế · Cần làm |
| 11 | 2 | Build data pipeline để incremental materialize dữ liệu mới nhất từ OFFLINE qua ONLINE… | [feature_store.md](feature_store.md#edai-2-11) | Đã có · Cần làm |
| 12 | 2 | Deploy các jobs chịu trách nhiệm push streaming feature vào OFFLINE & ONLINE store | [feature_store.md](feature_store.md#edai-2-12) | Đã có · Cần làm |
| 13 | 2 | Build 1 training pipeline với ít nhất 4 steps: load data từ offline feature store, data… | [ml_pipeline.md](ml_pipeline.md#edai-2-13) | Đã có · Cần sửa |
| 14 | 2 | Lưu model, data và các metadata liên quan khác ở mỗi training run lên MLFlow, tự động gắn… | [ml_pipeline.md](ml_pipeline.md#edai-2-14) | Đã có |
| 15 | 2 | Sử dụng KServe để serve model vừa train ở bên trên, dùng model-inside-image pattern | [ml_inference_service.md](ml_inference_service.md#edai-2-15) | Đã có · Cần làm |
| 16 | 1 | Có sử dụng FastAPI + data validation + healthcheck for k8s | [mcp_server.md](mcp_server.md#edai-2-16) | Đã có |
| 17 | 1 | Sử dụng async cho concurrent processing | [mcp_server.md](mcp_server.md#edai-2-17) | Đã có |
| 18 | 2 | Deploy in the form of MCP tool to k8s with helm + rollingupdate + auto fallback | [mcp_server.md](mcp_server.md#edai-2-18) | Đã có · Cần làm |
| 19 | 2 | Deploy 1 Agent sử dụng MCP tool ở trên với multi-replica và auto-scale sử dụng cái này | [mcp_server.md](mcp_server.md#edai-2-19) | Đã có · Cần sửa · Cần làm |
| 20 | 1 | Configure Agent chạy trong Sandbox để đảm bảo security | [mcp_server.md](mcp_server.md#edai-2-20) | Thiết kế · Cần sửa · Cần làm |
| 21 | 1 | Publish Agent ở trên lên registry đã deploy để đảm bảo governance | [mcp_server.md](mcp_server.md#edai-2-21) | Đã có · Cần làm |
| 22 | 8 | Làm tương tự, thêm 1 Agent nhận dữ liệu từ Online Feature Store, và có 2 tools: | [second_agent.md](second_agent.md#edai-2-22) | Đã có · Cần làm |
| 23 | 2 | MCP Gateway | [mcp_gateway.md](mcp_gateway.md#edai-2-23) | Đã có |
| 24 | 2 | A2A Gateway | [a2a_gateway.md](a2a_gateway.md#edai-2-24) | Một phần · Cần làm |
| 25 | 2 | Deploy 1 Coordinator Agent với multi-replica và auto-scale sử dụng cái này | [coordinator_agent.md](coordinator_agent.md#edai-2-25) | Đã có · Cần sửa · Cần làm |
| 26 | 2 | Publish Agent ở này lên registry đã deploy để đảm bảo governance. | [coordinator_agent.md](coordinator_agent.md#edai-2-26) | Cần làm |
| 27 | 2 | Cài đặt hệ thống ở chế độ Warm Up cho agent theo hướng dẫn sau để tối ưu chi phí, đồng… | [warm_up.md](warm_up.md#edai-2-27) | Thiết kế · Cần làm |
| 28 | 1 | Unit test với Test Coverage > 90% | [testing.md](testing.md#edai-2-28) | Đã có |
| 29 | 2 | Có sử dụng kỹ thuật equivalence partitioning vs boundary value analysis khi thiết kế test… | [testing.md](testing.md#edai-2-29) | Đã có |
| 30 | 2 | Có sử dụng mutation testing để đánh giá hiệu quả của các test | [testing.md](testing.md#edai-2-30) | Đã có · Cần làm |
| 31 | 2 | Idempotency testing sử dụng property-based testing | [testing.md](testing.md#edai-2-31) | Đã có |
| 32 | 2 | Load test the Web API to understand throughput and latency | [testing.md](testing.md#edai-2-32) | Đã có · Cần làm |
| 33 | 2 | RAG Data Pipeline | [cicd.md](cicd.md#edai-2-33) | Thiết kế · Cần làm |
| 34 | 2 | Agent kéo dữ liệu | [cicd.md](cicd.md#edai-2-34) | Đã có · Cần làm |
| 35 | 2 | Agent để làm coordinator | [cicd.md](cicd.md#edai-2-35) | Thiết kế · Cần làm |
| 36 | 2 | CI/CD cho stream feature jobs | [cicd.md](cicd.md#edai-2-36) | Thiết kế · Cần làm |
| 37 | 2 | Service để coi metric | [routing_gateway.md](routing_gateway.md#edai-2-37) | Đã có · Cần làm |
| 38 | 2 | Service để coi log | [routing_gateway.md](routing_gateway.md#edai-2-38) | Đã có · Cần làm |
| 39 | 2 | Service để coi trace | [routing_gateway.md](routing_gateway.md#edai-2-39) | Đã có · Cần làm |
| 40 | 2 | UI để test agent | [routing_gateway.md](routing_gateway.md#edai-2-40) | Đã có · Cần làm |
| 41 | 2 | UI cho agent registry | [routing_gateway.md](routing_gateway.md#edai-2-41) | Đã có · Cần làm |
| 42 | 2 | Setup authentication cho UI test agent ở trên | [routing_gateway.md](routing_gateway.md#edai-2-42) | Đã có · Cần làm |
| 43 | 1 | Làm cái này cho Web API kéo dữ liệu | [routing_gateway.md](routing_gateway.md#edai-2-43) | Đã có · Cần làm |
| 44 | 1 | Dùng Terraform để setup GKE hoặc các cloud services | [iac.md](iac.md#edai-2-44) | Đã có · Cần làm |
| 45 | 1 | Dùng Ansible để configure và deploy các service lên VM | [iac.md](iac.md#edai-2-45) | Cần làm |
| 46 | 1 | Web API monitoring metrics such as req/s, num of reqs, num of failures, etc. | [observability.md](observability.md#edai-2-46) | Thiết kế · Cần làm |
| 47 | 1 | Collect và visualize metrics với Prometheus + Grafana | [observability.md](observability.md#edai-2-47) | Thiết kế · Cần làm |
| 48 | 1 | Tương tự cho logs | [observability.md](observability.md#edai-2-48) | Thiết kế · Cần làm |
| 49 | 1 | Tương tự cho traces | [observability.md](observability.md#edai-2-49) | Thiết kế · Cần làm |
| 50 | 2 | Đảm bảo ít nhất các metrics | [observability.md](observability.md#edai-2-50) | Đã có · Cần sửa · Cần làm |
| 51 | 2 | Đảm bảo ít nhất các metrics | [observability.md](observability.md#edai-2-51) | Đã có · Cần làm |
| 52 | 1 | Perform A/B test for agents with different model config and monitor them | [ab_testing.md](ab_testing.md#edai-2-52) | Thiết kế · Cần làm |
| 53 | 1 | Perform A/B test for different LLM versions on the LLM inference platform | [ab_testing.md](ab_testing.md#edai-2-53) | Đã có · Cần làm |
| 54 | 1 | Centralize secret management via Hashi Corp Vault so it will be used across the whole… | [security.md](security.md#edai-2-54) | Đã có · Cần làm |
| 55 | 2 | README.md và documentation follow rule ở ô A2 | [ml_design.md](ml_design.md#edai-2-55) | Cần làm |
| 56 | 2 | Idea 1 | [novel_ideas.md](novel_ideas.md#edai-2-56) | — |
| 57 | 2 | Idea 2 | [novel_ideas.md](novel_ideas.md#edai-2-57) | — |

## Dòng rubric final

| Dòng | Điểm | Mục | Tài liệu | Trạng thái |
|---|---|---|---|---|
| 3 | 2 | Có sử dụng FastAPI + data validation + healthcheck for k8s | [web_api.md](web_api.md#final-3) | Đã có · Cần làm |
| 4 | 2 | Sử dụng async | [web_api.md](web_api.md#final-4) | Đã có |
| 5 | 2 | Deploy to k8s with helm + rollingupdate + auto fallback | [web_api.md](web_api.md#final-5) | Đã có · Cần làm |
| 6 | 2 | Có sử dụng FastAPI + data validation + healthcheck for k8s | [web_api.md](web_api.md#final-6) | Đã có · Cần làm |
| 7 | 2 | Sử dụng async | [web_api.md](web_api.md#final-7) | Đã có |
| 8 | 2 | Deploy to k8s with helm + rollingupdate + auto fallback | [web_api.md](web_api.md#final-8) | Thiết kế · Cần làm |
| 9 | 2 | Web API kéo dữ liệu | [web_api.md](web_api.md#final-9) | Thiết kế · Cần làm |
| 10 | 2 | Web API cho drift detection | [web_api.md](web_api.md#final-10) | Thiết kế · Cần làm |
| 11 | 2 | Unit test với Test Coverage > 90% | [testing.md](testing.md#final-11) | Đã có · Cần làm |
| 12 | 2 | Có sử dụng kỹ thuật equivalence partitioning vs boundary value analysis khi thiết kế test… | [testing.md](testing.md#final-12) | Đã có · Cần làm |
| 13 | 2 | Có sử dụng mutation testing để đánh giá hiệu quả của các test | [testing.md](testing.md#final-13) | Đã có · Cần làm |
| 14 | 2 | Idempotency testing sử dụng property-based testing | [testing.md](testing.md#final-14) | Đã có · Thiết kế |
| 15 | 2 | Load test the Web API to understand throughput and latency | [testing.md](testing.md#final-15) | Đã có · Cần làm |
| 19 | 2 | Build data pipeline để incremental materialize dữ liệu mới nhất từ offline qua online… | [feature_store.md](feature_store.md#final-19) | Đã có · Cần làm |
| 20 | 1 | Deploy job chịu trách nhiệm push streaming feature vào OFFLINE store | [feature_store.md](feature_store.md#final-20) | Thiết kế |
| 21 | 1 | Deploy job chịu trách nhiệm push streaming feature vào ONLINE store | [feature_store.md](feature_store.md#final-21) | Đã có · Cần làm |
| 22 | 2 | Define TTL cho từng bảng feature, giải thích tại sao chọn TTL như thế | [feature_store.md](feature_store.md#final-22) | Đã có · Cần làm |
| 23 | 2 | Jupyter notebook để kéo dữ liệu từ offline store để tạo ra model. | [ml_pipeline.md](ml_pipeline.md#final-23) | Thiết kế |
| 24 | 2 | Chuyển đổi code từ Jupyter notebook thành training pipeline với số lượng step giống ở… | [ml_pipeline.md](ml_pipeline.md#final-24) | Đã có · Cần làm |
| 25 | 2 | Trong training pipeline, ở step train, thay bằng distributed training | [ml_pipeline.md](ml_pipeline.md#final-25) | Thiết kế · Cần làm |
| 26 | 2 | Khi training pipeline hoàn tất, thông tin của MODEL cần được lưu trữ lại ở Model Registry | [ml_pipeline.md](ml_pipeline.md#final-26) | Đã có |
| 27 | 2 | Mỗi lần kéo dữ liệu từ Feast về để training, cần version lại DATA theo cơ chế incremental | [ml_pipeline.md](ml_pipeline.md#final-27) | Thiết kế · Cần làm |
| 28 | 2 | Materialize Pipeline | [cicd.md](cicd.md#final-28) | Thiết kế · Cần làm |
| 29 | 2 | Training Pipeline | [cicd.md](cicd.md#final-29) | Thiết kế · Cần làm |
| 33 | 2 | Web API | [cicd.md](cicd.md#final-33) | Đã có · Cần làm |
| 34 | 1 | Inference Engine | [cicd.md](cicd.md#final-34) | Đã có · Thiết kế |
| 35 | 1 | Cho real-time drift detection Web API | [cicd.md](cicd.md#final-35) | Đã có · Cần làm |
| 36 | 1 | Job 1: Push stream feature to OFFLINE store | [cicd.md](cicd.md#final-36) | Thiết kế |
| 37 | 1 | Job 2: Push stream feature to ONLINE store | [cicd.md](cicd.md#final-37) | Thiết kế · Cần làm |
| 38 | 2 | Service để coi metric | [routing_gateway.md](routing_gateway.md#final-38) | Đã có · Cần làm |
| 39 | 2 | Service để coi log | [routing_gateway.md](routing_gateway.md#final-39) | Đã có · Cần làm |
| 40 | 2 | Service để coi trace | [routing_gateway.md](routing_gateway.md#final-40) | Đã có · Cần làm |
| 41 | 2 | Web API kéo dữ liệu | [routing_gateway.md](routing_gateway.md#final-41) | Thiết kế |
| 42 | 2 | Setup authentication & rate limit cho Web API kéo dữ liệu | [routing_gateway.md](routing_gateway.md#final-42) | Thiết kế |
| 43 | 1 | Làm cái này cho Web API kéo dữ liệu | [routing_gateway.md](routing_gateway.md#final-43) | Đã có · Cần làm |
| 44 | 2 | Dùng Terraform để setup GKE hoặc các cloud services | [iac.md](iac.md#final-44) | Đã có · Thiết kế |
| 45 | 2 | Dùng Ansible để configure và deploy các service lên VM | [iac.md](iac.md#final-45) | Thiết kế · Cần làm |
| 46 | 2 | Web API monitoring metrics such as req/s, num | [observability.md](observability.md#final-46) | Thiết kế |
| 47 | 2 | Collect và visualize metrics với Prometheus + Grafana | [observability.md](observability.md#final-47) | Thiết kế |
| 48 | 2 | Tương tự cho logs | [observability.md](observability.md#final-48) | Thiết kế |
| 49 | 2 | Tương tự cho traces | [observability.md](observability.md#final-49) | Thiết kế |
| 50 | 1 | Airflow data drift pipeline to periodically pull data from offline feature store and… | [observability.md](observability.md#final-50) | Đã có · Cần làm |
| 51 | 1 | Trigger retrain by calling Kubeflow API | [observability.md](observability.md#final-51) | Đã có · Cần làm |
| 52 | 1 | Perform A/B traffic split for 2 versions of inference service | [ab_testing.md](ab_testing.md#final-52) | Thiết kế |
| 53 | 1 | Setup monitoring dashboard to monitor 2 versions. | [ab_testing.md](ab_testing.md#final-53) | Thiết kế |
| 54 | 1 | Centralize secret management via Hashi Corp Vault so it will be used across the whole… | [security.md](security.md#final-54) | Đã có · Thiết kế |
| 55 | 1 | Using service mesh to authorize access from service to service | [security.md](security.md#final-55) | Đã có · Cần làm |
| 56 | 2 | Clean Code + clean repo + demonstrate the use of Design Pattern | [ml_design.md](ml_design.md#final-56) | Thiết kế |
| 57 | 1 | Propose 5 key classes to present our main focus: | [ml_design.md](ml_design.md#final-57) | Thiết kế |
| 58 | 2 | Idea 1 | [novel_ideas.md](novel_ideas.md#final-58) | — |
| 59 | 2 | Idea 2 | [novel_ideas.md](novel_ideas.md#final-59) | — |
