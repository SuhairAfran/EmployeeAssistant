from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, PostgresDsn, field_validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── App ─────────────────────────────────────────────────
    APP_NAME: str = "Enterprise AI Copilot"
    APP_ENV: str = "development"             # development | staging | production
    DEBUG: bool = False
    SECRET_KEY: str                          # used for JWT signing
    ALLOWED_ORIGINS: list[AnyHttpUrl] = []

    # ── Database ─────────────────────────────────────────────
    DATABASE_URL: PostgresDsn               # postgresql+asyncpg://user:pass@host/db
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_ECHO: bool = False                   # set True to log all SQL

    # ── Redis (short-term memory / rate limiting) ─────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    SESSION_TTL_SECONDS: int = 3600         # 1 hour idle timeout

    # ── LLM Providers ────────────────────────────────────────
    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: str = ""

    # Dynamic routing: which model for which task
    LLM_INTENT: str = "gpt-4o-mini"         # fast, cheap intent classification
    LLM_HR: str = "gpt-4o"                  # balanced for HR conversations
    LLM_IT: str = "gpt-4o-mini"             # fast for IT support
    LLM_FINANCE: str = "gpt-4o"             # strong reasoning for calculations
    LLM_EVALUATOR: str = "gpt-4o-mini"      # GEPA self-evaluation node
    LLM_TEMPERATURE: float = 0.1            # low temp for enterprise accuracy

    # ── LangSmith (tracing) ──────────────────────────────────
    LANGCHAIN_TRACING_V2: bool = True
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = "enterprise-ai-copilot"

    # ── Vector DB / RAG ──────────────────────────────────────
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIM: int = 1536
    RAG_TOP_K: int = 5
    RAG_SCORE_THRESHOLD: float = 0.75       # below this → trigger web search fallback
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50

    # ── FastMCP ──────────────────────────────────────────────
    MCP_HOST: str = "0.0.0.0"
    MCP_PORT: int = 8001

    # ── Email (Power Automate trigger) ───────────────────────
    POWER_AUTOMATE_WEBHOOK_URL: str = ""

    # ── JWT ──────────────────────────────────────────────────
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8-hour work day

    # ── Rate Limiting ─────────────────────────────────────────
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60

    # ── GEPA (self-evaluation) ───────────────────────────────
    GEPA_EVAL_THRESHOLD: float = 0.80       # retry if quality score < this
    GEPA_MAX_RETRIES: int = 2

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def fix_asyncpg_driver(cls, v: str) -> str:
        """Ensure asyncpg driver is used."""
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()