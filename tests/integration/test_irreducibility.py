
"""
Integration tests: symbolic irreducibility verification via SymPy.
Requires: sympy
"""
import pytest

sympy = pytest.importorskip("sympy", reason="sympy not installed")

P18_COEFFS = [
    1180129, -11436428, 98015844, -462103584, 1145811528,
    -1398966480, 227573920, 1526909568, -1038261808, -2960321792,
    7803109440, -9722063488, 7918461504, -4564076288, 1899131648,
    -563649536, 114038784, -14172160, 819200
]


@pytest.fixture(scope="module")
def p18_poly():
    d = sympy.Symbol("d")
    poly_expr = sum(c * d ** (18 - i) for i, c in enumerate(P18_COEFFS))
    return sympy.Poly(poly_expr, d)


class TestIrreducibilitySymPy:

    def test_degree_is_18(self, p18_poly):
        assert p18_poly.degree() == 18

    def test_irreducible_over_Q(self, p18_poly):
        """P18 must be irreducible over Q."""
        assert p18_poly.is_irreducible is True

    def test_primitive_over_Z(self, p18_poly):
        """GCD of all coefficients must be 1 (primitive polynomial)."""
        content = sympy.gcd(P18_COEFFS)
        assert content == 1

    def test_irreducible_mod_17(self, p18_poly):
        """P18 mod 17 must be irreducible in GF(17)[d] — certificate prime."""
        d = sympy.Symbol("d")
        poly_expr = sum(c * d ** (18 - i) for i, c in enumerate(P18_COEFFS))
        p17 = sympy.Poly(poly_expr, d, domain=sympy.GF(17))
        assert p17.is_irreducible is True

    def test_irreducible_mod_23(self, p18_poly):
        """P18 mod 23 must also be irreducible — secondary certificate."""
        d = sympy.Symbol("d")
        poly_expr = sum(c * d ** (18 - i) for i, c in enumerate(P18_COEFFS))
        p23 = sympy.Poly(poly_expr, d, domain=sympy.GF(23))
        assert p23.is_irreducible is True

    def test_leading_coeff_not_divisible_by_17(self):
        assert P18_COEFFS[0] % 17 != 0

    def test_gauss_lemma_chain(self, p18_poly):
        """
        Full Gauss's Lemma chain:
        primitive_over_Z AND irreducible_mod_17 => irreducible_over_Q
        """
        content = sympy.gcd(P18_COEFFS)
        primitive = (content == 1)

        d = sympy.Symbol("d")
        poly_expr = sum(c * d ** (18 - i) for i, c in enumerate(P18_COEFFS))
        p17 = sympy.Poly(poly_expr, d, domain=sympy.GF(17))
        irred_mod_17 = p17.is_irreducible

        # By Gauss's Lemma: primitive + irreducible mod p => irreducible over Q
        assert primitive is True
        assert irred_mod_17 is True
        assert p18_poly.is_irreducible is True


class TestRootIsolation:

    def test_sturm_root_count_in_interval(self):
        """Sturm sequence must confirm exactly 1 real root in isolating interval."""
        d = sympy.Symbol("d")
        poly_expr = sum(c * d ** (18 - i) for i, c in enumerate(P18_COEFFS))
        P = sympy.Poly(poly_expr, d)

        sturm_chain = sympy.sturm(P)

        a = sympy.Rational(4212795439839, 10 ** 13)
        b = sympy.Rational(4212795439840, 10 ** 13)

        def count_sign_changes(val):
            evals = [f.eval(val) for f in sturm_chain]
            evals = [v for v in evals if v != 0]
            return sum(
                1 for i in range(len(evals) - 1)
                if evals[i] * evals[i + 1] < 0
            )

        v_a = count_sign_changes(a)
        v_b = count_sign_changes(b)
        root_count = v_a - v_b

        assert root_count == 1, (
            f"Expected 1 root in interval, got {root_count} "
            f"(V(a)={v_a}, V(b)={v_b})"
        )

    def test_interval_endpoints_sign_change(self):
        """P18(a) and P18(b) must have opposite signs (IVT)."""
        d = sympy.Symbol("d")
        poly_expr = sum(c * d ** (18 - i) for i, c in enumerate(P18_COEFFS))

        a = sympy.Rational(4212795439839, 10 ** 13)
        b = sympy.Rational(4212795439840, 10 ** 13)

        val_a = poly_expr.subs(d, a)
        val_b = poly_expr.subs(d, b)

        assert val_a * val_b < 0, (
            f"No sign change: P18(a)={val_a}, P18(b)={val_b}"
        )

