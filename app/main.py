"""
AI-Powered Presentation Assistant — Main Application

FastAPI application with:
- REST API for documents, chat, and voice
- WebSocket for real-time communication
- Gemini-powered RAG pipeline for document-grounded answers
- Signal detection for presentation assistance
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api.routes import documents, chat, voice
from app.api.websocket import websocket_endpoint
from app.models.schemas import HealthCheckResponse
from app.services.rag.engine import rag_engine
from app.agents.orchestrator import agent_orchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    settings = get_settings()
    logger.info("=" * 60)
    logger.info(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"   Environment: {settings.app_env}")
    logger.info(f"   Debug: {settings.debug}")
    logger.info(f"   Gemini Model: {settings.gemini_model}")
    logger.info("=" * 60)

    # Initialize services
    try:
        await rag_engine.initialize()
        logger.info("✅ RAG engine initialized")
    except Exception as e:
        logger.warning(f"⚠️  RAG engine initialization failed: {e}")

    try:
        await agent_orchestrator.initialize()
        logger.info("✅ Agent orchestrator initialized")
    except Exception as e:
        logger.warning(f"⚠️  Agent orchestrator initialization failed: {e}")

    logger.info("🎯 Application ready to serve requests")

    yield  # Application runs here

    logger.info("👋 Shutting down...")


# ── Create FastAPI Application ───────────────────────────────

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "AI-powered presentation assistant that helps users answer "
        "unexpected questions during presentations using uploaded documents "
        "and real-time voice/text analysis."
    ),
    lifespan=lifespan,
)

# ── CORS Middleware ──────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Routes ───────────────────────────────────────────────

app.include_router(documents.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(voice.router, prefix="/api/v1")

# ── WebSocket ────────────────────────────────────────────────

app.websocket("/ws")(websocket_endpoint)

# ── Health Check ─────────────────────────────────────────────


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint — redirects to docs."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring."""
    rag_stats = {}
    try:
        rag_stats = await rag_engine.get_stats()
        rag_status = "healthy"
    except Exception:
        rag_status = "unavailable"

    services = {
        "rag_engine": rag_status,
        "agent_orchestrator": "healthy" if agent_orchestrator._initialized else "not_initialized",
        "chromadb_chunks": str(rag_stats.get("total_chunks", 0)),
    }

    # Check Gemini API key
    if settings.google_api_key:
        services["gemini_api"] = "configured"
    else:
        services["gemini_api"] = "not_configured (mock mode)"

    return HealthCheckResponse(
        status="healthy",
        version=settings.app_version,
        environment=settings.app_env,
        services=services,
    )
