"""Rescue endpoint: a typed question -> grounded, line-by-line script."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from cue.rescue import service
from cue.rescue.models import RescueRequest, RescueResponse
from cue.sessions.errors import SessionNotFoundError

router = APIRouter(tags=["rescue"])


@router.post("/rescue", response_model=RescueResponse)
def rescue(request: RescueRequest) -> RescueResponse:
    """Retrieve grounded passages and return a speakable rescue script + citations."""
    try:
        return service.generate_rescue(request.question, request.k, request.session_id)
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"Session not found: {exc}") from exc
