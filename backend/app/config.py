from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Islamic Guru API"
    database_url: str = "postgresql+asyncpg://guru:guru@localhost:5432/guru"

    # Auth
    jwt_secret: str = "change-me-in-production"
    jwt_expiry_days: int = 30

    # Claude (Anthropic SDK reads ANTHROPIC_API_KEY from the environment)
    answer_model: str = "claude-opus-5-5"
    answer_effort: str = "medium"
    rewrite_effort: str = "low"

    # Embeddings (optional). Without a key, retrieval falls back to keyword search.
    voyage_api_key: str | None = None
    embedding_model: str = "voyage-3.5"
    embedding_dim: int = 1024

    # Retrieval
    retrieval_top_k: int = 8
    min_relevance: float = 0.35  # cosine similarity floor for vector search

    # Free tier
    daily_free_questions: int = 10


@lru_cache
def get_settings() -> Settings:
    return Settings()
