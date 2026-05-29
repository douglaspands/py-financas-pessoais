from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.index import controller as index_controller


async def lifespan(app: FastAPI):
    yield


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.mount("/static", StaticFiles(directory="static"), name="static")
    app.include_router(index_controller.router)
    return app
