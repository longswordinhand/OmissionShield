from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess

from src.evidence_dag import CoverageObligation, EvidenceDAG, why_not_gate


@dataclass(frozen=True)
class GitEvidenceResult:
    changed_files: tuple[str, ...]
    delivered_files: tuple[str, ...]
    allow: bool
    missing_files: tuple[str, ...]
    source_root: str


def _git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def changed_files(repo: Path, base: str, head: str) -> tuple[str, ...]:
    out = _git(repo, "diff", "--name-only", base, head)
    return tuple(x for x in out.splitlines() if x)


def audit_delivery(repo: Path, base: str, head: str, delivered_files: tuple[str, ...]) -> GitEvidenceResult:
    expected = changed_files(repo, base, head)
    obligation = CoverageObligation.from_source_ids(f"git:{base}..{head}", expected)
    dag = EvidenceDAG()
    for path in expected:
        blob = _git(repo, "show", f"{head}:{path}")
        dag.add_source(path, payload=blob)
    if delivered_files:
        dag.add_derived("review-context", delivered_files, payload="rendered review context")
        terminal = ["review-context"]
    else:
        terminal = []
    decision = why_not_gate(dag, obligation, terminal, obligation.source_root)
    return GitEvidenceResult(
        changed_files=expected,
        delivered_files=delivered_files,
        allow=decision.allow,
        missing_files=tuple(sorted(decision.missing_ids)),
        source_root=obligation.source_root,
    )
