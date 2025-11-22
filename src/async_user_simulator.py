### async simulation

import asyncio
import time
import numpy as np
from vllm import AsyncLLMEngine, AsyncEngineArgs, SamplingParams
from datasets import load_dataset
import aiosqlite
from prometheus_client import Counter, Histogram, Gauge, make_asgi_app
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI


prompts_total = Counter('prompts_total', 'Total prompts processed')
prompts_dangerous = Counter('prompts_dangerous_total', 'Dangerous prompts')
gen_latency = Histogram('generation_latency_seconds', 'Generation time')
in_flight = Gauge('prompts_in_flight', 'Currently processing')


frontier_model_id = "allenai/OLMo-2-1124-7B-Instruct"
guard_model_id = ""
rate = 100


async def process_prompt(engine, prompt_id, prompt_text):
    start = time.time()
    
    sampling = SamplingParams(temperature=0.7, max_tokens=512)
    results_generator = engine.generate(prompt_text, sampling, f"req-{prompt_id}")
    
    async for result in results_generator:
        if result.finished:
            response = result.outputs[0].text
    
    print(f"[{prompt_id}] {time.time() - start:.2f}s {response[0:50]}")


async def main():
    # Load prompts
    dataset = load_dataset("allenai/wildguardmix", "wildguardtrain")["train"]
    prompts = [elt["prompt"] for elt in dataset if elt["prompt"]]
    
    # Init engine
    args = AsyncEngineArgs(
        model=frontier_model_id, 
        max_model_len=2048,
        gpu_memory_utilization=0.7
        )
    frontier_llm_engine = AsyncLLMEngine.from_engine_args(args)
    
    for i, prompt in enumerate(prompts):
        asyncio.create_task(process_prompt(frontier_llm_engine, i, prompt))
        
        
        await asyncio.sleep(np.random.exponential(1/rate))
    
    await asyncio.sleep(60)




if __name__ == "__main__":
    asyncio.run(main())