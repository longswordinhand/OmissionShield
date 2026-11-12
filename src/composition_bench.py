from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path

from src.runtime import TrustedEvidenceRuntime

KEY = b"omissionshield-composition-benchmark-key"


def _chunks(xs: list[str], k: int) -> list[list[str]]:
    return [xs[i:i+k] for i in range(0, len(xs), k)]


def build_tree(n_sources: int, fanin: int = 4, attack_layer: int | None = None):
    rt = TrustedEvidenceRuntime(KEY)
    items = [(f"src:{i:05d}", f"payload-{i}") for i in range(n_sources)]
    obligation = rt.enumerate_source("task", items)
    handles = [eid for eid, _ in items]
    lineage = {h: frozenset([h]) for h in handles}
    layer = 0
    omitted_handle = None
    expected_missing = frozenset()

    while len(handles) > 1:
        next_handles: list[str] = []
        groups = _chunks(handles, fanin)
        for gi, group in enumerate(groups):
            delivered = list(group)
            if attack_layer == layer and omitted_handle is None and len(delivered) > 1:
                omitted_handle = delivered.pop(0)
                expected_missing = lineage[omitted_handle]
            stage_id = f"L{layer}:G{gi}"
            out = f"node:L{layer}:G{gi}"
            rt.deliver(stage_id, delivered)
            rt.commit_derived(stage_id, out, f"summary layer={layer} group={gi}")
            union = frozenset().union(*(lineage[h] for h in delivered)) if delivered else frozenset()
            lineage[out] = union
            next_handles.append(out)
        handles = next_handles
        layer += 1

    t0 = time.perf_counter_ns()
    decision = rt.gate(obligation, handles)
    gate_us = (time.perf_counter_ns() - t0) / 1000.0
    return {
        "n_sources": n_sources,
        "fanin": fanin,
        "n_layers": layer,
        "attack_layer": attack_layer,
        "omitted_handle": omitted_handle,
        "expected_missing_count": len(expected_missing),
        "observed_missing_count": len(decision.missing_ids),
        "exact_missing": frozenset(decision.missing_ids) == expected_missing,
        "allow": decision.allow,
        "reason": decision.reason,
        "gate_us": gate_us,
    }


def run(out_dir: Path, repeats: int = 200, fanin: int = 4) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    ns = [16, 64, 256, 1024]
    rows = []
    summaries = []
    for n in ns:
        probe = build_tree(n, fanin)
        layers = probe["n_layers"]
        complete_times = []
        for _ in range(repeats):
            r = build_tree(n, fanin)
            complete_times.append(r["gate_us"])
        complete = {
            "n_sources": n,
            "fanin": fanin,
            "n_layers": layers,
            "complete_accept": all(build_tree(n, fanin)["allow"] for _ in range(3)),
            "gate_median_us": statistics.median(complete_times),
            "gate_p95_us": sorted(complete_times)[max(0, int(0.95 * len(complete_times)) - 1)],
        }
        attacks = []
        for layer in range(layers):
            r = build_tree(n, fanin, attack_layer=layer)
            rows.append(r)
            attacks.append(r)
        complete["attack_layers_tested"] = len(attacks)
        complete["all_attacks_rejected"] = all(not r["allow"] for r in attacks)
        complete["all_exact_missing"] = all(r["exact_missing"] for r in attacks)
        complete["missing_counts_by_layer"] = [r["observed_missing_count"] for r in attacks]
        summaries.append(complete)

    summary = {
        "design": "balanced fan-in evidence compression tree; one branch suppressed at each possible layer",
        "repeats_complete_gate": repeats,
        "fanin": fanin,
        "settings": summaries,
        "all_complete_accepted": all(x["complete_accept"] for x in summaries),
        "all_layer_attacks_rejected": all(x["all_attacks_rejected"] for x in summaries),
        "all_missing_sets_exact": all(x["all_exact_missing"] for x in summaries),
        "n_attack_conditions": len(rows),
    }
    (out_dir / "trials.jsonl").write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows), encoding="utf-8")
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return summary


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="results/composition")
    ap.add_argument("--repeats", type=int, default=200)
    ap.add_argument("--fanin", type=int, default=4)
    args = ap.parse_args()
    run(Path(args.out_dir), repeats=args.repeats, fanin=args.fanin)
