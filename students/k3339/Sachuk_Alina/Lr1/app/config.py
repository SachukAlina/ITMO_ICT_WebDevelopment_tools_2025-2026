from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "BookCrossing API"
    database_url: str = (
        "postgresql+psycopg://bookcrossing:bookcrossing@localhost:5432/bookcrossing"
    )
    jwt_secret_key: str = "development-only-secret-change-me-0000000000000000"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
