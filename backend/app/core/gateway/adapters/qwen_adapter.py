from app.config import get_settings
from app.core.gateway.adapters import LLMAdapter, register_adapter

@register_adapter("qwen")
class QwenAdapter(LLMAdapter):
    def get_base_url(self) -> str:
        return get_settings().qwen_base_url

    def get_api_key(self) -> str:
        return get_settings().qwen_api_key

    def get_provider_name(self) -> str:
        return "qwen"

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> float:
        rates = {
            "qwen-turbo": (0.0003, 0.0006),
            "qwen-plus": (0.002, 0.006),
        }
        input_rate, output_rate = rates.get(model, (0.001, 0.002))
        return (prompt_tokens * input_rate + completion_tokens * output_rate) / 1000
