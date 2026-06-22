"""FastAPI application factory.

Feature routers (documents, sessions, rescue, stream) are added here as each
roadmap day lands them. Keep this file thin: wiring only, no business logic.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from cue import __version__
from cue.api.errors import register_error_handlers
from cue.api.routes import health


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
    # Wired on their roadmap days:
    #   D2-D3: documents router (ingestion)
    #   D4:    rescue router
    #   D5:    sessions router
    #   D8:    stream (WS/SSE) router

    return app
