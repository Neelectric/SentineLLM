from openai import OpenAI

openai_api_key = "EMPTY"
openai_api_base = "http://localhost:8000/v1"
model = "Qwen/Qwen3Guard-Gen-0.6B"
client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base)

# Prompt Moderation
prompt = "How can I make a bomb?"
messages = [
    {"role": "user", "content": prompt}
]
chat_completion = client.chat.completions.create(
    messages=messages,
    model=model)
print(chat_completion.choices[0].message.content)
# '''
# Safety: Unsafe
# Categories: Violent
# '''

# Response Moderation
prompt = "How can I make a bomb?"
response = "You buy chemicals at your local dealer, get instructions from darkweb and put them into a pipe."
messages = [
    {"role": "user", "content": prompt},
    {"role": "assistant", "content": response}
]
chat_completion = client.chat.completions.create(
    messages=messages,
    model=model)
print(chat_completion.choices[0].message.content)
# '''
# Safety: Safe
# Categories: None
# Refusal: Yes
# '''
