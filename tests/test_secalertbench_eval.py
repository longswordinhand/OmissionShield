import json
from pathlib import Path

from src.secalertbench_eval import ALL_FIELDS, CONTENT_ONLY_EXCLUDE, freeze_selection, load_frozen, visible_fields


def test_frozen_secalertbench_cohort_is_balanced_and_stable(tmp_path: Path):
    data = []
    for label in ['Attack', 'Non-Attack']:
        for i in range(5):
            row = {f: f'{f}-{i}' for f in ALL_FIELDS}
            row['rule_name'] = f'rule-{label}-{i}'
            row['Label'] = label
            data.append(row)
    dataset = tmp_path / 'd.json'
    frozen = tmp_path / 'f.json'
    dataset.write_text(json.dumps(data), encoding='utf-8')
    freeze_selection(dataset, frozen, n_per_label=3)
    rows = load_frozen(dataset, frozen)
    assert sum(r['Label'] == 'Attack' for r in rows) == 3
    assert sum(r['Label'] == 'Non-Attack' for r in rows) == 3
    primary = visible_fields(rows[0], 'primary')
    content = visible_fields(rows[0], 'content_only')
    assert 'Label' not in primary
    assert CONTENT_ONLY_EXCLUDE.isdisjoint(content)
