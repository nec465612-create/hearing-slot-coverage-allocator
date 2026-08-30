from pathlib import Path


ROOT = Path(__file__).parents[2]
CONTRACT = ROOT / "contracts" / "hearing_slot_coverage_allocator.py"


def test_integration_matrix_is_declared_before_network_execution():
    source = CONTRACT.read_text(encoding="utf-8")
    assert "gl.nondet.web.get" in source
    assert "hashlib.sha256(response.body).hexdigest()" in source
    assert "validator_fn" in source
    assert "selected_comment_ids" in source


def test_contract_has_no_external_side_effect_dependencies():
    source = CONTRACT.read_text(encoding="utf-8")
    assert "requests" not in source
    assert "sqlite" not in source.lower()
    assert "web3" not in source.lower()
