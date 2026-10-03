"""Integration tests for the full pipeline."""
import pytest, numpy as np, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

def test_search_produces_numerical():
    from atlas.search.multistart import run_multistart_search
    r = run_multistart_search("test", 4, n_restarts=5, seed=42)
    assert r.status == "NUMERICAL"
    assert r.objective > 0

def test_search_then_verify():
    from atlas.search.multistart import run_multistart_search
    from atlas.geometry.circle_packing import PackingConfiguration, evaluate_configuration
    r = run_multistart_search("test", 4, n_restarts=10, seed=42)
    config = PackingConfiguration(4, np.array(r.coordinates))
    vr = evaluate_configuration(config)
    assert vr.passed

def test_provenance_records_commit():
    from atlas.provenance.tracker import ProvenanceRecord
    p = ProvenanceRecord.create("test", seed=42)
    assert p.git_commit is not None
    assert p.run_id is not None

def test_evidence_status_dict():
    from atlas.schema.evidence import EvidenceStatus, ComputationalEvidence, FormalEvidence
    s = EvidenceStatus(ComputationalEvidence.INDEPENDENTLY_VERIFIED, FormalEvidence.STATEMENT_FORMALIZED)
    d = s.to_dict()
    assert d["combined"] == "E3/L1"
    assert not d["is_formally_proved"]
