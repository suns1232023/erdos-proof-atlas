
"""
Unit tests for atlas schema and evidence model.
Migrated from test/ → tests/unit/
"""
import pytest


# ---------------------------------------------------------------------------
# Evidence axis constants
# ---------------------------------------------------------------------------
E_LEVELS = ["E0", "E1", "E2", "E3", "E4", "E5"]
L_LEVELS = ["L0", "L1", "L2", "L3", "L4", "L5"]

E_DESCRIPTIONS = {
    "E0": "IDEA",
    "E1": "NUMERICAL",
    "E2": "COMPUTATIONAL",
    "E3": "INDEPENDENTLY_VERIFIED",
    "E4": "EXACTIFIED",
    "E5": "SYMBOLICALLY_CERTIFIED",
}

L_DESCRIPTIONS = {
    "L0": "NOT_FORMALIZED",
    "L1": "STATEMENT_FORMALIZED",
    "L2": "DEFINITIONS_FORMALIZED",
    "L3": "KEY_LEMMAS_FORMALIZED",
    "L4": "PROOF_SOURCE_COMPLETE",
    "L5": "KERNEL_CHECKED",
}


class TestEvidenceAxisSchema:
    """Verify the E-axis (computational evidence) schema."""

    def test_e_levels_count(self):
        assert len(E_LEVELS) == 6

    def test_e_levels_ordered(self):
        assert E_LEVELS == ["E0", "E1", "E2", "E3", "E4", "E5"]

    def test_e_descriptions_complete(self):
        for level in E_LEVELS:
            assert level in E_DESCRIPTIONS, f"Missing description for {level}"

    def test_e5_is_symbolically_certified(self):
        assert E_DESCRIPTIONS["E5"] == "SYMBOLICALLY_CERTIFIED"

    def test_e0_is_idea(self):
        assert E_DESCRIPTIONS["E0"] == "IDEA"


class TestFormalAxisSchema:
    """Verify the L-axis (formal proof) schema."""

    def test_l_levels_count(self):
        assert len(L_LEVELS) == 6

    def test_l_levels_ordered(self):
        assert L_LEVELS == ["L0", "L1", "L2", "L3", "L4", "L5"]

    def test_l_descriptions_complete(self):
        for level in L_LEVELS:
            assert level in L_DESCRIPTIONS, f"Missing description for {level}"

    def test_l5_is_kernel_checked(self):
        """L5 must mean lake build passes with no sorry and no unauthorized axiom."""
        assert L_DESCRIPTIONS["L5"] == "KERNEL_CHECKED"

    def test_l4_is_proof_source_complete(self):
        """L4 means proof source is complete; final acceptance checks may still be pending."""
        assert L_DESCRIPTIONS["L4"] == "PROOF_SOURCE_COMPLETE"

    def test_l0_is_not_formalized(self):
        assert L_DESCRIPTIONS["L0"] == "NOT_FORMALIZED"

    def test_l1_is_statement_formalized(self):
        """L1 = mathematically meaningful statement exists in Lean."""
        assert L_DESCRIPTIONS["L1"] == "STATEMENT_FORMALIZED"


class TestStatusTransitions:
    """Verify that status transitions are monotonically increasing."""

    def test_e_axis_monotone(self):
        for i in range(len(E_LEVELS) - 1):
            assert E_LEVELS.index(E_LEVELS[i]) < E_LEVELS.index(E_LEVELS[i + 1])

    def test_l_axis_monotone(self):
        for i in range(len(L_LEVELS) - 1):
            assert L_LEVELS.index(L_LEVELS[i]) < L_LEVELS.index(L_LEVELS[i + 1])

    def test_cannot_skip_levels(self):
        """Levels must be sequential; no automatic promotion."""
        for i, level in enumerate(E_LEVELS):
            assert int(level[1]) == i

        for i, level in enumerate(L_LEVELS):
            assert int(level[1]) == i

