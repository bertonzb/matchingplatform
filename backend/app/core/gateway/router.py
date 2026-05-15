from typing import AsyncIterator
import httpx
from app.core.gateway.adapters import get_adapter_for_model

class GatewayRouter:
    """Unified LLM call entry, compatible with OpenAI chat/completions format"""

    async def chat_completion(self, messages: list[dict], model: str,
                              stream: bool = False, **kwargs):
        adapter = get_adapter_for_model(model)
        if not adapter:
            raise ValueError(f"Unsupported model: {model}")

        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            **kwargs,
        }

        url = f"{adapter.get_base_url()}/chat/completions"
        headers = {
            "Authorization": f"Bearer {adapter.get_api_key()}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json(), adapter.get_provider_name(), adapter

    async def chat_completion_stream(self, messages: list[dict], model: str,
                                     **kwargs) -> AsyncIterator[dict]:
        adapter = get_adapter_for_model(model)
        if not adapter:
            raise ValueError(f"Unsupported model: {model}")

        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            **kwargs,
        }

        url = f"{adapter.get_base_url()}/chat/completions"
        headers = {
            "Authorization": f"Bearer {adapter.get_api_key()}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream("POST", url, json=payload, headers=headers) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line.startswith("data: ") and line != "data: [DONE]":
                        import json
                        yield json.loads(line[6:])
