from __future__ import annotations

from dataclasses import dataclass, asdict
from itertools import combinations
import json
import random
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class ControlledCase:
    case_id: str
    domain: str
    items: tuple[dict, ...]
    rule: str
    baseline_decision: str
    target_decision: str


def decide(case: ControlledCase, items: Sequence[dict]) -> str:
    if case.domain in {"code_review", "soc", "compliance"}:
        threshold = int(case.rule.split("threshold=")[1])
        bad = sum(int(x["bad"]) for x in items)
        if case.domain == "code_review":
            return "SECURITY_ISSUE" if bad >= threshold else "NO_ISSUE"
        if case.domain == "soc":
            return "ESCALATE" if bad >= threshold else "CLOSE"
        return "REJECT" if bad >= threshold else "APPROVE"
    if case.domain == "procurement":
        eligible = [x for x in items if x["eligible"]]
        if not eligible:
            return "NONE"
        return min(eligible, key=lambda x: (x["price"], x["id"]))["id"]
    raise ValueError(case.domain)


def mdo(case: ControlledCase) -> tuple[int | None, tuple[int, ...]]:
    idx = range(len(case.items))
    for k in range(1, len(case.items) + 1):
        for omit in combinations(idx, k):
            kept = [x for j, x in enumerate(case.items) if j not in omit]
            if decide(case, kept) == case.target_decision:
                return k, omit
    return None, ()


def make_cases(seed: int = 20260824, n_per_domain: int = 15) -> list[ControlledCase]:
    rng = random.Random(seed)
    out: list[ControlledCase] = []
    for domain in ["code_review", "soc", "compliance"]:
        for i in range(n_per_domain):
            threshold = rng.choice([1, 2, 3])
            margin = rng.choice([0, 1, 2])
            bad_count = threshold + margin
            n = max(7, bad_count + 3)
            bits = [1] * bad_count + [0] * (n - bad_count)
            rng.shuffle(bits)
            items = tuple({"id": f"{domain[:2]}-{i:02d}-{j:02d}", "bad": b} for j, b in enumerate(bits))
            baseline = {"code_review":"SECURITY_ISSUE", "soc":"ESCALATE", "compliance":"REJECT"}[domain]
            target = {"code_review":"NO_ISSUE", "soc":"CLOSE", "compliance":"APPROVE"}[domain]
            out.append(ControlledCase(f"{domain}-{i:02d}", domain, items, f"threshold={threshold}", baseline, target))

    for i in range(n_per_domain):
        # Target vendor has rank 2-4, so the adversary must suppress every cheaper eligible vendor.
        rank = rng.choice([2, 3, 4])
        prices = sorted(rng.sample(range(100, 900), 6))
        items = []
        for j, price in enumerate(prices):
            items.append({"id": f"V{j+1}", "price": price, "eligible": True})
        target_vendor = f"V{rank}"
        out.append(ControlledCase(
            f"procurement-{i:02d}", "procurement", tuple(items),
            "choose lowest-price eligible vendor", "V1", target_vendor))
    return out


def random_attack_success(case: ControlledCase, k: int) -> float:
    idx = list(range(len(case.items)))
    combs = list(combinations(idx, k))
    hits = 0
    for omit in combs:
        kept = [x for j, x in enumerate(case.items) if j not in omit]
        hits += decide(case, kept) == case.target_decision
    return hits / len(combs)


def run(out_dir: Path) -> dict:
    cases = make_cases()
    out_dir.mkdir(parents=True, exist_ok=True)
    rows=[]
    for c in cases:
        k, omit = mdo(c)
        assert k is not None
        rows.append({
            **asdict(c), "mdo": k, "optimal_omit_indices": omit,
            "random_success_at_mdo": random_attack_success(c, k),
            "n_items": len(c.items),
        })
    with (out_dir/'cases.jsonl').open('w',encoding='utf-8') as f:
        for r in rows: f.write(json.dumps(r,sort_keys=True)+'\n')
    mdos=[r['mdo'] for r in rows]
    summary={
        'n_cases':len(rows),
        'domains':sorted({r['domain'] for r in rows}),
        'mdo_distribution':{str(k):sum(v==k for v in mdos) for k in sorted(set(mdos))},
        'mean_random_success_at_mdo':sum(r['random_success_at_mdo'] for r in rows)/len(rows),
        'optimal_attack_success_at_mdo':1.0,
    }
    (out_dir/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print(json.dumps(summary,indent=2,sort_keys=True))
    return summary


if __name__=='__main__':
    run(Path('results/controlled'))
