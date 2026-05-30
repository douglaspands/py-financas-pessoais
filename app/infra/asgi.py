from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.financial_dash.controller import router as financial_dash_router


async def lifespan(app: FastAPI):
    yield


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.mount("/static", StaticFiles(directory="static"), name="static")
    app.include_router(financial_dash_router)
    return app
