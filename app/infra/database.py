from contextlib import asynccontextmanager
from functools import cache
from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.infra.settings import get_settings


@cache
def session_maker() -> async_sessionmaker[AsyncSession]:
    settings = get_settings()
    return async_sessionmaker(
        create_async_engine(
            settings.db_url(is_async=True),
            echo=settings.db_debug,
            connect_args={"check_same_thread": False},
        ),
        class_=AsyncSession,
        expire_on_commit=False,
    )


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, Any]:
    Session = session_maker()
    async with Session() as session:
        yield session
