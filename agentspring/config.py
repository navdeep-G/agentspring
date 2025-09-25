from functools import lru_cache
from typing import Optional
from pydantic import PostgresDsn, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "AgentSpring"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # API
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/agentspring"
    SYNC_DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/agentspring"
    TEST_DATABASE_URL: Optional[str] = None

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS
    CORS_ORIGINS: list[str] = ["*"]

    # Single-tenant dev mode or multi-tenant admin
    API_KEY: str = "test-api-key"
    ADMIN_API_KEY: Optional[str] = None

    # --- Providers / Models ---
    DEFAULT_PROVIDER: str = "mock"
    MODEL: str = "mock"
    EMBEDDING_MODEL: str = "text-embedding-3-small"

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

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @validator("DATABASE_URL")
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> str:
        if isinstance(v, str):
            return v
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=values.get("POSTGRES_USER", "postgres"),
                password=values.get("POSTGRES_PASSWORD", "postgres"),
                host=values.get("POSTGRES_SERVER", "postgres"),
                path=f"/{values.get('POSTGRES_DB', 'agentspring') or ''}",
            )
        )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


# Global settings instance
settings = get_settings()
