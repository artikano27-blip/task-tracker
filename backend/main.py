import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.exception_handlers import register_exception_handlers
from core.redis import redis_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    yield
    await redis_client.aclose()
app = FastAPI(title="Task Tracker", lifespan=lifespan)

register_exception_handlers(app)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
