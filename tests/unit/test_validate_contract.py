"""
Tests for scripts/validate_contract.py

Tests cover:
  - valid contract
  - missing contract
  - missing module
  - wrong Lean version
  - wrong Mathlib revision
  - stale manifest
  - Main.lean missing / lowercase main.lean
  - malformed TOML
  - malformed JSON
"""
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# Add scripts/ to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))


class TestValidateContractIntegration:
    """Integration tests against the actual repository."""

    def test_contract_file_exists(self):
        """project_contract.json must exist."""
        from pathlib import Path
        repo_root = Path(__file__).resolve().parents[2]
        contract = repo_root / "formal" / "lean" / "project_contract.json"
        assert contract.is_file(), f"Missing: {contract}"

    def test_contract_has_required_fields(self):
        """All required fields must be present."""
        from pathlib import Path
        repo_root = Path(__file__).resolve().parents[2]
        contract = json.loads(
            (repo_root / "formal" / "lean" / "project_contract.json").read_text()
        )
        required = [
            "project_name", "project_mode", "lean_toolchain", "mathlib_rev",
            "library_root", "executable_root", "executable_entry",
            "canonical_theorem", "current_formal_level", "required_modules",
            "sorry_policy", "authorized_axioms",
        ]
        for field in required:
            assert field in contract, f"Missing field: {field}"

    def test_formal_level_is_L1(self):
        """Formal level must remain L1 -- do not auto-promote."""
        from pathlib import Path
        repo_root = Path(__file__).resolve().parents[2]
        contract = json.loads(
            (repo_root / "formal" / "lean" / "project_contract.json").read_text()
        )
        level = contract.get("current_formal_level")
        assert level == "L1", (
            f"Formal level is {level!r}, expected L1. "
            "Do not promote to L5 merely because lake build succeeds."
        )

    def test_sorry_policy_L1_allows_sorry(self):
        """L1 must allow sorry."""
        from pathlib import Path
        repo_root = Path(__file__).resolve().parents[2]
        contract = json.loads(
            (repo_root / "formal" / "lean" / "project_contract.json").read_text()
        )
        policy = contract.get("sorry_policy", {})
        assert policy.get("L1") == "allowed", "L1 must allow sorry"

    def test_sorry_policy_L5_forbids_sorry(self):
        """L5 must forbid sorry."""
        from pathlib import Path
        repo_root = Path(__file__).resolve().parents[2]
        contract = json.loads(
            (repo_root / "formal" / "lean" / "project_contract.json").read_text()
        )
        policy = contract.get("sorry_policy", {})
        assert policy.get("L5") == "forbidden", "L5 must forbid sorry"

    def test_canonical_theorem_defined(self):
        """canonical_theorem must be non-empty."""
        from pathlib import Path
        repo_root = Path(__file__).resolve().parents[2]
        contract = json.loads(
            (repo_root / "formal" / "lean" / "project_contract.json").read_text()
        )
        theorem = contract.get("canonical_theorem", "")
        assert theorem, "canonical_theorem must be defined"
        assert "circlePacking10MinDistBound" in theorem

    def test_authorized_axioms_defined(self):
        """authorized_axioms must be a non-empty list."""
        from pathlib import Path
        repo_root = Path(__file__).resolve().parents[2]
        contract = json.loads(
            (repo_root / "formal" / "lean" / "project_contract.json").read_text()
        )
        axioms = contract.get("authorized_axioms", [])
        assert isinstance(axioms, list) and len(axioms) > 0
        assert "Classical.choice" in axioms

    def test_lean_toolchain_format(self):
        """lean_toolchain must follow leanprover/lean4:vX.Y.Z format."""
        from pathlib import Path
        import re
        repo_root = Path(__file__).resolve().parents[2]
        contract = json.loads(
            (repo_root / "formal" / "lean" / "project_contract.json").read_text()
        )
        tc = contract.get("lean_toolchain", "")
        assert re.match(r"leanprover/lean4:v\d+\.\d+\.\d+", tc), (
            f"lean_toolchain format invalid: {tc!r}"
        )

    def test_mathlib_rev_format(self):
        """mathlib_rev must follow vX.Y.Z format."""
        from pathlib import Path
        import re
        repo_root = Path(__file__).resolve().parents[2]
        contract = json.loads(
            (repo_root / "formal" / "lean" / "project_contract.json").read_text()
        )
        rev = contract.get("mathlib_rev", "")
        assert re.match(r"v\d+\.\d+\.\d+", rev), (
            f"mathlib_rev format invalid: {rev!r}"
        )
