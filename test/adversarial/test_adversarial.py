"""Adversarial tests — verifier must REJECT all bad configurations."""
import pytest, numpy as np, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from atlas.geometry.circle_packing import PackingConfiguration, evaluate_configuration
from atlas.verification.verifier import verify_adversarial_cases

def test_overlapping_rejected():
    assert not evaluate_configuration(PackingConfiguration(3, np.array([[0.1,0.1],[0.1,0.1],[0.9,0.9]]))).passed

def test_boundary_rejected():
    assert not evaluate_configuration(PackingConfiguration(2, np.array([[1.5,0.5],[0.5,0.5]]))).passed

def test_duplicate_rejected():
    assert not evaluate_configuration(PackingConfiguration(3, np.array([[0.3,0.3],[0.3,0.3],[0.7,0.7]]))).passed

def test_all_adversarial_cases_rejected():
    for case, ok in verify_adversarial_cases().items():
        assert ok, f"Adversarial case '{case}' was NOT rejected"

def test_numerical_status_enforced():
    from atlas.search.multistart import SearchResult
    with pytest.raises(ValueError):
        SearchResult("t","t",0.5,[],42,"t",1.0,{},status="THEOREM")
