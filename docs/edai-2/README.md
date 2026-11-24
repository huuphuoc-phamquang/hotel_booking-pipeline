# AI / agent platform (edai-2)

Môi trường chạy minh chứng:

- **GKE**: data platform, Feast, Kubeflow, MLflow, KServe, booking-mcp, kagent, agentgateway, registry, KEDA, Vault,
  observability, fine-tune LoRA (GPU L4).
- **K3s, GPU RTX 3060 12GB**: vLLM, Agent Substrate (sandbox gVisor, warm-up).
- **Laptop, GPU RTX 2000 Ada 8GB**: benchmark so sánh cấu hình vLLM, A/B offline giữa các bản LLM, vLLM cho agent trên GKE
  (qua Cloudflare tunnel).

| Tài liệu | Nội dung |
|---|---|
| [llm_inference_platform.md](llm_inference_platform.md) | Nền tảng LLM chạy vLLM, model tự fine-tune, agentgateway và benchmark. |
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
| [ml_design.md](ml_design.md) | README, sơ đồ kiến trúc tổng thể và các design pattern trong mã nguồn. |
| [novel_ideas.md](novel_ideas.md) | Mỗi ý tưởng gồm vấn đề, cách làm và minh chứng đã chạy. |
