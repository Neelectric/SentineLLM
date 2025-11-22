# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright contributors to the vLLM project

from vllm import LLM, SamplingParams

from datasets import load_dataset

dataset_id = "allenai/wildguardmix"
dataset = load_dataset(dataset_id, "wildguardtrain")["train"]
print(dataset)

prompts = [elt["prompt"] for elt in dataset if elt["prompt"] is not None and elt["prompt"] != ""]


print(len(prompts))
print(prompts[0])


# Create a sampling params object.
sampling_params = SamplingParams(temperature=0.8, top_p=0.95)


def main():
    # Create an LLM.
    llm = LLM(
        model="Qwen/Qwen3-4B-Thinking-2507",
        max_model_len=8192,
        )
    # Generate texts from the prompts.
    # The output is a list of RequestOutput objects
    # that contain the prompt, generated text, and other information.
    outputs = llm.generate(prompts, sampling_params)
    # Print the outputs.
    print("\nGenerated Outputs:\n" + "-" * 60)
    for output in outputs:
        prompt = output.prompt
        generated_text = output.outputs[0].text
        print(f"Prompt:    {prompt!r}")
        print(f"Output:    {generated_text!r}")
        print("-" * 60)


if __name__ == "__main__":
    main()