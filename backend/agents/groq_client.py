from groq import Groq
import json
import os
from typing import Optional

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

_client: Optional[Groq] = None

def get_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=GROQ_API_KEY)
    return _client

def llm(messages: list[dict], temperature: float = 0.7, max_tokens: int = 2048) -> str:
    client = get_client()
    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content or ""

def llm_json(messages: list[dict], temperature: float = 0.3) -> dict:
    content = llm(messages + [{"role": "user", "content": "Respond with valid JSON only, no markdown."}], temperature=temperature)
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[-1]
        content = content.rsplit("```", 1)[0]
    return json.loads(content.strip())

def system_msg(text: str) -> dict:
    return {"role": "system", "content": text}

def user_msg(text: str) -> dict:
    return {"role": "user", "content": text}
