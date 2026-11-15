# LLM inference platform

llm-d + vLLM, custom LLM, agentgateway, benchmark.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-2-3"></a>
## Deploy LLM inference platform

**Rubric:** edai-2 · dòng 3 · 2 điểm · nhóm *Deploy a LLM inference platform theo hướng dẫn này và set up gateway cho agent theo hướng dẫn này* › *Deploy LLM inference platform + setup custom model & agentgateway*

**Cần nộp (cả nhóm):** Document cách setup và benchmark cùng kết quả đạt được sau benchmark

**Cách làm:** [Đã chốt] chuyển sang llm-d theo quickstart của rubric; KServe huggingface runtime (llm_platform/llm-inference.yaml) là trạng thái mẫu, giữ đến khi llm-d chạy được rồi xoá. [Thiết kế] vLLM + llm-d router (EPP, Gateway API Inference Extension) cài bằng Helm + Kustomize, secret llm-d-hf-token; agentgateway /v1 trỏ tới router. [Cần làm] chụp pod Ready + gọi thử /v1/chat/completions.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-4"></a>
## Setup a custom LLM model

**Rubric:** edai-2 · dòng 4 · 2 điểm · nhóm *Deploy a LLM inference platform theo hướng dẫn này và set up gateway cho agent theo hướng dẫn này* › *Deploy LLM inference platform + setup custom model & agentgateway*

**Cách làm:** [Đã có] llm_platform/finetune: build_dataset.py (429 hội thoại từ policies/*.md + K từ overbooking.limit + từ chối PII, có test) và train_lora.py (LoRA r=16 Qwen2.5-1.5B-Instruct, bf16, vừa GPU 8GB, gộp adapter cho vLLM). [Cần làm] chạy fine-tune, upload s3://models/qwen2.5-1.5b-booking-sft/.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-5"></a>
## Setup agent gateway theo hướng dẫn và thiết lập security & policy phù hợp

**Rubric:** edai-2 · dòng 5 · 1 điểm · nhóm *Deploy a LLM inference platform theo hướng dẫn này và set up gateway cho agent theo hướng dẫn này* › *Deploy LLM inference platform + setup custom model & agentgateway*

> Setup agent gateway theo hướng dẫn và thiết lập security & policy phù hợp (trên này có rất nhiều doc để mn tham khảo)

**Cách làm:** [Đã có] agentgateway: jwtAuth Keycloak, localRateLimit, mcpAuthorization theo tool + role. [Cần làm] docs/edai-2/llm_inference_platform.md giải thích từng policy và vì sao chọn.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-6"></a>
## Benchmark model server and optimize the platform

**Rubric:** edai-2 · dòng 6 · 2 điểm · nhóm *Deploy a LLM inference platform theo hướng dẫn này và set up gateway cho agent theo hướng dẫn này* › *Deploy LLM inference platform + setup custom model & agentgateway*

**Cách làm:** [Đã có] arg tối ưu: prefix caching, max-model-len, gpu-memory-utilization. [Thiết kế] vllm bench serve / guidellm quét concurrency 1/4/16/64, workload có prefix chung; baseline -> bật prefix caching -> chỉnh gpu-memory-utilization / max-num-seqs -> routing prefix-aware của llm-d. [Cần làm] bảng throughput, TTFT, TPOT, E2E p50/p95/p99, lỗi trong docs/edai-2/llm_inference_platform.md.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
