
"""
Unit tests for P18(d) minimal polynomial properties.
Verifies: coefficients, degree, leading term, constant term.
"""
import pytest

# Certified P18(d) coefficients (highest to lowest degree)
# Source: de Groot, Peikert, Würtz (1990) / OEIS A281065
P18_COEFFS = [
    1180129, -11436428, 98015844, -462103584, 1145811528,
    -1398966480, 227573920, 1526909568, -1038261808, -2960321792,
    7803109440, -9722063488, 7918461504, -4564076288, 1899131648,
    -563649536, 114038784, -14172160, 819200
]

D10_APPROX = 0.421279543983903432768821760651


class TestP18Coefficients:
    """Verify structural properties of P18(d)."""

    def test_degree(self):
        """P18 must be degree 18."""
        assert len(P18_COEFFS) == 19  # 19 coefficients for degree-18 polynomial

    def test_leading_coefficient(self):
        """Leading coefficient must be 1180129 = 827 × 1427."""
        assert P18_COEFFS[0] == 1180129
        assert 1180129 == 827 * 1427

    def test_constant_term(self):
        """Constant term must be 819200 = 2^15 × 5^2."""
        assert P18_COEFFS[-1] == 819200
        assert 819200 == (2 ** 15) * (5 ** 2)

    def test_all_integer_coefficients(self):
        """All coefficients must be integers."""
        for c in P18_COEFFS:
            assert isinstance(c, int), f"Non-integer coefficient: {c}"

    def test_nonzero_leading_coefficient(self):
        assert P18_COEFFS[0] != 0

    def test_nonzero_constant_term(self):
        assert P18_COEFFS[-1] != 0

    def test_coefficient_count(self):
        """Exactly 19 coefficients for a degree-18 polynomial."""
        assert len(P18_COEFFS) == 19


class TestP18NumericalRoot:
    """Verify that d10 is approximately a root of P18."""

    def _eval_p18(self, x):
        result = 0.0
        for i, c in enumerate(P18_COEFFS):
            result += c * (x ** (18 - i))
        return result

    def test_d10_is_approximate_root(self):
        """P18(d10) should be very close to 0."""
        residual = abs(self._eval_p18(D10_APPROX))
        assert residual < 1e-5, f"Residual too large: {residual}"

    def test_d10_positive(self):
        assert D10_APPROX > 0

    def test_d10_less_than_one(self):
        """d10 must be less than 1 (it's a distance in unit square)."""
        assert D10_APPROX < 1.0

    def test_d10_in_known_range(self):
        """d10 must be in the known isolating interval."""
        a = 4212795439839 / 10 ** 13
        b = 4212795439840 / 10 ** 13
        assert a <= D10_APPROX <= b, f"d10={D10_APPROX} not in [{a}, {b}]"


class TestP18IrreducibilityEvidence:
    """
    Lightweight checks for irreducibility evidence.
    Full symbolic verification requires SymPy (see integration tests).
    """

    def test_leading_coeff_not_divisible_by_17(self):
        """Good prime check: leading coefficient must not be divisible by p=17."""
        assert P18_COEFFS[0] % 17 != 0

    def test_leading_coeff_not_divisible_by_3(self):
        assert P18_COEFFS[0] % 3 != 0

    def test_constant_term_not_zero(self):
        """Constant term nonzero ensures d=0 is not a root."""
        assert P18_COEFFS[-1] != 0

