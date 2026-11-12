from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import hmac
import json
from typing import Iterable, Sequence

from src.evidence_dag import CoverageObligation, EvidenceDAG, GateDecision, why_not_gate


def _canon(ids: Iterable[str]) -> bytes:
    return json.dumps(sorted(ids), separators=(",", ":")).encode("utf-8")


@dataclass(frozen=True)
class SignedObligation:
    task_id: str
    required_ids: tuple[str, ...]
    source_root: str
    signature: str


@dataclass(frozen=True)
class SignedDropAuthorization:
    task_id: str
    evidence_id: str
    source_root: str
    principal: str
    reason: str
    nonce: str
    signature: str


class TrustedEvidenceRuntime:
    """Small trusted control plane.

    Models and untrusted orchestration never write provenance edges. The runtime
    records source enumeration and actual handle delivery at transformation
    boundaries. This proves structural transfer only, not semantic use.
    """

    def __init__(self, key: bytes, drop_key: bytes | None = None):
        self._key = key
        self._drop_key = drop_key if drop_key is not None else key
        self.dag = EvidenceDAG()
        self._obligations: dict[str, SignedObligation] = {}
        self._delivered_to_stage: dict[str, tuple[str, ...]] = {}
        self._used_drop_nonces: set[tuple[str, str]] = set()

    def enumerate_source(self, task_id: str, items: Sequence[tuple[str, str]]) -> SignedObligation:
        ids = tuple(eid for eid, _ in items)
        obligation = CoverageObligation.from_source_ids(task_id, ids)
        sig = hmac.new(self._key, task_id.encode() + b"\0" + _canon(ids) + b"\0" + obligation.source_root.encode(), sha256).hexdigest()
        signed = SignedObligation(task_id, ids, obligation.source_root, sig)
        self._obligations[task_id] = signed
        for eid, payload in items:
            self.dag.add_source(eid, payload)
        return signed

    def verify_obligation(self, signed: SignedObligation) -> bool:
        expected = hmac.new(self._key, signed.task_id.encode() + b"\0" + _canon(signed.required_ids) + b"\0" + signed.source_root.encode(), sha256).hexdigest()
        return hmac.compare_digest(expected, signed.signature)

    def issue_drop_authorization(
        self,
        signed: SignedObligation,
        evidence_id: str,
        principal: str,
        reason: str,
        nonce: str,
    ) -> SignedDropAuthorization:
        if not self.verify_obligation(signed):
            raise ValueError("invalid obligation")
        if evidence_id not in signed.required_ids:
            raise ValueError(f"evidence {evidence_id} is not required by task {signed.task_id}")
        msg = b"\0".join([
            signed.task_id.encode(),
            evidence_id.encode(),
            signed.source_root.encode(),
            principal.encode(),
            reason.encode(),
            nonce.encode(),
        ])
        sig = hmac.new(self._drop_key, msg, sha256).hexdigest()
        return SignedDropAuthorization(
            signed.task_id,
            evidence_id,
            signed.source_root,
            principal,
            reason,
            nonce,
            sig,
        )

    def verify_drop_authorization(
        self,
        signed: SignedObligation,
        auth: SignedDropAuthorization,
    ) -> bool:
        if not self.verify_obligation(signed):
            return False
        if auth.task_id != signed.task_id or auth.source_root != signed.source_root:
            return False
        if auth.evidence_id not in signed.required_ids:
            return False
        msg = b"\0".join([
            auth.task_id.encode(),
            auth.evidence_id.encode(),
            auth.source_root.encode(),
            auth.principal.encode(),
            auth.reason.encode(),
            auth.nonce.encode(),
        ])
        expected = hmac.new(self._drop_key, msg, sha256).hexdigest()
        return hmac.compare_digest(expected, auth.signature)

    def apply_drop_authorization(
        self,
        signed: SignedObligation,
        auth: SignedDropAuthorization,
    ) -> None:
        if not self.verify_drop_authorization(signed, auth):
            raise ValueError("invalid drop authorization")
        replay_key = (auth.task_id, auth.nonce)
        if replay_key in self._used_drop_nonces:
            raise ValueError("replayed drop authorization")
        self._used_drop_nonces.add(replay_key)
        self.dag.record_drop(
            auth.evidence_id,
            f"{auth.principal}: {auth.reason}",
            policy_approved=True,
        )

    def deliver(self, stage_id: str, handles: Sequence[str]) -> tuple[str, ...]:
        # The runtime records what actually crossed the stage boundary.
        for h in handles:
            if h not in self.dag.nodes:
                raise ValueError(f"unknown handle {h}")
        actual = tuple(handles)
        self._delivered_to_stage[stage_id] = actual
        return actual

    def commit_derived(self, stage_id: str, output_handle: str, payload: str) -> str:
        # Parent edges come from runtime-observed delivery, not model output.
        parents = self._delivered_to_stage.get(stage_id)
        if parents is None:
            raise ValueError(f"no runtime delivery recorded for {stage_id}")
        self.dag.add_derived(output_handle, parents, payload)
        return output_handle

    def gate(self, signed: SignedObligation, terminal_handles: Sequence[str]) -> GateDecision:
        if not self.verify_obligation(signed):
            return GateDecision(False, frozenset(signed.required_ids), frozenset(), "INVALID_SOURCE_SIGNATURE")
        obligation = CoverageObligation(signed.task_id, frozenset(signed.required_ids), signed.source_root)
        return why_not_gate(self.dag, obligation, terminal_handles, signed.source_root)
