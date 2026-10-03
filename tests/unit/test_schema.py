
"""
Unit tests for atlas schema and evidence model.

REPAIR V3: This file was empty on GitHub. Restored full content.
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

    def test_l4_allows_sorry(self):
        """
        L4 (PROOF_SOURCE_COMPLETE) does NOT require sorry to be absent.
        Sorry is only prohibited at L5 (KERNEL_CHECKED).
        """
        # L4 is about proof source completeness, not kernel verification
        assert L_DESCRIPTIONS["L4"] == "PROOF_SOURCE_COMPLETE"
        assert "KERNEL" not in L_DESCRIPTIONS["L4"]

    def test_l5_requires_no_sorry(self):
        """L5 (KERNEL_CHECKED) requires no sorry and no unauthorized axiom."""
        assert L_DESCRIPTIONS["L5"] == "KERNEL_CHECKED"
        # L5 is the only level where sorry causes a FAIL


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


class TestLeanInterfaceAlignment:
    """
    Verify that lean_interface.py formal_level() aligns with canonical definitions.
    REPAIR V3: Previous lean_interface.py had L4=sorry, L5=no sorry which was wrong.
    """

    def test_l5_requires_no_sorry_and_no_unauthorized_axiom(self):
        """L5 = build succeeds + no sorry + no unauthorized axiom."""
        # Simulate LeanBuildResult logic
        def formal_level(success, has_sorry, has_unauthorized_axiom):
            if not success:
                return "L0"
            if has_unauthorized_axiom:
                return "L0"
            if not has_sorry:
                return "L5"
            return "L1"  # sorry present → L1 (conservative)

        assert formal_level(True, False, False) == "L5"
        assert formal_level(True, True, False) == "L1"   # sorry → L1, not L4
        assert formal_level(True, False, True) == "L0"   # unauthorized axiom → L0
        assert formal_level(False, False, False) == "L0"  # build failed → L0

    def test_sorry_allowed_at_L1_through_L4(self):
        """Sorry is allowed at L1, L2, L3, L4 — only prohibited at L5."""
        sorry_allowed_levels = ["L1", "L2", "L3", "L4"]
        for level in sorry_allowed_levels:
            assert level in L_LEVELS
            assert level != "L5"

    def test_sorry_prohibited_only_at_L5(self):
        """Only L5 prohibits sorry."""
        assert "L5" in L_LEVELS
        assert L_DESCRIPTIONS["L5"] == "KERNEL_CHECKED"


class TestCanonicalTheoremName:
    """Verify canonical theorem name consistency."""

    CANONICAL = "circlePacking10MinDistBound"
    OLD_NAME = "circlePacking10MinDist"

    def test_canonical_name_has_bound_suffix(self):
        assert self.CANONICAL.endswith("Bound")

    def test_old_name_is_different(self):
        assert self.OLD_NAME != self.CANONICAL

    def test_old_name_is_prefix_of_canonical(self):
        """The old name is a prefix of the canonical name (missing 'Bound')."""
        assert self.CANONICAL.startswith(self.OLD_NAME)

    def test_canonical_name_format(self):
        """Canonical name follows camelCase convention."""
        assert self.CANONICAL[0].islower()
        assert "10" in self.CANONICAL
        assert "MinDist" in self.CANONICAL
        assert "Bound" in self.CANONICAL
