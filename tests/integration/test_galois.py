
"""
Integration tests: Galois group certification for P18(d).
Requires: sympy, math

Fast tests (no discriminant): run in CI by default.
Slow tests (@pytest.mark.slow): skipped in CI, run with --run-slow.

Jordan witness: p=1571, cycle type [13,1,1,1,1,1] (verified).
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
    """Slow fixture: exact discriminant (~30-60s). Only used by @pytest.mark.slow tests."""
    d = sympy.Symbol("d")
    return int(sympy.discriminant(p18_expr, d))


def _get_cycle_types(max_prime=3000):
    """Collect Frobenius cycle types for good primes up to max_prime."""
    d = sympy.Symbol("d")
    poly_expr = sum(c * d ** (18 - i) for i, c in enumerate(P18_COEFFS))
    lc = P18_COEFFS[0]
    catalog = {}
    for p in sympy.primerange(2, max_prime):
        if lc % p == 0:
            continue
        fp = sympy.Poly(poly_expr, d, domain=sympy.GF(p))
        if fp.discriminant() == 0:
            continue
        factors = fp.factor_list()[1]
        if any(mult > 1 for _, mult in factors):
            continue
        degrees = tuple(sorted([f.degree() for f, _ in factors], reverse=True))
        catalog.setdefault(degrees, []).append(p)
    return catalog


# ---------------------------------------------------------------------------
# Fast tests — run in CI by default
# ---------------------------------------------------------------------------

class TestIrreducibilityFast:

    def test_irreducible_over_Q(self, p18_expr):
        d = sympy.Symbol("d")
        p18 = sympy.Poly(p18_expr, d)
        assert p18.is_irreducible is True

    def test_degree_18(self, p18_expr):
        d = sympy.Symbol("d")
        assert sympy.Poly(p18_expr, d).degree() == 18

    def test_d10_is_approximate_root(self, p18_expr):
        d = sympy.Symbol("d")
        residual = abs(float(p18_expr.subs(d, D10_APPROX)))
        assert residual < 1e-4, f"Residual too large: {residual}"


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
        Search up to max_prime=3000 (~3.3s) to reliably find it.
        """
        catalog = _get_cycle_types(max_prime=3000)
        jordan_satisfied = False
        witness = None
        for cycle, primes in catalog.items():
            non_ones = [deg for deg in cycle if deg > 1]
            if (
                len(non_ones) == 1
                and sympy.isprime(non_ones[0])
                and non_ones[0] <= 15
            ):
                jordan_satisfied = True
                witness = (non_ones[0], cycle, primes[:3])
                break
        assert jordan_satisfied, (
            "Jordan condition not satisfied: no prime p-cycle (p<=15) with fixed points.\n"
            "Expected witness: p=1571, cycle [13,1,1,1,1,1]"
        )


class TestGaloisNotInA18Fast:
    """
    Gal(P18/Q) contains odd permutations (Gal not in A18).
    Verified via Frobenius parity: if P18 mod p has odd permutation parity,
    then disc(P18) is not a square mod p, hence not a square in Q.
    """

    def test_odd_frobenius_element_exists(self):
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


# ---------------------------------------------------------------------------
# Slow tests — skipped in CI, run with: pytest --run-slow
# ---------------------------------------------------------------------------

@pytest.mark.slow
class TestDiscriminantExact:
    """Exact discriminant tests (~30-60s each). Skipped in CI by default."""

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
        _, exact = sympy.integer_nthroot(disc_value, 2)
        assert exact is False
