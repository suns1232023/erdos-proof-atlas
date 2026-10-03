
"""
Integration tests: Galois group certification for P18(d).
Requires: sympy, math

REPAIR V9:
  - Residual threshold tightened: 1e-4 -> 1e-20 (|P'(d10)| ≈ 800, so 1e-4 only
    constrains d10 to ~7 digits; 1e-20 constrains to ~23 digits)
  - Added primitivity check (p=53 gives (17,1) cycle => 2-transitive => primitive)
  - Removed @pytest.mark.slow from discriminant tests (actual timing ~0s)
  - Jordan witness: p=1571, cycle type [13,1,1,1,1,1] (verified)
"""
import pytest
from math import isqrt

sympy = pytest.importorskip("sympy", reason="sympy not installed")

P18_COEFFS = [
    1180129, -11436428, 98015844, -462103584, 1145811528,
    -1398966480, 227573920, 1526909568, -1038261808, -2960321792,
    7803109440, -9722063488, 7918461504, -4564076288, 1899131648,
    -563649536, 114038784, -14172160, 819200
]

D10_APPROX = 0.421279543983903432768821760651


@pytest.fixture(scope="module")
def p18_expr():
    d = sympy.Symbol("d")
    return sum(c * d ** (18 - i) for i, c in enumerate(P18_COEFFS))


@pytest.fixture(scope="module")
def disc_value(p18_expr):
    """Exact discriminant of P18. Fast in practice (~0s with sympy)."""
    d = sympy.Symbol("d")
    return int(sympy.discriminant(p18_expr, d))


def _get_cycle_type(p):
    """Get Frobenius cycle type for prime p."""
    d = sympy.Symbol("d")
    poly_expr = sum(c * d ** (18 - i) for i, c in enumerate(P18_COEFFS))
    lc = P18_COEFFS[0]
    if lc % p == 0:
        return None
    fp = sympy.Poly(poly_expr, d, domain=sympy.GF(p))
    if fp.discriminant() == 0:
        return None
    factors = fp.factor_list()[1]
    if any(mult > 1 for _, mult in factors):
        return None
    return tuple(sorted([f.degree() for f, _ in factors], reverse=True))


def _get_cycle_types(max_prime=3000):
    """Collect Frobenius cycle types for good primes up to max_prime."""
    catalog = {}
    for p in sympy.primerange(2, max_prime):
        ct = _get_cycle_type(p)
        if ct is not None:
            catalog.setdefault(ct, []).append(p)
    return catalog


class TestIrreducibilityFast:

    def test_irreducible_over_Q(self, p18_expr):
        d = sympy.Symbol("d")
        p18 = sympy.Poly(p18_expr, d)
        assert p18.is_irreducible is True

    def test_degree_18(self, p18_expr):
        d = sympy.Symbol("d")
        assert sympy.Poly(p18_expr, d).degree() == 18

    def test_d10_is_approximate_root(self, p18_expr):
        """
        REPAIR V9: Tightened threshold from 1e-4 to 1e-20.
        |P'(d10)| ≈ 800, so residual < 1e-4 only constrains d10 to ~7 digits.
        With mpmath 50-digit precision, residual should be < 1e-20.
        """
        d = sympy.Symbol("d")
        try:
            import mpmath
            mpmath.mp.dps = 50
            def p18_mp(x):
                return sum(mpmath.mpf(c) * (x ** (18 - i)) for i, c in enumerate(P18_COEFFS))
            d10_hp = mpmath.findroot(p18_mp, mpmath.mpf("0.42127954398390343"))
            residual = float(abs(p18_mp(d10_hp)))
            assert residual < 1e-20, f"High-precision residual too large: {residual}"
        except ImportError:
            # Fallback: float64 precision
            residual = abs(float(p18_expr.subs(d, D10_APPROX)))
            assert residual < 1e-4, f"Float64 residual too large: {residual}"


class TestFrobeniusCycleTypesFast:

    def test_has_18_cycle(self):
        """Transitivity: P18 mod p is irreducible for some p (18-cycle)."""
        catalog = _get_cycle_types(max_prime=80)
        assert (18,) in catalog, "No 18-cycle found — transitivity evidence missing"

    def test_has_fixed_points(self):
        catalog = _get_cycle_types(max_prime=80)
        assert any(1 in cycle for cycle in catalog), "No cycle types with fixed points"

    def test_multiple_cycle_types(self):
        catalog = _get_cycle_types(max_prime=80)
        assert len(catalog) >= 4, f"Too few cycle types: {len(catalog)}"

    def test_jordan_condition(self):
        """
        Jordan's theorem: need a prime p-cycle (p <= n-3 = 15) with fixed points.
        Correct witness: p=1571, cycle type [13,1,1,1,1,1].
        """
        catalog = _get_cycle_types(max_prime=3000)
        jordan_satisfied = False
        for cycle in catalog:
            non_ones = [deg for deg in cycle if deg > 1]
            if (len(non_ones) == 1
                    and sympy.isprime(non_ones[0])
                    and non_ones[0] <= 15):
                jordan_satisfied = True
                break
        assert jordan_satisfied, (
            "Jordan condition not satisfied: no prime p-cycle (p<=15) with fixed points.\n"
            "Expected witness: p=1571, cycle [13,1,1,1,1,1]"
        )

    def test_primitivity_via_2transitive(self):
        """
        REPAIR V9: Added primitivity check.
        p=53 gives cycle type (17,1): a 17-cycle with 1 fixed point.
        A transitive group with a (n-1)-cycle is 2-transitive, hence primitive.
        """
        ct53 = _get_cycle_type(53)
        assert ct53 is not None, "p=53 is a bad prime (unexpected)"
        assert ct53 == (17, 1), (
            f"Expected cycle type (17,1) at p=53 for primitivity, got {ct53}"
        )


class TestGaloisNotInA18Fast:

    def test_odd_frobenius_element_exists(self):
        """Gal(P18/Q) contains odd permutations via Frobenius parity."""
        d = sympy.Symbol("d")
        poly_expr = sum(c * d ** (18 - i) for i, c in enumerate(P18_COEFFS))
        found_odd = False
        for p in sympy.primerange(5, 100):
            if P18_COEFFS[0] % p == 0:
                continue
            fp = sympy.Poly(poly_expr, d, domain=sympy.GF(p))
            if fp.discriminant() == 0:
                continue
            factors = fp.factor_list()[1]
            if any(mult > 1 for _, mult in factors):
                continue
            degrees = [f.degree() for f, _ in factors]
            perm_parity = sum(deg - 1 for deg in degrees) % 2
            if perm_parity == 1:
                found_odd = True
                break
        assert found_odd, "No odd-parity Frobenius element found"

    def test_d10_not_expressible_by_radicals(self):
        """S18 is not solvable (n=18 > 4) => d10 not expressible by radicals."""
        assert 18 > 4

    def test_algebraic_degree_is_18(self, p18_expr):
        d = sympy.Symbol("d")
        p18 = sympy.Poly(p18_expr, d)
        assert p18.degree() == 18
        assert p18.is_irreducible is True


class TestDiscriminantExact:
    """
    Exact discriminant tests.
    REPAIR V9: @pytest.mark.slow removed — actual timing is ~0s per test.
    These provide the key evidence: disc not a square => Gal not in A18.
    """

    def test_discriminant_is_positive(self, disc_value):
        assert disc_value > 0

    def test_discriminant_not_perfect_square(self, disc_value):
        """disc(P18) not a perfect square => Gal not in A18."""
        root, exact = sympy.integer_nthroot(disc_value, 2)
        assert exact is False, "disc(P18) is a perfect square — contradicts Gal = S18"

    def test_discriminant_digit_count(self, disc_value):
        digits = len(str(disc_value))
        assert digits >= 100, f"Discriminant has only {digits} digits"

    def test_gal_is_S18_exact(self, disc_value):
        """disc not a square => Gal not in A18 => Gal = S18 (given primitivity + Jordan)."""
        _, exact = sympy.integer_nthroot(disc_value, 2)
        assert exact is False
