from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Generator, Self

from fastapi import Request
from sqlmodel import Session

from app.database import get_session
from app.template import Jinja2Templates, templates


class Context:
    _session: Session | None = None
    _request: Request | None = None
    _template: Jinja2Templates | None = None

    def __init__(
        self: Self,
        session: Session | None = None,
        request: Request | None = None,
        template: Jinja2Templates | None = None,
    ):
        self._session = session
        self._request = request
        self._template = template

    @property
    def session(self: Self) -> Session:
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


@contextmanager
def get_context(
    request: Request | None = None,
    template: Jinja2Templates | None = None,
) -> Generator[Context, Any, None]:
    with get_session() as session:
        yield Context(session=session, request=request, template=template)


def get_context_from_request(
    request: Request,
) -> Generator[Context, Any, None]:
    with get_context(request=request, template=templates) as context:
        yield context


__all__ = ("Context", "get_context", "get_context_from_request")
