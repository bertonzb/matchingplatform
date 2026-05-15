from abc import ABC, abstractmethod
from typing import AsyncIterator

class LLMAdapter(ABC):
    @abstractmethod
    def get_base_url(self) -> str: ...

    @abstractmethod
    def get_api_key(self) -> str: ...

    @abstractmethod
    def get_provider_name(self) -> str: ...

    @abstractmethod
    def estimate_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> float: ...


_registry: dict[str, type[LLMAdapter]] = {}

def register_adapter(model_prefix: str):
    def decorator(cls: type[LLMAdapter]):
        _registry[model_prefix] = cls
        return cls
    return decorator

def get_adapter_for_model(model: str) -> LLMAdapter | None:
    for prefix, cls in _registry.items():
        if model.startswith(prefix):
            return cls()
    return None
