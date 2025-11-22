import asyncio
import time
import numpy as np
from datasets import load_dataset
from openai import AsyncOpenAI
from tqdm import tqdm
from transformers import AutoTokenizer

from olmo_trace import olmo_trace

frontier_model_id = "allenai/OLMo-2-1124-13B-Instruct"
guard_model_id = "Qwen/Qwen3Guard-Gen-0.6B"

FRONTIER_URL = "http://localhost:8001/v1"
GUARD_URL = "http://localhost:8002/v1"
RATE = 10

frontier_client = AsyncOpenAI(api_key="EMPTY", base_url=FRONTIER_URL)
guard_client = AsyncOpenAI(api_key="EMPTY", base_url=GUARD_URL)

async def process_prompt(prompt_id, prompt_text):
    start = time.time()
    
    # collect response from frontier model
    frontier_response = await frontier_client.chat.completions.create(
        model=frontier_model_id,
        messages=[{"role": "user", "content": prompt_text}],
        temperature=0.7,
        max_tokens=1800
    )
    
    frontier_text = frontier_response.choices[0].message.content
    # print(f"[{prompt_id}] {time.time() - start:.2f}s {frontier_text[:1]}")
    
    # collect safety rating from guard model
    safety_rating = 1
    guard_response = await guard_client.chat.completions.create(
        model=guard_model_id,
        messages=[
            {"role": "user", "content": prompt_text},
            {"role": "assistant", "content": frontier_text},
            ],
        )
    guard_text = guard_response.choices[0].message.content
    if "Unsafe" in guard_text:
        safety_rating = 0
        tqdm.write(prompt_text + "//////")
        tqdm.write(frontier_text)
        tqdm.write(guard_text)
        tqdm.write("#" * 50)
    pre_train_docs = olmo_trace(frontier_model_id, prompt_text, frontier_text)

    # print(f"----[{prompt_id}] {time.time() - start:.2f}s {safety_rating}")
    
    
    

async def main():
    dataset = load_dataset("allenai/wildguardmix", "wildguardtrain")["train"]
    prompts = [elt["prompt"] for elt in dataset if elt["prompt"]][0:500]
    
    for i, prompt in tqdm(enumerate(prompts), total=len(prompts)):
        asyncio.create_task(process_prompt(i, prompt))
        await asyncio.sleep(np.random.exponential(1/RATE))
    
    await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())