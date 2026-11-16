"""LoRA SFT Qwen2.5-1.5B-Instruct trên bộ hội thoại booking, gộp adapter vào model để vLLM nạp như model thường.

Rubric edai-2 › Setup a custom LLM model: model ra thư mục --out, rồi
  mc cp --recursive <out>/ minio/models/qwen2.5-1.5b-booking-sft/   (llm_platform/llm-inference.yaml trỏ tới đây)
Bản 3B (v2 của A/B LLM) chạy cùng script với --base Qwen/Qwen2.5-3B-Instruct.
Vừa GPU 8GB: bf16, gradient checkpointing, batch 4 × accumulate 4, chỉ train LoRA (r=16) trên các ma trận attention + MLP.
Chạy: python train_lora.py --data booking_sft.jsonl --out out/qwen2.5-1.5b-booking-sft
"""
import argparse

import torch
from datasets import load_dataset
from peft import LoraConfig
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import SFTConfig, SFTTrainer

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="Qwen/Qwen2.5-1.5B-Instruct")
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--epochs", type=float, default=2)
    a = ap.parse_args()

    tok = AutoTokenizer.from_pretrained(a.base)
    data = load_dataset("json", data_files=a.data, split="train").train_test_split(test_size=0.05, seed=0)
    model = AutoModelForCausalLM.from_pretrained(a.base, torch_dtype=torch.bfloat16)
    lora = LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, task_type="CAUSAL_LM",
                      target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"])
    cfg = SFTConfig(output_dir=f"{a.out}-ckpt", num_train_epochs=a.epochs, per_device_train_batch_size=4,
                    gradient_accumulation_steps=4, learning_rate=2e-4, lr_scheduler_type="cosine", warmup_ratio=0.05,
                    bf16=True, gradient_checkpointing=True, max_length=1024, logging_steps=10, eval_strategy="epoch",
                    save_strategy="no", assistant_only_loss=False, report_to=[])
    trainer = SFTTrainer(model=model, args=cfg, train_dataset=data["train"], eval_dataset=data["test"],
                         processing_class=tok, peft_config=lora)
    trainer.train()
    print("eval:", trainer.evaluate())
    merged = trainer.model.merge_and_unload()                 # vLLM nạp model gộp, không cần nạp adapter riêng
    merged.save_pretrained(a.out, safe_serialization=True)
    tok.save_pretrained(a.out)
    print("saved", a.out)
