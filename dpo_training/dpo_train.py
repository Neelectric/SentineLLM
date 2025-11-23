
from datasets import load_dataset
from trl import DPOConfig, DPOTrainer
from transformers import AutoModelForCausalLM, AutoTokenizer



def run_dpo_training(frontier_model_id, dataset_id):
    # train_dpo.py
    

    model = AutoModelForCausalLM.from_pretrained(frontier_model_id)
    tokenizer = AutoTokenizer.from_pretrained(frontier_model_id)
    train_dataset = load_dataset(dataset_id, split="train")

    training_args = DPOConfig(output_dir="Qwen2-0.5B-DPO")
    trainer = DPOTrainer(model=model, args=training_args, processing_class=tokenizer, train_dataset=train_dataset)
    trainer.train()
    return