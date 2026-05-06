import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, field_validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",          # silently skip unknown env vars (e.g. LANGSMITH_*)
    )

    # ── App ─────────────────────────────────────────────────
    APP_NAME: str = "Employee Assistant"
    APP_ENV: str = "development"             # development | staging | production
    DEBUG: bool = False
    SECRET_KEY: str                          # used for JWT signing
    ALLOWED_ORIGINS: list[str] = []

    # ── Database ─────────────────────────────────────────────
    DATABASE_URL: PostgresDsn               # postgresql+asyncpg://user:pass@host/db
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_ECHO: bool = False                   # set True to log all SQL

    # ── Redis (short-term memory / rate limiting) ─────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    SESSION_TTL_SECONDS: int = 3600         # 1 hour idle timeout

    # ── LLM Providers ────────────────────────────────────────
    OPENAI_API_KEY: str = ""                 # optional — only if using OpenAI models
    ANTHROPIC_API_KEY: str = ""
    XAI_API_KEY: str = ""                    # Grok (xAI)
    GOOGLE_API_KEY: str = ""                 # Gemini
    OPENAI_BASE_URL: str | None = None
    OPENAI_VERIFY_SSL: bool = True

    # Dynamic routing: which model for which task
    # Prefix determines the provider: grok-* → xAI, gemini-* → Google, gpt-* → OpenAI
    LLM_INTENT: str = "grok-3-mini-fast"    # fast, cheap intent classification
    LLM_HR: str = "gemini-2.5-flash"        # balanced for HR conversations
    LLM_IT: str = "grok-3-mini-fast"        # fast for IT support
    LLM_FINANCE: str = "gemini-2.5-flash"   # strong reasoning for calculations
    LLM_EVALUATOR: str = "grok-3-mini-fast" # GEPA self-evaluation node
    LLM_TEMPERATURE: float = 0.1            # low temp for enterprise accuracy

    # ── LangSmith (tracing) ──────────────────────────────────
    LANGCHAIN_TRACING_V2: bool = True
    LANGCHAIN_API_KEY: str = ""
    LANGSMITH_PROJECT: str = "EmployeeAssistant"  # matches LANGSMITH_PROJECT in .env

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

# Inject LangSmith settings directly into OS environment for LangChain under-the-hood tracking
if settings.LANGCHAIN_TRACING_V2 and settings.LANGCHAIN_API_KEY:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = settings.LANGSMITH_PROJECT