# AI / agent platform (edai-2)

| Tài liệu | Nội dung |
|---|---|
| [llm_inference_platform.md](llm_inference_platform.md) | Nền tảng LLM gồm llm-d và vLLM, model tự fine-tune, agentgateway và benchmark. |
| [global_model_config.md](global_model_config.md) | Một ModelConfig dùng chung cho mọi agent. |
| [agent_registry.md](agent_registry.md) | Registry lưu agent card và MCP server. |
| [rag_pipeline.md](rag_pipeline.md) | Tài liệu chính sách được chia chunk, embed rồi lưu vào Feast, có lineage và kiểm tra dữ liệu. |
| [feature_store.md](feature_store.md) | Materialize feature từ offline sang online, đẩy stream feature và chọn TTL cho từng bảng. |
| [ml_pipeline.md](ml_pipeline.md) | Notebook, Kubeflow pipeline, training phân tán, MLflow và versioning dữ liệu train. |
| [ml_inference_service.md](ml_inference_service.md) | Model được phục vụ bằng KServe theo mô hình model-inside-image. |
| [mcp_server.md](mcp_server.md) | booking-mcp viết bằng FastAPI, xử lý bất đồng bộ, deploy bằng Helm; agent gọi MCP tool, chạy trong sandbox và được đăng ký trên registry. |
| [second_agent.md](second_agent.md) | Agent thứ hai dùng tool ML (`predict_cancellation`: Feast online + KServe) và tool RAG (`search_policy`). |
| [mcp_gateway.md](mcp_gateway.md) | agentgateway là điểm vào duy nhất cho MCP server. |
| [a2a_gateway.md](a2a_gateway.md) | agentgateway là điểm vào duy nhất cho các agent. |
| [coordinator_agent.md](coordinator_agent.md) | Coordinator điều phối các agent con; tài liệu gồm số replica, autoscale và registry. |
| [warm_up.md](warm_up.md) | Giữ sẵn worker cho agent để giảm chi phí và độ trễ khởi động. |
| [testing.md](testing.md) | Unit test, phân lớp tương đương và giá trị biên (EP/BVA), mutation test, property-based test và load test. |
| [cicd.md](cicd.md) | Jenkins chạy test, build image và tự deploy. |
| [routing_gateway.md](routing_gateway.md) | Service được đặt sau ingress, có basic auth, rate limit, domain và HTTPS. |
| [iac.md](iac.md) | Terraform dựng hạ tầng GKE; Ansible cấu hình VM. |
| [observability.md](observability.md) | Metric của Web API, telemetry hệ thống, log, trace, telemetry cho LLM và agent, kiểm tra drift theo lịch. |
| [ab_testing.md](ab_testing.md) | A/B testing cho agent, LLM và model inference. |
| [security.md](security.md) | Vault quản lý secret; Istio bảo vệ giao tiếp giữa các service. |
| [ml_design.md](ml_design.md) | README và tài liệu, các design pattern đã dùng và 5 class chính của hệ thống ML. |
| [novel_ideas.md](novel_ideas.md) | Mỗi ý tưởng gồm vấn đề, cách làm và minh chứng đã chạy. |

## Dòng rubric edai-2

| Dòng | Điểm | Mục | Tài liệu | Trạng thái |
|---|---|---|---|---|
| 3 | 2 | Deploy LLM inference platform | [llm_inference_platform.md](llm_inference_platform.md#edai-2-3) | Thiết kế · chờ cluster |
| 4 | 2 | Setup a custom LLM model | [llm_inference_platform.md](llm_inference_platform.md#edai-2-4) | Đã có |
| 5 | 1 | Setup agent gateway theo hướng dẫn và thiết lập security & policy phù hợp | [llm_inference_platform.md](llm_inference_platform.md#edai-2-5) | Đã có · Cần làm |
| 6 | 2 | Benchmark model server and optimize the platform | [llm_inference_platform.md](llm_inference_platform.md#edai-2-6) | Đã có · Thiết kế · Cần làm |
| 7 | 2 | Deploy 1 global model config để các Agent có thể dùng follow tutorial này, config này sẽ… | [global_model_config.md](global_model_config.md#edai-2-7) | Đã có · Cần làm |
| 8 | 2 | Deploy registry for agent theo tutorial này | [agent_registry.md](agent_registry.md#edai-2-8) | Đã có · Thiết kế · chờ cluster |
| 9 | 2 | Build data pipeline với ít nhất các step sau: kéo dữ liệu từ text => chia chunk => lưu… | [rag_pipeline.md](rag_pipeline.md#edai-2-9) | Đã có · chờ cluster |
| 10 | 2 | Đảm bảo data governance cho pipeline | [rag_pipeline.md](rag_pipeline.md#edai-2-10) | Đã có · chờ cluster |
| 11 | 2 | Build data pipeline để incremental materialize dữ liệu mới nhất từ OFFLINE qua ONLINE… | [feature_store.md](feature_store.md#edai-2-11) | Đã có · chờ cluster |
| 12 | 2 | Deploy các jobs chịu trách nhiệm push streaming feature vào OFFLINE & ONLINE store | [feature_store.md](feature_store.md#edai-2-12) | Đã có · chờ cluster |
| 13 | 2 | Build 1 training pipeline với ít nhất 4 steps: load data từ offline feature store, data… | [ml_pipeline.md](ml_pipeline.md#edai-2-13) | Đã có |
| 14 | 2 | Lưu model, data và các metadata liên quan khác ở mỗi training run lên MLFlow, tự động gắn… | [ml_pipeline.md](ml_pipeline.md#edai-2-14) | Đã có |
| 15 | 2 | Sử dụng KServe để serve model vừa train ở bên trên, dùng model-inside-image pattern | [ml_inference_service.md](ml_inference_service.md#edai-2-15) | Đã có · chờ cluster |
| 16 | 1 | Có sử dụng FastAPI + data validation + healthcheck for k8s | [mcp_server.md](mcp_server.md#edai-2-16) | Đã có |
| 17 | 1 | Sử dụng async cho concurrent processing | [mcp_server.md](mcp_server.md#edai-2-17) | Đã có |
| 18 | 2 | Deploy in the form of MCP tool to k8s with helm + rollingupdate + auto fallback | [mcp_server.md](mcp_server.md#edai-2-18) | Đã có · chờ cluster |
| 19 | 2 | Deploy 1 Agent sử dụng MCP tool ở trên với multi-replica và auto-scale sử dụng cái này | [mcp_server.md](mcp_server.md#edai-2-19) | Đã có · chờ cluster |
| 20 | 1 | Configure Agent chạy trong Sandbox để đảm bảo security | [mcp_server.md](mcp_server.md#edai-2-20) | Thiết kế · chờ cluster |
| 21 | 1 | Publish Agent ở trên lên registry đã deploy để đảm bảo governance | [mcp_server.md](mcp_server.md#edai-2-21) | Đã có · chờ cluster |
| 22 | 8 | Làm tương tự, thêm 1 Agent nhận dữ liệu từ Online Feature Store, và có 2 tools: | [second_agent.md](second_agent.md#edai-2-22) | Đã có · Cần làm |
| 23 | 2 | MCP Gateway | [mcp_gateway.md](mcp_gateway.md#edai-2-23) | Đã có |
| 24 | 2 | A2A Gateway | [a2a_gateway.md](a2a_gateway.md#edai-2-24) | Đã có · Cần làm |
| 25 | 2 | Deploy 1 Coordinator Agent với multi-replica và auto-scale sử dụng cái này | [coordinator_agent.md](coordinator_agent.md#edai-2-25) | Đã có · Cần làm |
| 26 | 2 | Publish Agent ở này lên registry đã deploy để đảm bảo governance. | [coordinator_agent.md](coordinator_agent.md#edai-2-26) | Đã có · chờ cluster |
| 27 | 2 | Cài đặt hệ thống ở chế độ Warm Up cho agent theo hướng dẫn sau để tối ưu chi phí, đồng… | [warm_up.md](warm_up.md#edai-2-27) | Thiết kế · chờ cluster |
| 28 | 1 | Unit test với Test Coverage > 90% | [testing.md](testing.md#edai-2-28) | Đã có |
| 29 | 2 | Có sử dụng kỹ thuật equivalence partitioning vs boundary value analysis khi thiết kế test… | [testing.md](testing.md#edai-2-29) | Đã có |
| 30 | 2 | Có sử dụng mutation testing để đánh giá hiệu quả của các test | [testing.md](testing.md#edai-2-30) | Đã có · chờ cluster |
| 31 | 2 | Idempotency testing sử dụng property-based testing | [testing.md](testing.md#edai-2-31) | Đã có |
| 32 | 2 | Load test the Web API to understand throughput and latency | [testing.md](testing.md#edai-2-32) | Đã có · chờ cluster |
| 33 | 2 | RAG Data Pipeline | [cicd.md](cicd.md#edai-2-33) | Đã có · chờ cluster |
| 34 | 2 | Agent kéo dữ liệu | [cicd.md](cicd.md#edai-2-34) | Đã có · chờ cluster |
| 35 | 2 | Agent để làm coordinator | [cicd.md](cicd.md#edai-2-35) | Đã có · chờ cluster |
| 36 | 2 | CI/CD cho stream feature jobs | [cicd.md](cicd.md#edai-2-36) | Đã có · chờ cluster |
| 37 | 2 | Service để coi metric | [routing_gateway.md](routing_gateway.md#edai-2-37) | Đã có · chờ cluster |
| 38 | 2 | Service để coi log | [routing_gateway.md](routing_gateway.md#edai-2-38) | Đã có · chờ cluster |
| 39 | 2 | Service để coi trace | [routing_gateway.md](routing_gateway.md#edai-2-39) | Đã có · chờ cluster |
| 40 | 2 | UI để test agent | [routing_gateway.md](routing_gateway.md#edai-2-40) | Đã có · chờ cluster |
| 41 | 2 | UI cho agent registry | [routing_gateway.md](routing_gateway.md#edai-2-41) | Đã có · chờ cluster |
| 42 | 2 | Setup authentication cho UI test agent ở trên | [routing_gateway.md](routing_gateway.md#edai-2-42) | Đã có · chờ cluster |
| 43 | 1 | Làm cái này cho Web API kéo dữ liệu | [routing_gateway.md](routing_gateway.md#edai-2-43) | Đã có · chờ cluster |
| 44 | 1 | Dùng Terraform để setup GKE hoặc các cloud services | [iac.md](iac.md#edai-2-44) | Đã có · chờ cluster |
| 45 | 1 | Dùng Ansible để configure và deploy các service lên VM | [iac.md](iac.md#edai-2-45) | Đã có · chờ cluster |
| 46 | 1 | Web API monitoring metrics such as req/s, num of reqs, num of failures, etc. | [observability.md](observability.md#edai-2-46) | Đã có · chờ cluster |
| 47 | 1 | Collect và visualize metrics với Prometheus + Grafana | [observability.md](observability.md#edai-2-47) | Đã có · chờ cluster |
| 48 | 1 | Tương tự cho logs | [observability.md](observability.md#edai-2-48) | Đã có · chờ cluster |
| 49 | 1 | Tương tự cho traces | [observability.md](observability.md#edai-2-49) | Đã có · Cần làm |
| 50 | 2 | Đảm bảo ít nhất các metrics | [observability.md](observability.md#edai-2-50) | Đã có |
| 51 | 2 | Đảm bảo ít nhất các metrics | [observability.md](observability.md#edai-2-51) | Đã có · chờ cluster |
| 52 | 1 | Perform A/B test for agents with different model config and monitor them | [ab_testing.md](ab_testing.md#edai-2-52) | Đã có · Cần làm |
| 53 | 1 | Perform A/B test for different LLM versions on the LLM inference platform | [ab_testing.md](ab_testing.md#edai-2-53) | Đã có · chờ cluster |
| 54 | 1 | Centralize secret management via Hashi Corp Vault so it will be used across the whole… | [security.md](security.md#edai-2-54) | Đã có · chờ cluster |
| 55 | 2 | README.md và documentation follow rule ở ô A2 | [ml_design.md](ml_design.md#edai-2-55) | Đã có |
| 56 | 2 | Idea 1 | [novel_ideas.md](novel_ideas.md#edai-2-56) | chờ cluster |
| 57 | 2 | Idea 2 | [novel_ideas.md](novel_ideas.md#edai-2-57) | — |
