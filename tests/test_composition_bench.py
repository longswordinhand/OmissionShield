from src.composition_bench import build_tree


def test_multilayer_complete_and_source_suppression():
    complete = build_tree(64, fanin=4)
    assert complete['allow'] is True
    assert complete['n_layers'] == 3
    for layer, expected_missing in enumerate([1, 4, 16]):
        attacked = build_tree(64, fanin=4, attack_layer=layer)
        assert attacked['allow'] is False
        assert attacked['exact_missing'] is True
        assert attacked['observed_missing_count'] == expected_missing
