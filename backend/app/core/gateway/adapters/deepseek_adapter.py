from app.config import get_settings
from app.core.gateway.adapters import LLMAdapter, register_adapter

@register_adapter("deepseek")
class DeepSeekAdapter(LLMAdapter):
    def get_base_url(self) -> str:
        return get_settings().deepseek_base_url

    def get_api_key(self) -> str:
        return get_settings().deepseek_api_key

    def get_provider_name(self) -> str:
        return "deepseek"

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> float:
        rates = {
            "deepseek-chat": (0.001, 0.002),
            "deepseek-reasoner": (0.004, 0.012),
        }
        input_rate, output_rate = rates.get(model, (0.001, 0.002))
        return (prompt_tokens * input_rate + completion_tokens * output_rate) / 1000
