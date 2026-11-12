from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Iterable, Sequence


@dataclass(frozen=True)
class EvidenceObligation:
    task_id: str
    required_ids: frozenset[str]
    source_manifest_root: str


@dataclass(frozen=True)
class CoverageCertificate:
    delivered_ids: frozenset[str]
    source_manifest_root: str


def set_commitment(ids: Iterable[str]) -> str:
    canonical = "\n".join(sorted(ids)).encode("utf-8")
    return sha256(canonical).hexdigest()


def make_obligation(task_id: str, required_ids: Sequence[str]) -> EvidenceObligation:
    req = frozenset(required_ids)
    return EvidenceObligation(task_id, req, set_commitment(req))


def certify_delivery(delivered_ids: Sequence[str], source_manifest_root: str) -> CoverageCertificate:
    return CoverageCertificate(frozenset(delivered_ids), source_manifest_root)


def why_not_gate(obligation: EvidenceObligation, cert: CoverageCertificate) -> tuple[bool, frozenset[str]]:
    if cert.source_manifest_root != obligation.source_manifest_root:
        return False, obligation.required_ids
    missing = obligation.required_ids - cert.delivered_ids
    return not missing, missing


def positive_provenance_gate(delivered_ids: Sequence[str], valid_ids: Sequence[str]) -> bool:
    """A positive-provenance abstraction: every observed item has valid ancestry."""
    return set(delivered_ids).issubset(set(valid_ids))


def ifc_label_gate(delivered_ids: Sequence[str], labelled_ids: Sequence[str]) -> bool:
    """A Fides-style abstraction: every observed item has an integrity label.

    This intentionally does not claim to reimplement Fides. It isolates the
    information available to any gate that only validates labels on observed
    values and has no independent obligation over the source result set.
    """
    return set(delivered_ids).issubset(set(labelled_ids))
