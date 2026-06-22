"""Grounding + latency eval runner for the rescue path.

Runs every case in `grounding.jsonl` through the live rescue pipeline and reports
classification accuracy (grounded vs bridge) and latency. Uses whatever provider
is configured: with a GEMINI_API_KEY it is a real eval; without, it runs offline
on the fake embedder/generator.

    ./.venv/Scripts/python.exe tests/eval/run_eval.py

Exits non-zero if accuracy is below the target (default 0.9), so it can gate CI
or a pre-submission check.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path

from cue.config import get_settings
from cue.ingestion.models import DocType, ParsedDocument
from cue.rescue import service

EVAL_PATH = Path(__file__).parent / "grounding.jsonl"
TARGET_ACCURACY = 0.9


def main() -> int:
    # Isolate storage so the eval never touches real data.
    tmp = tempfile.mkdtemp(prefix="cue-eval-")
    os.environ.setdefault("CUE_CHROMA_DIR", os.path.join(tmp, "chroma"))
    os.environ.setdefault("CUE_DB_PATH", os.path.join(tmp, "cue.db"))
    get_settings.cache_clear()

    # Imported after env is set so the store binds to the temp dir.
    from cue.rag import index

    settings = get_settings()
    records = [
        json.loads(line)
        for line in EVAL_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    for i, rec in enumerate(records):
        index.index_document(
            ParsedDocument(
                id=f"e{i}",
                filename=f"e{i}.txt",
                doc_type=DocType.txt,
                char_count=len(rec["doc"]),
                text=rec["doc"],
            )
        )

    print(
        f"provider: emb={settings.active_embeddings_provider} "
        f"gen={settings.active_generation_provider} min_score={settings.rescue_min_score}"
    )
    correct = 0
    latencies: list[float] = []
    for rec in records:
        start = time.perf_counter()
        resp = service.generate_rescue(rec["question"])
        latencies.append(time.perf_counter() - start)
        ok = resp.grounded == rec["expect_grounded"]
        correct += ok
        flag = "OK" if ok else "XX"
        print(
            f"  [{flag}] grounded={str(resp.grounded):5} expect={str(rec['expect_grounded']):5} "
            f"{latencies[-1]:5.2f}s  {rec['id']}"
        )

    n = len(records)
    accuracy = correct / n
    latencies.sort()
    p50 = latencies[len(latencies) // 2]
    p95 = latencies[min(len(latencies) - 1, int(len(latencies) * 0.95))]
    print(f"\nclassification accuracy: {correct}/{n} = {accuracy:.0%}")
    print(f"latency: p50 {p50:.2f}s  p95 {p95:.2f}s  max {latencies[-1]:.2f}s")
    return 0 if accuracy >= TARGET_ACCURACY else 1


if __name__ == "__main__":
    sys.exit(main())
