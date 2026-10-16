import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from app.routers.auth import router as auth_router
from app.core.exception_handlers import register_exception_handlers
from app.core.redis import redis_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    yield
    await redis_client.aclose()
app = FastAPI(title="Task Tracker", lifespan=lifespan)
app.include_router(auth_router)
register_exception_handlers(app)

app.mount("/", StaticFiles(directory="/frontend", html=True), name="frontend")
