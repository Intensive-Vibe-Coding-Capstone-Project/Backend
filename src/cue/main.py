"""Process entry point.

`app` is the ASGI application (used by `uvicorn cue.main:app`). `run()` backs
the `cue` console script for a quick local dev server.
"""

from __future__ import annotations

from cue.api.app import create_app
from cue.config import get_settings

app = create_app()


def run() -> None:
    """Start a local dev server (reload on)."""
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "cue.main:app",
        host="127.0.0.1",
        port=8000,
        reload=settings.env == "dev",
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    run()
