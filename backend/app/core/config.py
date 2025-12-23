from pydantic_settings import BaseSettings
from typing import List
import secrets


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "DAAssist"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]

    # PostgreSQL
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "daassist"
    POSTGRES_PASSWORD: str = "daassist_password"
    POSTGRES_DB: str = "daassist"
    POSTGRES_PORT: int = 5432

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # SQL Server (Gestionale)
    SQLSERVER_HOST: str = "gestionale-server"
    SQLSERVER_PORT: int = 1433
    SQLSERVER_USER: str = "daassist_user"
    SQLSERVER_PASSWORD: str = "gestionale_password"
    SQLSERVER_DATABASE: str = "gestionale"
    SQLSERVER_REPLICA_DATABASE: str = "domarc_replica"

    @property
    def SQLSERVER_URL(self) -> str:
        return f"mssql+pymssql://{self.SQLSERVER_USER}:{self.SQLSERVER_PASSWORD}@{self.SQLSERVER_HOST}:{self.SQLSERVER_PORT}/{self.SQLSERVER_DATABASE}"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # JWT
    JWT_SECRET_KEY: str = secrets.token_urlsafe(32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@daassist.local"
    SMTP_TLS: bool = True

    # Google Calendar
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/calendar/sync/google/callback"

    # Microsoft 365
    MICROSOFT_CLIENT_ID: str = ""
    MICROSOFT_CLIENT_SECRET: str = ""
    MICROSOFT_TENANT_ID: str = ""
    MICROSOFT_REDIRECT_URI: str = "http://localhost:8000/api/v1/calendar/sync/outlook/callback"

    # Sync Settings
    SYNC_CLIENTS_INTERVAL_MINUTES: int = 15
    SYNC_CONTRACTS_INTERVAL_MINUTES: int = 15
    SYNC_REFERENTS_INTERVAL_MINUTES: int = 30

    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 10
    UPLOAD_DIR: str = "/tmp/daassist/uploads"

    # Encryption
    CREDENTIALS_ENCRYPTION_KEY: str = secrets.token_urlsafe(32)

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
