from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_name: str = "Matching Platform"
    debug: bool = False

    # SQL Server
    db_server: str = "localhost"
    db_port: int = 1433
    db_name: str = "matching_db"
    db_user: str = "sa"
    db_password: str = ""

    @property
    def database_url(self) -> str:
        return (
            f"mssql+pyodbc://{self.db_user}:{self.db_password}"
            f"@{self.db_server}:{self.db_port}/{self.db_name}"
            f"?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
        )

    # Weaviate
    weaviate_url: str = "http://localhost:8080"

    # Redis / Celery
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # LLM Gateways
    qwen_api_key: str = ""
    qwen_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"

    # Embedding
    embedding_model: str = "BAAI/bge-large-zh-v1.5"

    # Matching
    matching_quality_threshold: float = 60.0
    matching_max_retries: int = 2
    matching_top_n_default: int = 5
    weaviate_top_k_recall: int = 20
    rerank_top_k: int = 5

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
