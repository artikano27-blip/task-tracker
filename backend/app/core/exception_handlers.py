import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.exceptions import AppException

logger = logging.getLogger(__name__)

def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        details = f" | details: {exc.extra}" if exc.extra else ""
        logger.warning(
            f"{request.method} {request.url.path} -> {exc.code}: {exc.message}{details}"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.message,
                "code": exc.code,
            },
        )