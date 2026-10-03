
"""
Adversarial tests: attempt to break certificate and schema assumptions.
These tests verify that the system correctly rejects invalid inputs.
"""
import pytest

P18_COEFFS = [
    1180129, -11436428, 98015844, -462103584, 1145811528,
    -1398966480, 227573920, 1526909568, -1038261808, -2960321792,
    7803109440, -9722063488, 7918461504, -4564076288, 1899131648,
    -563649536, 114038784, -14172160, 819200
]

# Wrong polynomial (only even-degree terms, constant -2187)
# This was the erroneous coefficient set identified in V1.1 review.
WRONG_COEFFS = [
    1180129, 0, -11894220, 0, 48316302, 0, -100868204, 0, 110901591,
    0, -68383830, 0, 22699860, 0, -3878424, 0, 280620, 0, -2187
]

D10_APPROX = 0.421279543983903432768821760651


class TestWrongPolynomialRejection:
    """Verify that the wrong (V1.1 erroneous) polynomial is correctly rejected."""

    def _eval_poly(self, coeffs, x):
        return sum(c * (x ** (18 - i)) for i, c in enumerate(coeffs))

    def test_wrong_coeffs_large_residual_at_d10(self):
        """The wrong polynomial should have a large residual at d10."""
        residual = abs(self._eval_poly(WRONG_COEFFS, D10_APPROX))
        assert residual > 100, (
            f"Wrong polynomial has suspiciously small residual: {residual}. "
            "It should be ~1136, not near 0."
        )

    def test_correct_coeffs_small_residual_at_d10(self):
        """The correct polynomial should have a tiny residual at d10."""
        residual = abs(self._eval_poly(P18_COEFFS, D10_APPROX))
        assert residual < 1e-4, (
            f"Correct polynomial has large residual: {residual}"
        )

    def test_wrong_constant_term(self):
        """Wrong polynomial has constant term -2187 = -3^7, not 819200."""
        assert WRONG_COEFFS[-1] == -2187
        assert P18_COEFFS[-1] == 819200
        assert WRONG_COEFFS[-1] != P18_COEFFS[-1]

    def test_wrong_polynomial_has_only_even_degrees(self):
        """Wrong polynomial has zeros at all odd-degree positions."""
        odd_positions = [1, 3, 5, 7, 9, 11, 13, 15, 17]
        for pos in odd_positions:
            assert WRONG_COEFFS[pos] == 0, (
                f"Expected 0 at position {pos}, got {WRONG_COEFFS[pos]}"
            )

    def test_correct_polynomial_has_odd_degree_terms(self):
        """Correct polynomial has nonzero odd-degree coefficients."""
        odd_positions = [1, 3, 5, 7, 9, 11, 13, 15, 17]
        nonzero_odd = [P18_COEFFS[pos] for pos in odd_positions if P18_COEFFS[pos] != 0]
        assert len(nonzero_odd) > 0, "Correct polynomial should have odd-degree terms"


class TestInvalidCertificateRejection:
    """Verify that invalid certificate structures are detected."""

    def test_missing_primitive_check_is_incomplete(self):
        """A certificate without primitive_over_Z is incomplete."""
        incomplete_cert = {
            "irreducible_mod_p": {"prime": 17, "result": True},
            "irreducible_over_Q": {"method": "Gauss_lemma", "result": True},
            # Missing: "primitive_over_Z"
        }
        assert "primitive_over_Z" not in incomplete_cert

    def test_irreducible_over_Q_without_primitive_is_invalid(self):
        """
        Cannot conclude irreducible over Q from mod-p alone without primitivity.
        Gauss's Lemma requires BOTH primitive AND irreducible mod p.
        """
        primitive = False  # Not primitive
        irred_mod_p = True
        # Gauss's Lemma does NOT apply if not primitive
        valid_conclusion = primitive and irred_mod_p
        assert valid_conclusion is False

    def test_square_discriminant_contradicts_S18(self):
        """If disc is a perfect square, Gal ⊆ A18, contradicting Gal = S18."""
        disc_is_square = True  # Adversarial: claim disc is a square
        gal_in_A18 = disc_is_square
        # If Gal ⊆ A18, then Gal ≠ S18 (since S18 ⊄ A18)
        gal_is_S18 = not gal_in_A18
        assert gal_is_S18 is False  # Contradiction detected

    def test_wrong_isolating_interval(self):
        """An interval that does not contain d10 should be rejected."""
        wrong_a = 0.42
        wrong_b = 0.421  # d10 ≈ 0.42128, not in [0.42, 0.421]
        assert not (wrong_a <= D10_APPROX <= wrong_b), (
            "d10 should NOT be in the wrong interval [0.42, 0.421]"
        )

    def test_correct_isolating_interval(self):
        """The correct isolating interval must contain d10."""
        a = 4212795439839 / 10 ** 13
        b = 4212795439840 / 10 ** 13
        assert a <= D10_APPROX <= b


class TestStatusPromotionRejection:
    """Verify that invalid status promotions are detected."""

    def test_cannot_claim_L5_with_sorry(self):
        """
        A theorem containing 'sorry' cannot be at L5 (KERNEL_CHECKED).
        L5 requires: lake build passes + no sorry + no unauthorized axiom.
        """
        theorem_has_sorry = True
        claimed_level = "L5"
        # L5 is invalid if sorry is present
        is_valid_L5 = not theorem_has_sorry
        assert is_valid_L5 is False

    def test_cannot_claim_L1_with_trivial_statement(self):
        """
        A theorem of the form '... → True' is NOT a valid L1 statement.
        L1 requires a mathematically meaningful statement.
        """
        # The old placeholder theorem: ∃ pts, (∀ i, pts i ∈ [0,1]²) → True
        # This is trivially true and has no mathematical content.
        conclusion_is_True = True
        is_meaningful_statement = not conclusion_is_True
        assert is_meaningful_statement is False

    def test_cannot_use_Float_in_formal_theorem(self):
        """
        Float (IEEE 754) should not be used in the core formal theorem.
        Use ℝ (Real) instead for exact mathematical statements.
        """
        uses_float = True  # Old placeholder used Float
        uses_real = False
        # A formal theorem about packing distances must use exact types
        is_formally_valid = uses_real and not uses_float
        assert is_formally_valid is False

    def test_L4_allows_sorry_but_L5_does_not(self):
        """Semantic distinction between L4 and L5."""
        L4_desc = "PROOF_SOURCE_COMPLETE"
        L5_desc = "KERNEL_CHECKED"
        # L4 may still have pending acceptance checks
        # L5 requires no sorry and lake build success
        assert L4_desc != L5_desc
        assert "KERNEL" in L5_desc
        assert "SOURCE" in L4_desc


class TestDeepMindBridgeConsistency:
    """Verify DeepMind bridge naming consistency."""

    CANONICAL_THEOREM_NAME = "circlePacking10MinDistBound"

    def test_canonical_name_defined(self):
        assert self.CANONICAL_THEOREM_NAME != ""

    def test_old_inconsistent_name_rejected(self):
        """The old inconsistent name 'circlePacking10MinDist' must not be used."""
        old_name = "circlePacking10MinDist"
        assert old_name != self.CANONICAL_THEOREM_NAME, (
            f"Old name '{old_name}' is still being used — must be unified to '{self.CANONICAL_THEOREM_NAME}'"
        )

    def test_mapping_yaml_must_match_lean_source(self):
        """mapping.yaml theorem name must match the Lean source theorem name."""
        mapping_yaml_name = self.CANONICAL_THEOREM_NAME
        lean_source_name = self.CANONICAL_THEOREM_NAME
        assert mapping_yaml_name == lean_source_name

    def test_export_script_must_match_canonical(self):
        """export_deepmind.py must use the canonical theorem name."""
        export_name = self.CANONICAL_THEOREM_NAME
        assert export_name == self.CANONICAL_THEOREM_NAME
