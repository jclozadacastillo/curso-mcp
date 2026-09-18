"""Configuración de la aplicación mediante Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./gastos_dev.db"
    SECRET_KEY: str = "supersecretkeydefault32bytesminimumlengthrequiredhere!"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    DEMO_USER_EMAIL: str = "demo@gastos.local"
    DEMO_USER_PASSWORD: str = "demo_password_123"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
