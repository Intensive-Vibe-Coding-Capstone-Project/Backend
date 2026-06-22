"""SQLite-backed session/turn store (stdlib `sqlite3`, no extra deps).

Connections are short-lived (one per call) so the store is safe to use from
FastAPI's threadpool. `get_store()` is cached per db path; tests point
`CUE_DB_PATH` at a temp file and call `reset_cache()`.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from functools import lru_cache
from pathlib import Path

from cue.config import Settings, get_settings
from cue.rescue.models import Citation
from cue.sessions.models import PreparedScript, Session, SessionMeta, Turn, now_iso

_SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id              TEXT PRIMARY KEY,
    title           TEXT,
    created_at      TEXT NOT NULL,
    prepared_script TEXT,
    forbidden_terms TEXT
);
CREATE TABLE IF NOT EXISTS turns (
    id         TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    seq        INTEGER NOT NULL,
    question   TEXT NOT NULL,
    script     TEXT NOT NULL,
    lines      TEXT NOT NULL,
    grounded   INTEGER NOT NULL,
    citations  TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions (id)
);
CREATE INDEX IF NOT EXISTS idx_turns_session ON turns (session_id, seq);
"""


class SessionStore:
    """Persists sessions and their ordered turns in SQLite."""

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        parent = Path(db_path).parent
        if str(parent) not in ("", "."):
            parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript(_SCHEMA)
            # Migrate pre-existing tables that lack the D10 columns.
            for column in ("prepared_script TEXT", "forbidden_terms TEXT"):
                try:
                    conn.execute(f"ALTER TABLE sessions ADD COLUMN {column}")
                except sqlite3.OperationalError:
                    pass  # column already exists

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_session(self, title: str | None = None) -> Session:
        session = Session(id=uuid.uuid4().hex, title=title, created_at=now_iso())
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO sessions (id, title, created_at) VALUES (?, ?, ?)",
                (session.id, session.title, session.created_at),
            )
        return session

    def get_session(self, session_id: str) -> Session | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, title, created_at FROM sessions WHERE id = ?", (session_id,)
            ).fetchone()
        return Session(**row) if row else None

    def session_exists(self, session_id: str) -> bool:
        with self._connect() as conn:
            row = conn.execute("SELECT 1 FROM sessions WHERE id = ?", (session_id,)).fetchone()
        return row is not None

    def list_sessions(self) -> list[SessionMeta]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT s.id, s.title, s.created_at,
                       (SELECT COUNT(*) FROM turns t WHERE t.session_id = s.id) AS turn_count
                FROM sessions s
                ORDER BY s.created_at DESC
                """
            ).fetchall()
        return [SessionMeta(**row) for row in rows]

    def add_turn(
        self,
        session_id: str,
        question: str,
        script: str,
        lines: list[str],
        grounded: bool,
        citations: list[Citation],
        turn_id: str | None = None,
    ) -> Turn:
        turn = Turn(
            id=turn_id or uuid.uuid4().hex,
            session_id=session_id,
            question=question,
            script=script,
            lines=lines,
            grounded=grounded,
            citations=citations,
            created_at=now_iso(),
        )
        with self._connect() as conn:
            seq = conn.execute(
                "SELECT COALESCE(MAX(seq), 0) + 1 FROM turns WHERE session_id = ?",
                (session_id,),
            ).fetchone()[0]
            conn.execute(
                """
                INSERT INTO turns
                    (id, session_id, seq, question, script, lines, grounded, citations, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    turn.id,
                    session_id,
                    seq,
                    question,
                    script,
                    json.dumps(lines),
                    int(grounded),
                    json.dumps([c.model_dump() for c in citations]),
                    turn.created_at,
                ),
            )
        return turn

    def set_prepared_script(self, session_id: str, script: PreparedScript) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE sessions SET prepared_script = ?, forbidden_terms = ? WHERE id = ?",
                (script.text, json.dumps(script.forbidden_terms), session_id),
            )

    def get_prepared_script(self, session_id: str) -> PreparedScript | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT prepared_script, forbidden_terms FROM sessions WHERE id = ?",
                (session_id,),
            ).fetchone()
        if not row or row["prepared_script"] is None:
            return None
        terms = json.loads(row["forbidden_terms"]) if row["forbidden_terms"] else []
        return PreparedScript(text=row["prepared_script"], forbidden_terms=terms)

    def get_turns(self, session_id: str) -> list[Turn]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, session_id, question, script, lines, grounded, citations, created_at
                FROM turns WHERE session_id = ? ORDER BY seq
                """,
                (session_id,),
            ).fetchall()
        return [
            Turn(
                id=row["id"],
                session_id=row["session_id"],
                question=row["question"],
                script=row["script"],
                lines=json.loads(row["lines"]),
                grounded=bool(row["grounded"]),
                citations=[Citation(**c) for c in json.loads(row["citations"])],
                created_at=row["created_at"],
            )
            for row in rows
        ]


@lru_cache
def _build_store(db_path: str) -> SessionStore:
    return SessionStore(db_path)


def get_store(settings: Settings | None = None) -> SessionStore:
    """Return the cached session store for the configured db path."""
    settings = settings or get_settings()
    return _build_store(settings.db_path)


def reset_cache() -> None:
    """Drop cached stores (used by tests between temp db files)."""
    _build_store.cache_clear()
