import os
import requests
from openai import OpenAI

from src.review.prompt import PromptGenerator


client = OpenAI(
    api_key=os.environ["VSE_GPT_API_KEY"], base_url="https://api.vsegpt.ru/v1"
)
# client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")


def get_response(
    system_prompt: str, user_prompt: str, context: dict[str, list[str]]
) -> str:
    messages = [{"role": "system", "content": system_prompt}]
    for prompt, model_response in zip(context["user"], context["assistant"]):
        messages.append({"role": "user", "content": prompt})
        messages.append({"role": "assistant", "content": model_response})

    messages.append({"role": "user", "content": user_prompt})

    response = client.chat.completions.create(
        # model="qwen/qwen-2.5-coder-32b-instruct",
        model="google/gemma-2-27b-it",
        messages=messages,
        stream=False,
        temperature=0.15,
    )

    return response.choices[0].message.content
