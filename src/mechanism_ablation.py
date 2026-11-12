from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from src.runtime import TrustedEvidenceRuntime

KEY = b"omissionshield-mechanism-ablation-v1"


def _chunks(xs: list[str], k: int) -> list[list[str]]:
    return [xs[i:i+k] for i in range(0, len(xs), k)]


def positive_provenance_only(rt: TrustedEvidenceRuntime, terminal_handles: list[str]) -> dict[str, Any]:
    """Validate only the provenance graph that actually exists.

    This baseline has no independent expected-set membership obligation.
    It checks that every terminal handle exists and that every recorded parent
    recursively names an existing node. A missing source that never enters a
    recorded path is therefore invisible by construction.
    """
    seen: set[str] = set()
    stack = list(terminal_handles)
    unknown: set[str] = set()
    while stack:
        h = stack.pop()
        if h in seen:
            continue
        seen.add(h)
        node = rt.dag.nodes.get(h)
        if node is None:
            unknown.add(h)
            continue
        for p in node.parents:
            if p not in rt.dag.nodes:
                unknown.add(p)
            else:
                stack.append(p)
    return {
        "allow": not unknown,
        "unknown_handles": sorted(unknown),
        "observed_source_closure": sorted(rt.dag.source_closure(terminal_handles)),
    }


def terminal_only_check(rt: TrustedEvidenceRuntime, terminal_handles: list[str]) -> dict[str, Any]:
    """Check only the local terminal contract.

    The sink expects exactly one well-formed derived root. It does not receive
    or traverse source ancestry. This models schema/local-manifest validation
    after evidence has been summarized/aggregated.
    """
    if len(terminal_handles) != 1:
        return {"allow": False, "reason": "WRONG_TERMINAL_CARDINALITY"}
    node = rt.dag.nodes.get(terminal_handles[0])
    if node is None:
        return {"allow": False, "reason": "UNKNOWN_TERMINAL"}
    if node.kind != "derived":
        return {"allow": False, "reason": "WRONG_TERMINAL_KIND"}
    if not node.payload_digest:
        return {"allow": False, "reason": "MISSING_TERMINAL_DIGEST"}
    return {"allow": True, "reason": "LOCAL_TERMINAL_CONTRACT_SATISFIED"}


def direct_source_manifest_check(expected: list[str], delivered_source_ids: list[str]) -> dict[str, Any]:
    """Strong special case: every original source ID reaches final verifier."""
    exp = frozenset(expected)
    got = frozenset(delivered_source_ids)
    missing = sorted(exp - got)
    extra = sorted(got - exp)
    return {"allow": not missing and not extra, "missing_ids": missing, "extra_ids": extra}


def build_transformed_case(n_sources: int, fanin: int, attack_layer: int | None) -> dict[str, Any]:
    rt = TrustedEvidenceRuntime(KEY)
    items = [(f"src:{i:05d}", f"payload-{i}") for i in range(n_sources)]
    expected_ids = [eid for eid, _ in items]
    signed = rt.enumerate_source("task", items)

    handles = list(expected_ids)
    lineage = {h: frozenset([h]) for h in handles}
    layer = 0
    omitted_handle: str | None = None
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

    pos = positive_provenance_only(rt, handles)
    terminal = terminal_only_check(rt, handles)
    eci = rt.gate(signed, handles)

    # Strong manifest comparison special case: imagine raw source IDs were
    # forwarded unchanged to the final verifier. This is intentionally
    # separated from the transformed-root setting above.
    delivered_raw = sorted(set(expected_ids) - set(expected_missing))
    manifest = direct_source_manifest_check(expected_ids, delivered_raw)

    return {
        "n_sources": n_sources,
        "fanin": fanin,
        "n_layers": layer,
        "attack_layer": attack_layer,
        "omitted_handle": omitted_handle,
        "expected_missing_ids": sorted(expected_missing),
        "expected_missing_count": len(expected_missing),
        "terminal_handles": handles,
        "positive_provenance": pos,
        "terminal_only": terminal,
        "eci": {
            "allow": eci.allow,
            "missing_ids": sorted(eci.missing_ids),
            "reason": eci.reason,
            "exact_missing": frozenset(eci.missing_ids) == expected_missing,
        },
        "direct_manifest_full_forward_special_case": manifest,
    }


def run(out_dir: Path, fanin: int = 4) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []

    for n in [16, 64, 256, 1024]:
        complete = build_transformed_case(n, fanin, None)
        rows.append({"condition": "complete", **complete})
        for layer in range(complete["n_layers"]):
            rows.append({"condition": "attack", **build_transformed_case(n, fanin, layer)})

    complete_rows = [r for r in rows if r["condition"] == "complete"]
    attack_rows = [r for r in rows if r["condition"] == "attack"]

    summary = {
        "design": "balanced fan-in transformed-evidence trees; sink sees one derived root only",
        "fanin": fanin,
        "n_complete_conditions": len(complete_rows),
        "n_attack_conditions": len(attack_rows),
        "mechanisms": {
            "positive_provenance_only": {
                "complete_accept": sum(r["positive_provenance"]["allow"] for r in complete_rows),
                "attack_reject": sum(not r["positive_provenance"]["allow"] for r in attack_rows),
                "attack_accept": sum(r["positive_provenance"]["allow"] for r in attack_rows),
            },
            "terminal_only_check": {
                "complete_accept": sum(r["terminal_only"]["allow"] for r in complete_rows),
                "attack_reject": sum(not r["terminal_only"]["allow"] for r in attack_rows),
                "attack_accept": sum(r["terminal_only"]["allow"] for r in attack_rows),
            },
            "eci_transitive_coverage": {
                "complete_accept": sum(r["eci"]["allow"] for r in complete_rows),
                "attack_reject": sum(not r["eci"]["allow"] for r in attack_rows),
                "attack_accept": sum(r["eci"]["allow"] for r in attack_rows),
                "exact_missing_attack_conditions": sum(r["eci"]["exact_missing"] for r in attack_rows),
            },
            "direct_manifest_full_forward_special_case": {
                "complete_accept": sum(r["direct_manifest_full_forward_special_case"]["allow"] for r in complete_rows),
                "attack_reject": sum(not r["direct_manifest_full_forward_special_case"]["allow"] for r in attack_rows),
                "attack_accept": sum(r["direct_manifest_full_forward_special_case"]["allow"] for r in attack_rows),
            },
        },
        "attack_missing_counts": [r["expected_missing_count"] for r in attack_rows],
    }

    (out_dir / "trials.jsonl").write_text(
        "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows), encoding="utf-8"
    )
    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return summary


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="results/mechanism_ablation")
    ap.add_argument("--fanin", type=int, default=4)
    args = ap.parse_args()
    run(Path(args.out_dir), args.fanin)
