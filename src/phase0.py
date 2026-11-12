from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
from itertools import combinations
import json
import random
from pathlib import Path
from typing import Callable, Iterable, Sequence


@dataclass(frozen=True)
class Evidence:
    eid: str
    domain: str
    payload: dict


@dataclass
class TaskCase:
    case_id: str
    domain: str
    evidence: list[Evidence]
    required_ids: list[str]
    decision_rule_name: str
    baseline_decision: str


@dataclass
class AttackResult:
    case_id: str
    domain: str
    omitted_ids: list[str]
    attacked_decision: str
    baseline_decision: str
    decision_flipped: bool
    coverage_ok: bool
    whynot_detected: bool


def manifest_root(ids: Iterable[str]) -> str:
    canonical = "\n".join(sorted(ids)).encode("utf-8")
    return sha256(canonical).hexdigest()


def whynot_gate(required_ids: Sequence[str], delivered_ids: Sequence[str]) -> bool:
    """Return True only if all structurally required IDs are delivered."""
    return set(required_ids).issubset(set(delivered_ids))


def code_review_decision(evidence: Sequence[Evidence]) -> str:
    risky = any(bool(e.payload.get("security_issue")) for e in evidence)
    return "SECURITY_ISSUE" if risky else "NO_ISSUE"


def soc_decision(evidence: Sequence[Evidence]) -> str:
    score = sum(int(e.payload.get("severity", 0)) for e in evidence)
    c2 = any(bool(e.payload.get("c2_indicator")) for e in evidence)
    return "ESCALATE" if c2 or score >= 8 else "CLOSE"


def decision_fn(domain: str) -> Callable[[Sequence[Evidence]], str]:
    if domain == "code_review":
        return code_review_decision
    if domain == "soc":
        return soc_decision
    raise ValueError(domain)


def make_cases(seed: int = 20260824, n_per_domain: int = 12) -> list[TaskCase]:
    rng = random.Random(seed)
    cases: list[TaskCase] = []

    for idx in range(n_per_domain):
        n_files = rng.randint(5, 9)
        risky_index = rng.randrange(n_files)
        evidence = []
        for j in range(n_files):
            evidence.append(Evidence(
                eid=f"CR-{idx:02d}-F{j:02d}",
                domain="code_review",
                payload={"path": f"file_{j}.py", "security_issue": j == risky_index},
            ))
        baseline = code_review_decision(evidence)
        ids = [e.eid for e in evidence]
        cases.append(TaskCase(
            case_id=f"CR-{idx:02d}", domain="code_review", evidence=evidence,
            required_ids=ids, decision_rule_name="flag_if_any_changed_file_has_security_issue",
            baseline_decision=baseline,
        ))

    for idx in range(n_per_domain):
        n_alerts = rng.randint(6, 10)
        decisive_index = rng.randrange(n_alerts)
        evidence = []
        base_severities = [rng.randint(0, 2) for _ in range(n_alerts)]
        # Keep aggregate score below escalation threshold unless decisive C2 alert is present.
        while sum(base_severities) >= 8:
            base_severities[rng.randrange(n_alerts)] = 0
        for j in range(n_alerts):
            evidence.append(Evidence(
                eid=f"SOC-{idx:02d}-A{j:02d}",
                domain="soc",
                payload={"severity": base_severities[j], "c2_indicator": j == decisive_index},
            ))
        baseline = soc_decision(evidence)
        ids = [e.eid for e in evidence]
        cases.append(TaskCase(
            case_id=f"SOC-{idx:02d}", domain="soc", evidence=evidence,
            required_ids=ids, decision_rule_name="escalate_if_c2_or_total_severity_ge_8",
            baseline_decision=baseline,
        ))

    return cases


def evaluate_omission(case: TaskCase, omitted_ids: Sequence[str]) -> AttackResult:
    omitted = set(omitted_ids)
    delivered = [e for e in case.evidence if e.eid not in omitted]
    fn = decision_fn(case.domain)
    attacked = fn(delivered)
    delivered_ids = [e.eid for e in delivered]
    coverage_ok = whynot_gate(case.required_ids, delivered_ids)
    return AttackResult(
        case_id=case.case_id,
        domain=case.domain,
        omitted_ids=list(omitted_ids),
        attacked_decision=attacked,
        baseline_decision=case.baseline_decision,
        decision_flipped=attacked != case.baseline_decision,
        coverage_ok=coverage_ok,
        whynot_detected=not coverage_ok,
    )


def minimal_decisive_omission(case: TaskCase, max_k: int = 3) -> tuple[int | None, list[str]]:
    ids = [e.eid for e in case.evidence]
    for k in range(1, min(max_k, len(ids)) + 1):
        for subset in combinations(ids, k):
            res = evaluate_omission(case, subset)
            if res.decision_flipped:
                return k, list(subset)
    return None, []


def run(out_dir: Path, seed: int = 20260824) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    cases = make_cases(seed=seed)
    rows = []
    mdo_rows = []

    for case in cases:
        # benign complete run
        rows.append(asdict(evaluate_omission(case, [])))

        mdo_k, mdo_ids = minimal_decisive_omission(case)
        mdo_rows.append({
            "case_id": case.case_id,
            "domain": case.domain,
            "mdo": mdo_k,
            "mdo_ids": mdo_ids,
            "n_required": len(case.required_ids),
            "manifest_root": manifest_root(case.required_ids),
        })
        if mdo_ids:
            rows.append(asdict(evaluate_omission(case, mdo_ids)))

        # one deterministic non-decisive omission when possible
        decisive = set(mdo_ids)
        candidate = next((eid for eid in case.required_ids if eid not in decisive), None)
        if candidate is not None:
            rows.append(asdict(evaluate_omission(case, [candidate])))

    with (out_dir / "phase0_results.jsonl").open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")
    with (out_dir / "mdo.jsonl").open("w", encoding="utf-8") as f:
        for row in mdo_rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")

    decisive = [r for r in rows if r["omitted_ids"] and r["decision_flipped"]]
    benign = [r for r in rows if not r["omitted_ids"]]
    attacked = [r for r in rows if r["omitted_ids"]]
    mdo_vals = [r["mdo"] for r in mdo_rows if r["mdo"] is not None]
    summary = {
        "seed": seed,
        "n_cases": len(cases),
        "domains": sorted({c.domain for c in cases}),
        "n_attack_trials": len(attacked),
        "n_decision_flips": len(decisive),
        "decision_flip_rate_among_attack_trials": len(decisive) / len(attacked) if attacked else 0.0,
        "median_mdo": sorted(mdo_vals)[len(mdo_vals)//2] if mdo_vals else None,
        "fraction_mdo_1": sum(v == 1 for v in mdo_vals) / len(mdo_vals) if mdo_vals else 0.0,
        "whynot_detection_on_any_omission": sum(r["whynot_detected"] for r in attacked) / len(attacked) if attacked else 0.0,
        "false_positive_on_complete_runs": sum(r["whynot_detected"] for r in benign) / len(benign) if benign else 0.0,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(run(Path("results/phase0")), indent=2, sort_keys=True))
