from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.expense_tracker.controller import router as expense_tracker_router


async def lifespan(app: FastAPI):
    yield


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan, doc_url=None, redoc_url=None)
    app.mount("/static", StaticFiles(directory="static"), name="static")
    app.include_router(expense_tracker_router)
    app.get("/")(
        lambda: RedirectResponse(
            url=expense_tracker_router.url_path_for("gastos:index"), status_code=302
        )
    )
    return app
