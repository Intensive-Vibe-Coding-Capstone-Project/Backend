"""Transcript pipeline: streaming STT -> rolling per-session buffer.

Timestamps support windowing + silence detection. Lands D8.
"""
