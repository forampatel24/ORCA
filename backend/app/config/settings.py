"""Centralized configuration - docs 04_TECH_STACK, 14_SECURITY, 19_DEV_ENVIRONMENT."""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    environment: str = Field(default="development")
    log_level: str = Field(default="INFO")

    # Database
    database_url: str = Field(default="postgresql+psycopg://postgres:postgres@localhost:5432/orca_db")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0")

    # Qdrant
    qdrant_url: str = Field(default="http://localhost:6333")
    qdrant_api_key: str = Field(default="")

    # MinIO
    minio_endpoint: str = Field(default="localhost:9000")
    minio_access_key: str = Field(default="minioadmin")
    minio_secret_key: str = Field(default="minioadmin")
    minio_secure: bool = Field(default=False)

    # Mumbai-only - bbox filtering for all 39 datasets (no hardcoded coords elsewhere)
    mumbai_bbox: str = Field(default="72.2,18.5,73.2,19.5")
    mumbai_extended_bbox: str = Field(default="71.8,15.5,74.5,20.5")
    mumbai_point: str = Field(default="19.076,72.877")
    mumbai_state: str = Field(default="Maharashtra")

    # Provider endpoints - env overrideable for authentic sources
    incois_pfz_wms: str = Field(default="https://www.incois.gov.in/MarineFisheries/PfzWebGis")
    open_meteo_api: str = Field(default="https://api.open-meteo.com/v1/forecast")
    gfw_api: str = Field(default="https://api.globalfishingwatch.org/v2")
    copernicus_username: str = Field(default="")
    copernicus_password: str = Field(default="")

    # LLM - shared across all 8 agents (docs 06_AGENT_SPEC) — auto-detect gsk_->groq AIza->gemini else openai
    llm_api_key: str = Field(default="")
    llm_model: str = Field(default="gpt-4o-mini")
    llm_provider: str = Field(default="")  # openai|groq|gemini — empty=auto-detect
    llm_base_url: str = Field(default="")

    # JWT
    jwt_secret: str = Field(default="change-me-in-production")
    jwt_algorithm: str = Field(default="HS256")
    jwt_expire_minutes: int = Field(default=1440)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
