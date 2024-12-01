import os
import requests

from src.review.prompt import PromptGenerator

from dotenv import load_dotenv

load_dotenv()

MODEL_API_KEY = os.getenv("MODEL_API_KEY")
URL = "http://84.201.152.196:8020/v1/completions"


def get_response(
    system_prompt: str, user_prompt: str, context: dict[str, list[str]]
) -> str:
    headers = {"Authorization": MODEL_API_KEY, "Content-Type": "application/json"}

    messages = [{"role": "system", "content": system_prompt}]
    for prompt, model_response in zip(context["user"], context["assistant"]):
        messages.append({"role": "user", "content": prompt})
        messages.append({"role": "assistant", "content": model_response})

    messages.append({"role": "user", "content": user_prompt})

    data = {
        "model": "mistral-nemo-instruct-2407",
        "messages": messages,
        "max_tokens": 1024,
        "temperature": 0.3,
    }

    response = requests.post(URL, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]

    raise RuntimeError(response.json()["error"]["message"])
