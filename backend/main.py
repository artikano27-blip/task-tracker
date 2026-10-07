from fastapi import FastAPI

from core.exception_handlers import register_exception_handlers

app = FastAPI(title="Task Tracker")

register_exception_handlers(app)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
