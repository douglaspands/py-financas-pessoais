import typer
from fastapi import FastAPI

from app import controller
from app.database import init_db


async def lifespan(app: FastAPI):
    init_db()
    yield


def create_asgi() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(controller.router)
    return app


def create_cli() -> typer.Typer:
    app = typer.Typer(help="CLI utilitária para o sistema de Controle Financeiro.")
    return app
