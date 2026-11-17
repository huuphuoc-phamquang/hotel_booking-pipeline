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

**Cách làm:** [Đã có] `llm_platform/finetune` gồm `build_dataset.py` (429 hội thoại dựng từ `policies/*.md`, K từ `overbooking.limit` và các câu từ chối PII, có test) và `train_lora.py` (LoRA r=16 trên Qwen2.5-1.5B-Instruct, bf16, vừa GPU 8GB, gộp adapter để vLLM nạp). Chạy trên GKE bằng Job `llm_platform/finetune/job.yaml` (node L4 spot): v1 Qwen2.5-1.5B và v2 Qwen2.5-3B, model gộp được `upload.py` đẩy lên `s3://models/qwen2.5-{1.5b,3b}-booking-sft/`.

**Kết quả:** chạy trên GKE ngày 2026-11-17, mỗi model một Job trên 1 GPU L4 (spot), 2 epoch, 407 mẫu train và 22 mẫu eval.

| Model | Thời gian Job | Loss train (epoch 0,4 → 1,9) | Eval loss | Eval token accuracy | Đích |
|---|---|---|---|---|---|
| v1 Qwen2.5-1.5B | 6 phút 35 giây | 1,77 → 0,41 | 0,401 | 0,840 | `s3://models/qwen2.5-1.5b-booking-sft/` (10 file) |
| v2 Qwen2.5-3B | 12 phút | 1,86 → 0,41 | 0,397 | 0,845 | `s3://models/qwen2.5-3b-booking-sft/` (12 file) |

Loss tính trên toàn bộ hội thoại (`assistant_only_loss=False`), kể cả system prompt lặp lại, nên dừng quanh 0,40. Loss eval xấp xỉ loss train, không có dấu hiệu overfit. Bản 3B chỉ nhỉnh hơn bản 1.5B rất ít trên bộ dữ liệu này.

![Log fine-tune v1 (Qwen2.5-1.5B)](../images/edai-2/finetune-v1-log.png)

![Log fine-tune v2 (Qwen2.5-3B)](../images/edai-2/finetune-v2-log.png)

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
