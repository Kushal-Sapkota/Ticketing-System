from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "IT Helpdesk Ticketing System"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://helpdesk:helpdesk_password@localhost:5432/helpdesk"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret_key: str = Field(default="change-me")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 480
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000", "http://localhost:5173"])

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> list[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [origin.strip() for origin in value if origin and origin.strip()]
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        raise TypeError("cors_origins must be a list or comma-separated string")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
