# Image fine-tune LoRA qwen-booking, chạy trên node gpu-l4 (job.yaml). Build từ thư mục edai2:
#   docker build -f llm_platform/finetune/Dockerfile -t REGISTRY/llm/finetune:TAG .
FROM pytorch/pytorch:2.5.1-cuda12.4-cudnn9-runtime
WORKDIR /app/llm_platform/finetune
RUN pip install --no-cache-dir transformers==4.56.2 trl==0.23.0 peft==0.17.1 datasets==4.1.1 accelerate==1.10.1 \
    minio==7.2.20 numpy
# build_dataset.py nạp hàm limit từ ../../mcp_server, giữ đúng bố cục thư mục như trong repo
COPY mcp_server/overbooking.py /app/mcp_server/overbooking.py
COPY llm_platform/finetune/*.py ./
