#!/usr/bin/env bash
# Benchmark vLLM (rubric edai-2 dòng 6): 3 cấu hình × concurrency 1/4/16/64, workload có prefix chung 256 token.
# Chạy trên máy có GPU + Docker:  ADAPTERS=<thư mục finetune_outputs> OUT=<thư mục kết quả> bash vllm_bench.sh
# Kết quả 2026-11-19 (laptop RTX 2000 Ada 8GB) là các file <cấu hình>-c<concurrency>.json cạnh script này.
set -u
export MSYS_NO_PATHCONV=1
OUT=${OUT:-bench-results}
ADAPTERS=${ADAPTERS:?đặt ADAPTERS tới thư mục finetune_outputs (có adapter_v1/)}
mkdir -p "$OUT"
BASE_ARGS="--model Qwen/Qwen2.5-1.5B-Instruct --served-model-name qwen-base --enable-lora --lora-modules qwen-booking-v1=/adapters/adapter_v1 --max-lora-rank 16 --max-model-len 2048"
declare -A CFG=(
  [1-baseline]="--gpu-memory-utilization 0.85 --no-enable-prefix-caching"
  [2-prefix]="--gpu-memory-utilization 0.85 --enable-prefix-caching"
  # 0.86: Windows/WSL giữ ~1GB VRAM, 0.92 báo "Free memory on device (6.93/8.0 GiB) ... less than desired"
  [3-tuned]="--gpu-memory-utilization 0.86 --enable-prefix-caching --max-num-seqs 64"
)
for name in 1-baseline 2-prefix 3-tuned; do
  docker rm -f vllm-booking >/dev/null 2>&1
  docker run -d --name vllm-booking --gpus all -p 8000:8000 --ipc=host -v hf-cache:/root/.cache/huggingface \
    -v "$ADAPTERS:/adapters:ro" vllm/vllm-openai:v0.9.2 $BASE_ARGS ${CFG[$name]} >/dev/null
  until curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/v1/models | grep -q 200; do
    [ "$(docker inspect -f '{{.State.Status}}' vllm-booking)" != running ] && { echo "$name: vLLM không khởi động"; docker logs vllm-booking 2>&1 | tail -5; exit 1; }
    sleep 5
  done
  for c in 1 4 16 64; do
    n=$(( c * 4 < 16 ? 16 : c * 4 ))
    docker exec vllm-booking vllm bench serve --backend vllm --base-url http://localhost:8000 \
      --model Qwen/Qwen2.5-1.5B-Instruct --served-model-name qwen-base --dataset-name random \
      --random-input-len 512 --random-output-len 128 --random-prefix-len 256 --num-prompts $n --max-concurrency $c \
      --seed 0 --save-result --result-dir /tmp --result-filename "$name-c$c.json" > /dev/null 2>&1
    docker cp "vllm-booking:/tmp/$name-c$c.json" "$OUT/$name-c$c.json" >/dev/null 2>&1 && echo "$name c=$c xong" || echo "$name c=$c LỖI"
  done
  docker logs vllm-booking 2>&1 | grep -m1 -i "GPU KV cache size\|Maximum concurrency" > "$OUT/$name-kv.txt"
done
echo BENCH_DONE
