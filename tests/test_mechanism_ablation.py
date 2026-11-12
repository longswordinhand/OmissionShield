from src.mechanism_ablation import build_transformed_case

def test_mechanism_ablation_complete_and_attack():
    complete = build_transformed_case(16, 4, None)
    assert complete["positive_provenance"]["allow"]
    assert complete["terminal_only"]["allow"]
    assert complete["eci"]["allow"]
    assert complete["direct_manifest_full_forward_special_case"]["allow"]

    attacked = build_transformed_case(16, 4, 1)
    assert attacked["positive_provenance"]["allow"]
    assert attacked["terminal_only"]["allow"]
    assert not attacked["eci"]["allow"]
    assert attacked["eci"]["exact_missing"]
    assert not attacked["direct_manifest_full_forward_special_case"]["allow"]
