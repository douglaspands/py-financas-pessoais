from functools import cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    db_url: str = "sqlite:///database/financeiro.db"
    db_debug: bool = True


@cache
def get_settings() -> Settings:
    return Settings()
