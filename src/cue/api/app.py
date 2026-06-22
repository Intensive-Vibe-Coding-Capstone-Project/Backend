"""FastAPI application factory.

Feature routers (documents, sessions, rescue, stream) are added here as each
roadmap day lands them. Keep this file thin: wiring only, no business logic.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from cue import __version__
from cue.api.errors import register_error_handlers
from cue.api.routes import documents, health, rescue, sessions

_FRONTEND_DIR = Path(__file__).resolve().parents[3] / "frontend"


def create_app() -> FastAPI:
    """Build and configure the Cue FastAPI app."""
    app = FastAPI(
        title="Cue API",
        version=__version__,
        summary="Real-time presentation rescue agent — grounded rescue scripts from your docs.",
    )

    # Frontend lives in a separate repo; permissive CORS in dev. Tighten for prod.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_error_handlers(app)

    app.include_router(health.router)
    app.include_router(documents.router)  # D2: ingestion
    app.include_router(rescue.router)  # D4: retrieval + generation
    app.include_router(sessions.router)  # D5: sessions + history
    # Wired on their roadmap days:
    #   D8:    stream (WS/SSE) router

    # D7: text-path demo UI. Mounted at /ui (not /) so unknown API paths still
    # return the {error, detail} envelope. `GET /` redirects to it for convenience.
    if _FRONTEND_DIR.is_dir():

        @app.get("/", include_in_schema=False)
        def _root() -> RedirectResponse:
            return RedirectResponse(url="/ui/")

        app.mount("/ui", StaticFiles(directory=_FRONTEND_DIR, html=True), name="ui")

    return app
