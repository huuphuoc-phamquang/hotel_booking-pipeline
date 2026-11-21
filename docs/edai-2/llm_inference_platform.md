# LLM inference platform

Nền tảng LLM gồm `llm-d` và vLLM, model tự fine-tune, `agentgateway` và benchmark hiệu năng.

<a id="edai-2-3"></a>
## Triển khai LLM inference platform (llm-d + vLLM)

**[update sau]:** Do tài khoản GCP mới chưa được duyệt quota GPU trên GKE, hệ thống tạm chạy vLLM trên máy GPU cá nhân và kết nối qua Cloudflare tunnel, đồng thời giữ manifest KServe mẫu tại `llm_platform/llm-inference.yaml`. Ý tưởng triển khai đầy đủ là cài đặt `llm-d` (vLLM + EPP router qua Gateway API Inference Extension) bằng Helm/Kustomize với secret `llm-d-hf-token`, trỏ route `/v1` của `agentgateway` vào `llm-d` router, rồi bổ sung ảnh pod Ready và log gọi thử `/v1/chat/completions`.

<a id="edai-2-4"></a>
## Fine-tune custom LLM model (LoRA SFT)

Bộ script trong `llm_platform/finetune/` gồm `build_dataset.py` (dựng 429 hội thoại từ `policies/*.md`, giá trị `K` từ `overbooking.limit` và các mẫu từ chối PII) và `train_lora.py` (fine-tune LoRA `r=16`, `bf16` vừa GPU 8GB rồi gộp adapter để vLLM nạp trực tiếp).

Trên GKE (1 GPU L4 spot, 2 epoch, 407 mẫu train / 22 mẫu eval), job đã fine-tune 2 phiên bản và đẩy lên MinIO (`upload.py`):

| Model | Thời gian Job | Loss train (epoch 0,4 → 1,9) | Eval loss | Eval token accuracy | Đích lưu trữ |
|---|---|---|---|---|---|
| v1 Qwen2.5-1.5B | 6 phút 35 giây | 1,77 → 0,41 | 0,401 | 0,840 | `s3://models/qwen2.5-1.5b-booking-sft/` (10 file) |
| v2 Qwen2.5-3B | 12 phút | 1,86 → 0,41 | 0,397 | 0,845 | `s3://models/qwen2.5-3b-booking-sft/` (12 file) |

Loss eval tiệm cận loss train cho thấy mô hình không bị overfit; bản 3B chỉ nhỉnh hơn 1.5B rất ít trên tập dữ liệu này.

![Log fine-tune v1 (Qwen2.5-1.5B)](../images/edai-2/finetune-v1-log.png)

![Log fine-tune v2 (Qwen2.5-3B)](../images/edai-2/finetune-v2-log.png)

<a id="edai-2-5"></a>
## Thiết lập Agent Gateway, bảo mật và policy

`agentgateway` v1.6.0 chạy standalone trong namespace `gateway` ([`k8s/agentgateway.yaml`](../../edai2/k8s/agentgateway.yaml), [`gateway/agentgateway.yaml`](../../edai2/gateway/agentgateway.yaml), [`gateway/deploy.sh`](../../edai2/gateway/deploy.sh)), làm điểm vào duy nhất cho cả LLM (`/v1`), MCP (`/mcp`) và A2A (`/a2a/<agent>`), kết hợp Keycloak 26.3 (`realm agents`) cấp JWT riêng cho từng agent.

| Policy | Thiết lập | Lý do |
|---|---|---|
| `jwtAuth` (`mode: strict`) | Kiểm tra issuer, audience `agentgateway`, JWKS từ Keycloak | Định danh từng agent, tự xác thực bằng JWKS; bắt buộc có token. |
| `backendAuth.key` | Nạp khoá vLLM từ Secret `vllm-key` | Agent chỉ cầm JWT, lộ token agent không làm lộ khoá vLLM. |
| `backendTLS` | TLS tới vLLM | Bảo vệ kết nối tới vLLM chạy qua Cloudflare tunnel HTTPS. |
| `localRateLimit` | Bucket 50, nạp 10 req/s trên `/v1` | Tránh agent lặp tool vô hạn làm nghẽn GPU. |
| `mcpAuthorization` | Phân quyền tool theo claim `role` | Nguyên tắc quyền tối thiểu giữa `data-agent` và `policy-agent`. |
| `a2a` + `urlRewrite` | `/a2a/<agent>/` → `/` | Nhận diện telemetry A2A và ẩn địa chỉ nội bộ của pod agent. |

Kiểm thử bằng [`gateway/check.sh`](../../edai2/gateway/check.sh): thiếu token hoặc token giả bị trả `401`; với token hợp lệ của `data-agent` chỉ thấy `get_booking_features` và bị chặn nếu gọi `predict_cancellation` (`Unknown tool`); `/a2a` trả `200` khi có token.

![Kiểm security & policy của agentgateway](../images/edai-2/agentgateway-check.png)

<a id="edai-2-6"></a>
## Benchmark và tối ưu model server

Benchmark chạy trên **laptop GPU RTX 2000 Ada 8 GB** với vLLM 0.9.2 phục vụ `Qwen2.5-1.5B-Instruct` kèm adapter LoRA v1 (`max-model-len 2048`), dùng `vllm bench serve` (prompt 512 token có 256 token tiền tố chung, output 128 token, không request nào lỗi):

| Cấu hình | Conc. | req/s | token ra/s | TTFT trung bình | TTFT p99 | TPOT trung bình |
|---|---|---|---|---|---|---|
| 1. Baseline, tắt prefix caching | 16 | 3,84 | 484 | 552 ms | 1.469 ms | 28,4 ms |
| | 64 | 6,67 | 829 | 1.244 ms | 5.895 ms | 67,7 ms |
| 2. Bật prefix caching | 16 | 4,35 | 505 | 327 ms | 910 ms | 27,4 ms |
| | 64 | 9,52 | 1.183 | 867 ms | 3.472 ms | 48,0 ms |
| 3. Prefix caching, `gpu-memory-utilization 0.86`, `max-num-seqs 64` | 16 | 4,43 | 505 | 251 ms | 840 ms | 27,1 ms |
| | 64 | 9,50 | 1.180 | 891 ms | 3.644 ms | 47,9 ms |

Bật prefix caching giúp tăng throughput 43% và giảm TTFT trung bình 30% (TTFT p99 giảm 41%) ở concurrency 64. Cấu hình 3 cải thiện thêm TTFT ở concurrency 16 (327 → 251 ms).

![vllm bench serve: 3 cấu hình × 4 mức concurrency](../images/edai-2/vllm-bench.png)

**[update sau]:** Do chưa có quota GPU trên GKE, phần đo benchmark với routing prefix-aware của `llm-d` trên cluster sẽ được thực hiện và cập nhật kết quả sau khi có quota GPU.
