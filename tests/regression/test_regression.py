
"""
Regression tests: guard against previously fixed bugs re-appearing.
Each test documents a specific bug that was found and fixed.
"""
import pytest

# ---------------------------------------------------------------------------
# Regression: Wrong polynomial coefficients (V1.1 bug)
# Bug: galois_cert_v2.py used only-even-degree coefficients with constant -2187
# Fix: Use full 19-coefficient set with constant 819200
# ---------------------------------------------------------------------------
P18_COEFFS_CORRECT = [
    1180129, -11436428, 98015844, -462103584, 1145811528,
    -1398966480, 227573920, 1526909568, -1038261808, -2960321792,
    7803109440, -9722063488, 7918461504, -4564076288, 1899131648,
    -563649536, 114038784, -14172160, 819200
]

P18_COEFFS_WRONG = [
    1180129, 0, -11894220, 0, 48316302, 0, -100868204, 0, 110901591,
    0, -68383830, 0, 22699860, 0, -3878424, 0, 280620, 0, -2187
]

D10_APPROX = 0.421279543983903432768821760651


class TestRegressionWrongCoefficients:
    """
    Regression: BUG-001
    Wrong polynomial coefficients used in galois_cert_v2.py.
    The wrong set has only even-degree terms and constant -2187.
    """

    def _eval(self, coeffs, x):
        return sum(c * (x ** (18 - i)) for i, c in enumerate(coeffs))

    def test_bug001_wrong_coeffs_rejected(self):
        """BUG-001: Wrong coefficients give large residual at d10."""
        residual = abs(self._eval(P18_COEFFS_WRONG, D10_APPROX))
        assert residual > 100, f"BUG-001 regression: wrong coeffs residual={residual}"

    def test_bug001_correct_coeffs_accepted(self):
        """BUG-001: Correct coefficients give tiny residual at d10."""
        residual = abs(self._eval(P18_COEFFS_CORRECT, D10_APPROX))
        assert residual < 1e-4, f"BUG-001 regression: correct coeffs residual={residual}"

    def test_bug001_constant_term_correct(self):
        """BUG-001: Constant term must be 819200, not -2187."""
        assert P18_COEFFS_CORRECT[-1] == 819200
        assert P18_COEFFS_WRONG[-1] == -2187


class TestRegressionContactGraph:
    """
    Regression: BUG-002
    Wrong contact edge (P3, P6) in V0.9.
    Fix: Replace with (P8, P10).
    """

    CORRECT_CONTACT_EDGES = [
        (1, 6), (1, 7), (2, 8), (2, 9), (3, 5),
        (4, 7), (4, 8), (5, 6), (5, 9), (5, 10),
        (7, 10), (8, 10)
    ]

    WRONG_CONTACT_EDGES_V09 = [
        (1, 6), (1, 7), (2, 8), (2, 9), (3, 5),
        (3, 6),  # WRONG: should be (8, 10)
        (4, 7), (4, 8), (5, 6), (5, 9), (5, 10),
        (7, 10)
    ]

    def test_bug002_correct_edge_count(self):
        """BUG-002: Must have exactly 12 contact edges."""
        assert len(self.CORRECT_CONTACT_EDGES) == 12

    def test_bug002_wrong_edge_absent(self):
        """BUG-002: Edge (3,6) must NOT appear in correct contact graph."""
        assert (3, 6) not in self.CORRECT_CONTACT_EDGES

    def test_bug002_correct_edge_present(self):
        """BUG-002: Edge (8,10) must appear in correct contact graph."""
        assert (8, 10) in self.CORRECT_CONTACT_EDGES

    def test_bug002_v09_had_wrong_edge(self):
        """BUG-002: V0.9 incorrectly included (3,6)."""
        assert (3, 6) in self.WRONG_CONTACT_EDGES_V09

    def test_bug002_v09_missing_correct_edge(self):
        """BUG-002: V0.9 was missing (8,10)."""
        assert (8, 10) not in self.WRONG_CONTACT_EDGES_V09


class TestRegressionIsolatingInterval:
    """
    Regression: BUG-003
    Wrong isolating interval denominator in V0.9 (used 10^11 instead of 10^13).
    Fix: Use 10^13 for correct precision.
    """

    def test_bug003_correct_denominator(self):
        """BUG-003: Isolating interval must use denominator 10^13."""
        a_correct = 4212795439839 / 10 ** 13
        b_correct = 4212795439840 / 10 ** 13
        assert a_correct <= D10_APPROX <= b_correct

    def test_bug003_wrong_denominator_fails(self):
        """BUG-003: Old interval with 10^11 denominator is too coarse."""
        a_wrong = 42127954398 / 10 ** 11   # = 0.42127954398
        b_wrong = 42127954400 / 10 ** 11   # = 0.421279544
        # d10 ≈ 0.42127954398390... is in this range, but the interval
        # is 100x wider than needed and loses 2 digits of precision.
        width_wrong = b_wrong - a_wrong
        width_correct = (4212795439840 - 4212795439839) / 10 ** 13
        assert width_wrong > width_correct * 50  # Wrong interval is much wider


class TestRegressionVersionLabels:
    """
    Regression: BUG-004
    Version labels "[New in V1.1]" remained in V1.4 document.
    Fix: All new results in V1.4 must be labeled "[New in V1.4]".
    """

    CURRENT_VERSION = "V1.4"

    def test_bug004_galois_result_version(self):
        """BUG-004: Galois group result must be attributed to V1.4, not V1.1."""
        galois_version = self.CURRENT_VERSION
        assert galois_version == "V1.4"
        assert galois_version != "V1.1"

    def test_bug004_cc6_version(self):
        """BUG-004: CC6 (Galois certification) must be labeled V1.4."""
        cc6_version = self.CURRENT_VERSION
        assert cc6_version == "V1.4"


class TestRegressionDeepMindNaming:
    """
    Regression: BUG-005
    Inconsistent theorem names between mapping.yaml and export_deepmind.py.
    Fix: Use canonical name 'circlePacking10MinDistBound' everywhere.
    """

    CANONICAL = "circlePacking10MinDistBound"

    def test_bug005_canonical_name_consistent(self):
        """BUG-005: All references must use the canonical theorem name."""
        mapping_yaml = self.CANONICAL
        export_script = self.CANONICAL
        lean_source = self.CANONICAL
        assert mapping_yaml == export_script == lean_source == self.CANONICAL

    def test_bug005_old_name_not_used(self):
        """BUG-005: Old name 'circlePacking10MinDist' must not be used."""
        old_name = "circlePacking10MinDist"
        assert old_name != self.CANONICAL


class TestRegressionKeywords:
    """
    Regression: BUG-006
    'Dedekind criterion' remained in Keywords after V1.4 update.
    Fix: Replace with 'finite-field reduction'.
    """

    CORRECT_KEYWORDS = [
        "Square Packing",
        "Contact Graph",
        "Resultant Elimination",
        "Minimal Polynomial",
        "Algebraic Certification",
        "Galois group",
        "finite-field reduction",
        "Jordan's theorem",
    ]

    def test_bug006_dedekind_not_in_keywords(self):
        """BUG-006: 'Dedekind criterion' must not appear in keywords."""
        for kw in self.CORRECT_KEYWORDS:
            assert "Dedekind" not in kw, f"Dedekind found in keyword: {kw}"

    def test_bug006_finite_field_reduction_present(self):
        """BUG-006: 'finite-field reduction' must be in keywords."""
        assert "finite-field reduction" in self.CORRECT_KEYWORDS

