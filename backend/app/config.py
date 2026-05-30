import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Career Advisor API"
    API_V1_STR: str = "/api/v1"

    # DB & Redis Settings
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/career_advisor"
    REDIS_URL: str = "redis://redis:6379/0"

    # Security
    JWT_SECRET: str = "supersecretjwtkeyforcareeradvisorappmvp2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # File Paths
    UPLOAD_DIR: str = "/app/uploads"
    REPORT_DIR: str = "/app/reports"

    # AI & LLM Provider
    LLM_PROVIDER: str = "nvidia_nim"  # "openai", "nvidia_nim", or "ollama"
    OPENAI_API_KEY: str = ""
    NVIDIA_API_KEY: str = ""
    NVIDIA_NIM_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    NVIDIA_NIM_MODEL: str = "minimaxai/minimax-m2.7"
    OLLAMA_BASE_URL: str = "http://host.docker.internal:11434"

    # Public data APIs
    CAREERNET_API_KEY: str = ""
    CAREERNET_BASE_URL: str = "https://www.career.go.kr"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.REPORT_DIR, exist_ok=True)
