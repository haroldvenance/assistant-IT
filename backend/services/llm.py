import httpx
import json
from typing import AsyncGenerator
from ..config import GROQ_API_KEY, AVAILABLE_MODELS

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

class LLMServiceError(Exception):
    pass

async def call_groq(
    messages: list,
    model: str,
    temperature: float = 0.3,
    max_tokens: int = 2000,
    timeout: float = 30.0
) -> str:
    if model not in AVAILABLE_MODELS:
        raise LLMServiceError(f"Modèle non supporté : {model}")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                GROQ_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                },
                timeout=timeout
            )
        except (httpx.ConnectError, httpx.RemoteProtocolError) as e:
            raise LLMServiceError(f"Erreur de connexion à l'API Groq : {e}") from e

    if response.status_code != 200:
        raise LLMServiceError(f"Erreur Groq ({response.status_code}): {response.text}")

    data = response.json()
    return data["choices"][0]["message"]["content"]

async def call_groq_stream(
    messages: list,
    model: str,
    temperature: float = 0.3,
    max_tokens: int = 2000,
    timeout: float = 60.0
) -> AsyncGenerator[str, None]:
    if model not in AVAILABLE_MODELS:
        raise LLMServiceError(f"Modèle non supporté : {model}")

    async with httpx.AsyncClient() as client:
        try:
            async with client.stream(
                "POST",
                GROQ_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": True
                },
                timeout=timeout
            ) as response:
                if response.status_code != 200:
                    error_body = await response.aread()
                    raise LLMServiceError(f"Erreur Groq stream ({response.status_code}): {error_body.decode()}")

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        try:
                            chunk = json.loads(line[6:])
                            token = chunk["choices"][0]["delta"].get("content", "")
                            if token:
                                yield token
                        except (json.JSONDecodeError, KeyError, IndexError):
                            continue
        except (httpx.ConnectError, httpx.RemoteProtocolError) as e:
            raise LLMServiceError(f"Erreur de connexion à l'API Groq : {e}") from e