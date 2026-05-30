from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Self

from fastapi import Request

from app.infra.database import AsyncSession, get_session
from app.infra.template import Jinja2Templates, templates


class Context:
    _session: AsyncSession | None = None
    _request: Request | None = None
    _template: Jinja2Templates | None = None

    def __init__(
        self: Self,
        session: AsyncSession | None = None,
        request: Request | None = None,
        template: Jinja2Templates | None = None,
    ):
        self._session = session
        self._request = request
        self._template = template

    @property
    def session(self: Self) -> AsyncSession:
        if not self._session:
            raise ValueError("session not found")
        return self._session

    @property
    def request(self: Self) -> Request:
        if not self._request:
            raise ValueError("request not found")
        return self._request

    @property
    def template(self: Self) -> Jinja2Templates:
        if not self._template:
            raise ValueError("template not found")
        return self._template


@asynccontextmanager
async def get_context(
    request: Request | None = None,
    template: Jinja2Templates | None = None,
) -> AsyncGenerator[Context, Any]:
    async with get_session() as session:
        yield Context(session=session, request=request, template=template)


async def get_context_from_request(
    request: Request,
) -> AsyncGenerator[Context, Any]:
    async with get_context(request=request, template=templates) as context:
        yield context


__all__ = ("Context", "get_context", "get_context_from_request")
