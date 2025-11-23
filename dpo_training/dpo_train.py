
from datasets import load_dataset
from trl import DPOConfig, DPOTrainer
from transformers import AutoModelForCausalLM, AutoTokenizer



def run_dpo_training(frontier_model_id, dataset_id):
    model = AutoModelForCausalLM.from_pretrained(frontier_model_id)
    tokenizer = AutoTokenizer.from_pretrained(frontier_model_id)
    train_dataset = load_dataset(dataset_id, split="train")

    training_args = DPOConfig(
        # Output
        output_dir="./dpo_output",

        num_train_epochs=1,
        per_device_train_batch_size=1,
        per_device_eval_batch_size=1,
        gradient_accumulation_steps=1,  
        
        # Learning rate
        learning_rate=5e-7,
        lr_scheduler_type="cosine",
        warmup_ratio=0.1,
        
        # Loss
        loss_type="sigmoid",  # Standard DPO
        beta=0.1,
        
        # Sequence lengths (small for testing)
        max_prompt_length=2048,
        max_length=2048,
        
        # Memory optimization
        gradient_checkpointing=True,
        bf16=True,  # or fp16=True if bf16 not available
        
        # Logging
        logging_steps=1,
        eval_strategy="none",
        
        # Saving
        save_strategy="steps",
        save_steps=0.5,
        save_total_limit=2,
        
        # Preprocessing
        dataset_num_proc=16,
        )
    
    
    
    trainer = DPOTrainer(
        model=model, 
        args=training_args, 
        processing_class=tokenizer, 
        train_dataset=train_dataset
        )
    trainer.train()
    return