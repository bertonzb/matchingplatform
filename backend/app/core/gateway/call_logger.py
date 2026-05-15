import time
from sqlalchemy.orm import Session
from app.models.llm_call_log import LLMCallLog

class CallLogger:
    def __init__(self, db: Session, provider: str, model: str):
        self.db = db
        self.provider = provider
        self.model = model
        self.start_time: float = 0
        self.prompt_tokens: int = 0
        self.completion_tokens: int = 0

    def start(self):
        self.start_time = time.time()

    def set_usage(self, prompt_tokens: int, completion_tokens: int):
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens

    def log(self, cost: float):
        latency = int((time.time() - self.start_time) * 1000)
        entry = LLMCallLog(
            model=self.model,
            provider=self.provider,
            prompt_tokens=self.prompt_tokens,
            completion_tokens=self.completion_tokens,
            latency_ms=latency,
            cost=cost,
        )
        self.db.add(entry)
        self.db.commit()
