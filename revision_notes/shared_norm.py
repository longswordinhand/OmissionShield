"""Audit-only unified label parser for OmissionShield Phase 1.

This module is staged in revision_2026-11-10 only. It does not modify the
frozen experiment code. A response is parseable only when exactly one of the
allowed labels occurs as a whole token; zero or multiple matches return
UNPARSEABLE so label-order priority cannot silently decide ambiguous output.
"""
from __future__ import annotations
import re
from collections.abc import Sequence


def normalize_label(text: str, allowed_labels: Sequence[str]) -> str:
    up = text.upper()
    hits = [
        label
        for label in allowed_labels
        if re.search(rf"\b{re.escape(label.upper())}\b", up)
    ]
    return hits[0] if len(hits) == 1 else "UNPARSEABLE"
