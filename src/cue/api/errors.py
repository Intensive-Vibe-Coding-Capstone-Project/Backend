"""Consistent error shape: `{"error": ..., "detail": ...}` (per conventions)."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def _error_body(error: str, detail: object) -> dict[str, object]:
    return {"error": error, "detail": detail}


def register_error_handlers(app: FastAPI) -> None:
    """Attach handlers that normalize all errors to `{error, detail}`."""

    @app.exception_handler(StarletteHTTPException)
    async def _http_exc(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body("http_error", exc.detail),
        )

    @app.exception_handler(RequestValidationError)
    async def _validation_exc(request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=_error_body("validation_error", exc.errors()),
        )
