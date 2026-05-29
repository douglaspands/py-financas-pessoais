import typer
from fastapi import FastAPI

from app import cli, controller


async def lifespan(app: FastAPI):
    yield


def create_asgi() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(controller.router)
    return app


def create_cli() -> typer.Typer:
    app = typer.Typer(help="CLI utilitária para o sistema de Controle Financeiro.")
    app.add_typer(cli.app)
    return app
