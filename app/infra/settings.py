from functools import cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    db_type: str = "sqlite"
    db_host: str = "database/financeiro.db"
    db_debug: bool = False

    def db_url(self, is_async: bool = False) -> str:
        conn = f"{self.db_type}{'+aiosqlite' if is_async else ''}:///"
        return f"{conn}{self.db_host}"


@cache
def get_settings() -> Settings:
    return Settings()
