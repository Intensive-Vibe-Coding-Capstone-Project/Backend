"""Rescue endpoint: a typed question -> grounded, line-by-line script."""

from __future__ import annotations

from fastapi import APIRouter

from cue.rescue import service
from cue.rescue.models import RescueRequest, RescueResponse

router = APIRouter(tags=["rescue"])


@router.post("/rescue", response_model=RescueResponse)
def rescue(request: RescueRequest) -> RescueResponse:
    """Retrieve grounded passages and return a speakable rescue script + citations."""
    return service.generate_rescue(request.question, request.k)
