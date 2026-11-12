import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.api import account, admin, library, scholar
from app.api.routes import router
from app.config import get_settings
from app.db import init_db

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(_: FastAPI):
    if get_settings().auto_create_tables:
        await init_db()
    yield


app = FastAPI(title=get_settings().app_name, lifespan=lifespan)
app.include_router(router)
app.include_router(account.router)
app.include_router(library.router)
app.include_router(scholar.router)
app.include_router(admin.router)

_ADMIN_PAGE = Path(__file__).parent / "static" / "admin.html"


@app.get("/admin", include_in_schema=False)
async def admin_page() -> FileResponse:
    return FileResponse(_ADMIN_PAGE)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
