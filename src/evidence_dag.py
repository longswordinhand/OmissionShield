from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from typing import Iterable, Mapping, Sequence


def _h(data: bytes) -> str:
    return sha256(data).hexdigest()


def merkle_root(ids: Iterable[str]) -> str:
    leaves = [_h(x.encode("utf-8")) for x in sorted(ids)]
    if not leaves:
        return _h(b"")
    while len(leaves) > 1:
        if len(leaves) % 2:
            leaves.append(leaves[-1])
        leaves = [_h((leaves[i] + leaves[i + 1]).encode("ascii")) for i in range(0, len(leaves), 2)]
    return leaves[0]


@dataclass(frozen=True)
class EvidenceNode:
    eid: str
    kind: str  # source | derived
    parents: frozenset[str] = frozenset()
    payload_digest: str = ""


@dataclass(frozen=True)
class DropRecord:
    eid: str
    reason: str
    policy_approved: bool = False


@dataclass
class EvidenceDAG:
    nodes: dict[str, EvidenceNode] = field(default_factory=dict)
    drops: list[DropRecord] = field(default_factory=list)

    def add_source(self, eid: str, payload: str = "") -> None:
        if eid in self.nodes:
            raise ValueError(f"duplicate evidence id {eid}")
        self.nodes[eid] = EvidenceNode(eid=eid, kind="source", payload_digest=_h(payload.encode("utf-8")))

    def add_derived(self, eid: str, parent_ids: Sequence[str], payload: str = "") -> None:
        if eid in self.nodes:
            raise ValueError(f"duplicate evidence id {eid}")
        parents = frozenset(parent_ids)
        unknown = parents - self.nodes.keys()
        if unknown:
            raise ValueError(f"unknown parents: {sorted(unknown)}")
        self.nodes[eid] = EvidenceNode(eid=eid, kind="derived", parents=parents, payload_digest=_h(payload.encode("utf-8")))

    def record_drop(self, eid: str, reason: str, policy_approved: bool = False) -> None:
        if eid not in self.nodes:
            raise ValueError(f"unknown evidence id {eid}")
        self.drops.append(DropRecord(eid=eid, reason=reason, policy_approved=policy_approved))

    def source_closure(self, terminal_ids: Sequence[str]) -> frozenset[str]:
        todo = list(terminal_ids)
        seen: set[str] = set()
        source: set[str] = set()
        while todo:
            eid = todo.pop()
            if eid in seen:
                continue
            seen.add(eid)
            node = self.nodes.get(eid)
            if node is None:
                continue
            if node.kind == "source":
                source.add(eid)
            else:
                todo.extend(node.parents)
        return frozenset(source)


@dataclass(frozen=True)
class CoverageObligation:
    task_id: str
    required_source_ids: frozenset[str]
    source_root: str

    @classmethod
    def from_source_ids(cls, task_id: str, ids: Sequence[str]) -> "CoverageObligation":
        s = frozenset(ids)
        return cls(task_id=task_id, required_source_ids=s, source_root=merkle_root(s))


@dataclass(frozen=True)
class GateDecision:
    allow: bool
    missing_ids: frozenset[str]
    approved_drop_ids: frozenset[str]
    reason: str


def why_not_gate(
    dag: EvidenceDAG,
    obligation: CoverageObligation,
    terminal_ids: Sequence[str],
    observed_source_root: str,
) -> GateDecision:
    if observed_source_root != obligation.source_root:
        return GateDecision(False, obligation.required_source_ids, frozenset(), "SOURCE_COMMITMENT_MISMATCH")
    covered = dag.source_closure(terminal_ids)
    missing = obligation.required_source_ids - covered
    approved = frozenset(d.eid for d in dag.drops if d.policy_approved)
    unapproved_missing = missing - approved
    if unapproved_missing:
        return GateDecision(False, frozenset(unapproved_missing), approved, "SILENT_REQUIRED_EVIDENCE_OMISSION")
    return GateDecision(True, frozenset(), approved, "COVERAGE_SATISFIED")
