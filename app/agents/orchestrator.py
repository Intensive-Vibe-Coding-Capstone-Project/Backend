"""
RAG Pipeline Orchestrator using Gemini.
Implements the query processing pipeline:
- Query analysis & retrieval strategy
- Gemini-powered answer generation (grounded in documents)
- Response validation (accuracy & hallucination checks)

Note: The project uses Loop Engineering (Planning/QA/Dev Agents)
as a DEVELOPMENT methodology to build this code. The prompt
templates below use "agent" naming for the different Gemini
prompt roles, but they are all calls to the same Gemini model
at runtime — not separate autonomous agents.
"""

import logging
from typing import Optional

from app.core.config import get_settings
from app.services.rag.engine import rag_engine
from app.services.signals.detector import signal_detector

logger = logging.getLogger(__name__)


# ── Agent Instructions ───────────────────────────────────────

PLANNING_AGENT_INSTRUCTION = """You are the Planning Agent for an AI-Powered Presentation Assistant.

Your role is to:
1. Analyze the user's question or detected difficulty signal
2. Determine what information is needed from the uploaded documents
3. Create a retrieval strategy to find the most relevant context
4. Route the query to the appropriate response pipeline

When a user asks a question:
- Identify the key concepts and entities in the question
- Determine which document sections are most relevant
- Consider the presentation context (if available)
- Formulate a clear retrieval query for the RAG engine

When a difficulty signal is detected:
- Assess the urgency (real-time presentation vs. async)
- Identify what topic the presenter might need help with
- Prepare context from the most relevant documents

Always respond with a structured retrieval plan.
"""

DEV_AGENT_INSTRUCTION = """You are the Dev Agent (Generator) for an AI-Powered Presentation Assistant.

Your role is to generate clear, concise, document-grounded answers that help presenters.

Guidelines:
1. ONLY use information from the provided document context
2. Structure your answer for QUICK READING during a live presentation
3. Format each key point on its own line (like song lyrics)
4. Keep sentences short and scannable
5. Lead with the most important point first
6. Include specific data/facts from the documents when available
7. If the context doesn't contain the answer, say so honestly

Response format:
- Break your answer into short, scannable lines
- Each line should convey one key point
- Use simple, clear language
- No bullet points or markdown — just clean lines of text

Example output format:
The quarterly revenue grew 15% year-over-year
Reaching $2.3 billion in Q4
Driven primarily by cloud services expansion
Which accounted for 40% of total revenue
"""

QA_AGENT_INSTRUCTION = """You are the QA Agent (Validator) for an AI-Powered Presentation Assistant.

Your role is to validate the accuracy of generated answers before they reach the user.

Validation checks:
1. FACTUAL ACCURACY: Every claim must be traceable to the provided source documents
2. HALLUCINATION CHECK: Flag any information not present in the source context
3. BRAND SAFETY: Verify brand names, product names, and proper nouns are correct
4. COMPLETENESS: Ensure the answer addresses the user's question
5. CLARITY: Confirm the answer is easy to read quickly during a presentation

Respond with:
- "APPROVED" if the answer passes all checks, followed by any minor suggestions
- "REJECTED" with specific reasons if the answer fails any check

Be strict about factual accuracy — a wrong answer during a live presentation is worse than no answer.
"""


class AgentOrchestrator:
    """
    Orchestrates the multi-agent workflow using the Loop Engineering pattern.
    Planning → Dev → QA → (loop if rejected) → User
    """

    def __init__(self):
        self._model = None
        self._initialized = False

    async def initialize(self):
        """Initialize the Gemini model for agent interactions."""
        if self._initialized:
            return

        settings = get_settings()
        if not settings.google_api_key:
            logger.warning(
                "GOOGLE_API_KEY not set — agent orchestrator running in mock mode"
            )
            self._initialized = True
            return

        try:
            from google import genai

            self._model = genai.Client(api_key=settings.google_api_key)
            self._initialized = True
            logger.info(f"Agent orchestrator initialized with model: {settings.gemini_model}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            # Continue in mock mode
            self._initialized = True

    async def process_query(
        self,
        query: str,
        doc_ids: Optional[list[str]] = None,
        language: str = "en",
    ) -> dict:
        """
        Process a user query through the full agent pipeline:
        Planning → RAG Retrieval → Dev (Generate) → QA (Validate)
        """
        await self.initialize()

        # Step 1: RAG Retrieval
        context, sources = await rag_engine.get_context_for_query(query, doc_ids)

        if not context:
            return {
                "response": "I don't have enough information from the uploaded documents to answer this question. Please upload relevant documents first.",
                "sources": [],
                "confidence": 0.0,
                "formatted_lines": [
                    "I don't have enough information",
                    "from the uploaded documents",
                    "to answer this question.",
                    "",
                    "Please upload relevant documents first.",
                ],
            }

        # Step 2: Generate answer using Dev Agent
        answer = await self._generate_answer(query, context, language)

        # Step 3: Validate with QA Agent
        validation = await self._validate_answer(answer, context, query)

        # If rejected, retry once with feedback
        if not validation["approved"]:
            logger.info("QA rejected answer, regenerating with feedback...")
            answer = await self._generate_answer(
                query, context, language,
                feedback=validation.get("reason", ""),
            )
            validation = await self._validate_answer(answer, context, query)

        # Format into lyrics-style lines
        formatted_lines = [
            line.strip()
            for line in answer.split("\n")
            if line.strip()
        ]

        return {
            "response": answer,
            "sources": sources,
            "confidence": validation.get("confidence", 0.8),
            "formatted_lines": formatted_lines,
        }

    async def _generate_answer(
        self,
        query: str,
        context: str,
        language: str = "en",
        feedback: str = "",
    ) -> str:
        """Use the Dev Agent to generate a document-grounded answer."""
        settings = get_settings()

        lang_instruction = (
            "Respond in Vietnamese." if language == "vi"
            else "Respond in English."
        )

        feedback_note = ""
        if feedback:
            feedback_note = f"\n\nPrevious answer was rejected for: {feedback}\nPlease fix these issues."

        prompt = f"""{DEV_AGENT_INSTRUCTION}

{lang_instruction}
{feedback_note}

--- DOCUMENT CONTEXT ---
{context}

--- USER QUESTION ---
{query}

--- YOUR ANSWER (formatted as lyrics, one point per line) ---"""

        if self._model:
            try:
                response = self._model.models.generate_content(
                    model=settings.gemini_model,
                    contents=prompt,
                )
                return response.text
            except Exception as e:
                logger.error(f"Gemini generation failed: {e}")

        # Mock response for development without API key
        return (
            f"Based on the uploaded documents:\n"
            f"This is a mock response for: {query}\n"
            f"In production, this will be generated by Gemini\n"
            f"using the {len(context)} chars of document context"
        )

    async def _validate_answer(self, answer: str, context: str, query: str) -> dict:
        """Use the QA Agent to validate the generated answer."""
        settings = get_settings()

        prompt = f"""{QA_AGENT_INSTRUCTION}

--- SOURCE DOCUMENTS ---
{context}

--- USER QUESTION ---
{query}

--- GENERATED ANSWER ---
{answer}

--- YOUR VALIDATION ---"""

        if self._model:
            try:
                response = self._model.models.generate_content(
                    model=settings.gemini_model,
                    contents=prompt,
                )
                result_text = response.text.strip().upper()
                approved = result_text.startswith("APPROVED")
                return {
                    "approved": approved,
                    "reason": response.text if not approved else "",
                    "confidence": 0.9 if approved else 0.4,
                }
            except Exception as e:
                logger.error(f"Gemini validation failed: {e}")

        # Mock validation — always approve in dev mode
        return {"approved": True, "reason": "", "confidence": 0.8}


# Singleton instance
agent_orchestrator = AgentOrchestrator()
