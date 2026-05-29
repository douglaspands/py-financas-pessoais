from contextlib import contextmanager
from functools import cache

from sqlmodel import Session, create_engine

from app.settings import get_settings


@cache
def get_engine():
    settings = get_settings()
    return create_engine(
        settings.db_url,
        echo=settings.db_debug,
        connect_args={"check_same_thread": False},
    )


@contextmanager
def get_session():
    with Session(get_engine()) as session:
        yield session
