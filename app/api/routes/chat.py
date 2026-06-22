"""
Chat API routes.
Real-time chat with RAG-powered responses and conversation history.
"""

import uuid
import logging
from datetime import datetime, UTC
from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    ChatMessageRequest,
    ChatMessageResponse,
    ConversationSummary,
    ConversationDetail,
    MessageRecord,
    SourceReference,
)
from app.agents.orchestrator import agent_orchestrator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["Chat"])

# In-memory conversation store (will be replaced by Firebase in Day 3-4)
_conversations: dict[str, ConversationDetail] = {}


@router.post("/", response_model=ChatMessageResponse)
async def send_message(request: ChatMessageRequest):
    """
    Send a chat message and get a RAG-powered response.
    The response is generated using the multi-agent pipeline:
    Planning → Dev → QA → User
    """
    # Get or create conversation
    conv_id = request.conversation_id or f"conv_{uuid.uuid4().hex[:12]}"

    if conv_id not in _conversations:
        _conversations[conv_id] = ConversationDetail(
            id=conv_id,
            title=request.message[:50] + ("..." if len(request.message) > 50 else ""),
            messages=[],
            document_ids=request.document_ids or [],
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

    conversation = _conversations[conv_id]

    # Store user message
    user_msg = MessageRecord(
        id=f"msg_{uuid.uuid4().hex[:8]}",
        role="user",
        content=request.message,
    )
    conversation.messages.append(user_msg)

    # Process through agent pipeline
    result = await agent_orchestrator.process_query(
        query=request.message,
        doc_ids=request.document_ids or conversation.document_ids,
    )

    # Store assistant message
    assistant_msg = MessageRecord(
        id=f"msg_{uuid.uuid4().hex[:8]}",
        role="assistant",
        content=result["response"],
        sources=[
            SourceReference(**s) if isinstance(s, dict) else s
            for s in result.get("sources", [])
        ],
    )
    conversation.messages.append(assistant_msg)
    conversation.updated_at = datetime.now(UTC)

    # Build response with lyrics-style formatted lines
    return ChatMessageResponse(
        response=result["response"],
        sources=[
            SourceReference(**s) if isinstance(s, dict) else s
            for s in result.get("sources", [])
        ],
        conversation_id=conv_id,
        confidence=result.get("confidence", 0.0),
        formatted_lines=result.get("formatted_lines", []),
    )


@router.get("/history", response_model=list[ConversationSummary])
async def list_conversations():
    """List all conversations (most recent first)."""
    summaries = []
    for conv in sorted(
        _conversations.values(),
        key=lambda c: c.updated_at,
        reverse=True,
    ):
        summaries.append(ConversationSummary(
            id=conv.id,
            title=conv.title,
            message_count=len(conv.messages),
            document_ids=conv.document_ids,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
        ))
    return summaries


@router.get("/history/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(conversation_id: str):
    """Get the full conversation with all messages."""
    if conversation_id not in _conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return _conversations[conversation_id]


@router.delete("/history/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation."""
    if conversation_id not in _conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    del _conversations[conversation_id]
    return {"message": f"Conversation {conversation_id} deleted"}
