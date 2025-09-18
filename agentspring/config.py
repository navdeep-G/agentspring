# agentspring/config.py
from __future__ import annotations
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Read .env if present, accept unknown keys, and treat env names case-insensitively
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Core ---
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@db:5432/agentspring"
    )
    REDIS_URL: str = Field(default="redis://redis:6379/0")

    # Single-tenant dev mode or multi-tenant admin
    API_KEY: Optional[str] = None
    ADMIN_API_KEY: Optional[str] = None

    # --- Providers / Models ---
    DEFAULT_PROVIDER: str = "openai"
    OPENAI_API_KEY: Optional[str] = None
    MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_API_VERSION: Optional[str] = None

    # Anthropic
    ANTHROPIC_API_KEY: Optional[str] = None

    # Optional local/OSS
    OLLAMA_BASE_URL: Optional[str] = None

    # --- Security / Web ---
    ALLOWLIST_DOMAINS: str = ""              # CSV
    CORS_ALLOWED_ORIGINS: str = ""           # CSV
    REQUIRE_OIDC: bool = False
    OIDC_ISSUER: Optional[str] = None
    OIDC_AUDIENCE: Optional[str] = None

    # --- Celery / Background ---
    CELERY_BROKER_URL: Optional[str] = None  # falls back to REDIS_URL in code
    CELERY_RESULT_BACKEND: Optional[str] = None

    # --- Observability (make optional so absence never crashes) ---
    SENTRY_DSN: Optional[str] = None
    OTEL_EXPORTER_OTLP_ENDPOINT: Optional[str] = None
    OTEL_EXPORTER_OTLP_HEADERS: Optional[str] = None  # e.g. "Authorization=Bearer abc"

    # --- Logging / Env ---
    LOG_LEVEL: str = "INFO"
    AGENTSPRING_ENV: str = "development"
    LOG_DIR: str = "logs"

    # --- Example/demo keys (harmless; keep optional so extras don't crash) ---
    AGENTSPRING_APP: Optional[str] = None
    CUSTOMER_SUPPORT_AGENT_API_KEY: Optional[str] = None


settings = Settings()

