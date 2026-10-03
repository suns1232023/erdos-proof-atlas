"""Unit tests for dual-axis evidence model."""
import pytest, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from atlas.schema.evidence import ComputationalEvidence, FormalEvidence, EvidenceStatus, validate_upgrade

def test_evidence_ordering():
    assert ComputationalEvidence.NUMERICAL < ComputationalEvidence.SYMBOLICALLY_CERTIFIED
    assert FormalEvidence.NOT_FORMALIZED < FormalEvidence.LEAN_BUILD_VERIFIED

def test_only_l5_is_formally_proved():
    assert FormalEvidence.LEAN_BUILD_VERIFIED.is_formally_proved()
    assert not FormalEvidence.THEOREM_PROVED.is_formally_proved()
    assert not FormalEvidence.STATEMENT_FORMALIZED.is_formally_proved()

def test_e5_l5_is_theorem():
    s = EvidenceStatus(ComputationalEvidence.SYMBOLICALLY_CERTIFIED, FormalEvidence.LEAN_BUILD_VERIFIED)
    assert s.is_theorem()

def test_e5_l0_is_not_theorem():
    s = EvidenceStatus(ComputationalEvidence.SYMBOLICALLY_CERTIFIED, FormalEvidence.NOT_FORMALIZED)
    assert not s.is_theorem()

def test_forbidden_numerical_to_theorem():
    with pytest.raises(ValueError): validate_upgrade("NUMERICAL", "THEOREM")

def test_forbidden_computational_to_theorem():
    with pytest.raises(ValueError): validate_upgrade("COMPUTATIONAL", "THEOREM")

def test_forbidden_ai_to_verified():
    with pytest.raises(ValueError): validate_upgrade("AI_GENERATED", "VERIFIED")

def test_forbidden_certificate_to_formal_proof():
    with pytest.raises(ValueError): validate_upgrade("CERTIFICATE", "FORMAL_PROOF")

def test_evidence_label():
    s = EvidenceStatus(ComputationalEvidence.INDEPENDENTLY_VERIFIED, FormalEvidence.STATEMENT_FORMALIZED)
    assert s.label() == "E3/L1"

def test_search_result_must_be_numerical():
    from atlas.search.multistart import SearchResult
    with pytest.raises(ValueError):
        SearchResult("test","test",0.5,[],42,"test",1.0,{},status="THEOREM")

def test_galois_cert_cannot_be_theorem():
    from atlas.certification.certificate import GaloisCertificate
    with pytest.raises(ValueError):
        GaloisCertificate("P18",18,True,True,False,187,[],24,"computational","S18","test",False,"test",status="THEOREM")
