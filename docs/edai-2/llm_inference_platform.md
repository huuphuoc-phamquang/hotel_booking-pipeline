# LLM inference platform

Nền tảng LLM gồm llm-d và vLLM, model tự fine-tune, agentgateway và benchmark.

Mỗi mục dưới đây ứng với một dòng của rubric. Phần **Cách làm** mô tả giải pháp đã triển khai, đồng bộ từ
cột F của rubric. Phần **Kết quả** ghi test đã chạy, số liệu đo được hoặc ảnh chụp (`docs/images/`).

<a id="edai-2-3"></a>
## Deploy LLM inference platform

**Rubric:** edai-2 · dòng 3 · 2 điểm · nhóm *Deploy a LLM inference platform theo hướng dẫn này và set up gateway cho agent theo hướng dẫn này* › *Deploy LLM inference platform + setup custom model & agentgateway*

**Cần nộp (cả nhóm):** Document cách setup và benchmark cùng kết quả đạt được sau benchmark

**Cách làm:** [Đã chốt] Chuyển sang llm-d theo quickstart của rubric. KServe huggingface runtime (`llm_platform/llm-inference.yaml`) là trạng thái mẫu, giữ lại tới khi llm-d chạy được thì xoá. [Thiết kế] vLLM và llm-d router (EPP, Gateway API Inference Extension) cài bằng Helm và Kustomize, secret `llm-d-hf-token`; route `/v1` của agentgateway trỏ tới router. [Cần làm] chụp pod Ready và một lần gọi thử `/v1/chat/completions`.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-2-4"></a>
## Setup a custom LLM model

**Rubric:** edai-2 · dòng 4 · 2 điểm · nhóm *Deploy a LLM inference platform theo hướng dẫn này và set up gateway cho agent theo hướng dẫn này* › *Deploy LLM inference platform + setup custom model & agentgateway*

**Cách làm:** [Đã có] `llm_platform/finetune` gồm `build_dataset.py` (429 hội thoại dựng từ `policies/*.md`, K từ `overbooking.limit` và các câu từ chối PII, có test) và `train_lora.py` (LoRA r=16 trên Qwen2.5-1.5B-Instruct, bf16, vừa GPU 8GB, gộp adapter để vLLM nạp). [Cần làm] chạy fine-tune, upload lên `s3://models/qwen2.5-1.5b-booking-sft/`.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-2-5"></a>
## Setup agent gateway theo hướng dẫn và thiết lập security & policy phù hợp

**Rubric:** edai-2 · dòng 5 · 1 điểm · nhóm *Deploy a LLM inference platform theo hướng dẫn này và set up gateway cho agent theo hướng dẫn này* › *Deploy LLM inference platform + setup custom model & agentgateway*

> Setup agent gateway theo hướng dẫn và thiết lập security & policy phù hợp (trên này có rất nhiều doc để mn tham khảo)

**Cách làm:** [Đã có] agentgateway áp dụng `jwtAuth` với Keycloak, `localRateLimit` và `mcpAuthorization` theo tool và role. [Cần làm] giải thích từng policy và lý do lựa chọn trong `docs/edai-2/llm_inference_platform.md`.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-2-6"></a>
## Benchmark model server and optimize the platform

**Rubric:** edai-2 · dòng 6 · 2 điểm · nhóm *Deploy a LLM inference platform theo hướng dẫn này và set up gateway cho agent theo hướng dẫn này* › *Deploy LLM inference platform + setup custom model & agentgateway*

**Cách làm:** [Đã có] Các tham số tối ưu: prefix caching, `max-model-len`, `gpu-memory-utilization`. [Thiết kế] Đo bằng `vllm bench serve` hoặc guidellm, quét concurrency 1/4/16/64 với workload có prefix chung. Trình tự: baseline → bật prefix caching → chỉnh `gpu-memory-utilization`, `max-num-seqs` → routing prefix-aware của llm-d. [Cần làm] ghi bảng throughput, TTFT, TPOT, độ trễ E2E p50/p95/p99 và tỉ lệ lỗi vào `docs/edai-2/llm_inference_platform.md`.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._
