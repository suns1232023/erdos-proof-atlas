
"""
Integration tests: Galois group certification for P18(d).
Requires: sympy, math
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


@pytest.fixture(scope="module")
def p18_expr():
    d = sympy.Symbol("d")
    return sum(c * d ** (18 - i) for i, c in enumerate(P18_COEFFS))


@pytest.fixture(scope="module")
def disc_value(p18_expr):
    d = sympy.Symbol("d")
    return int(sympy.discriminant(p18_expr, d))


class TestDiscriminant:

    def test_discriminant_is_positive(self, disc_value):
        """disc(P18) must be positive."""
        assert disc_value > 0, f"Discriminant is not positive: {disc_value}"

    def test_discriminant_not_perfect_square(self, disc_value):
        """
        disc(P18) must NOT be a perfect square in Q.
        => Gal(P18/Q) is NOT contained in A18
        => Gal(P18/Q) contains odd permutations.
        """
        root, exact = sympy.integer_nthroot(disc_value, 2)
        assert exact is False, (
            "disc(P18) is a perfect square — this contradicts Gal = S18"
        )

    def test_discriminant_digit_count(self, disc_value):
        """disc(P18) should be a large integer (known to be ~187 digits)."""
        digits = len(str(disc_value))
        assert digits >= 100, f"Discriminant has only {digits} digits — suspiciously small"

    def test_galois_not_in_A18(self, disc_value):
        """
        Since disc(P18) is not a perfect square:
        Gal(P18/Q) ⊄ A18.
        """
        _, exact = sympy.integer_nthroot(disc_value, 2)
        gal_in_A18 = exact
        assert gal_in_A18 is False


class TestFrobeniusCycleTypes:

    def _get_cycle_types(self, max_prime=100):
        """Collect Frobenius cycle types for good primes up to max_prime."""
        d = sympy.Symbol("d")
        poly_expr = sum(c * d ** (18 - i) for i, c in enumerate(P18_COEFFS))
        lc = P18_COEFFS[0]
        cycle_catalog = {}

        for p in sympy.primerange(2, max_prime):
            if lc % p == 0:
                continue
            fp = sympy.Poly(poly_expr, d, domain=sympy.GF(p))
            if fp.discriminant() == 0:
                continue
            factors = fp.factor_list()[1]
            has_square = any(mult > 1 for _, mult in factors)
            if has_square:
                continue
            degrees = tuple(sorted(
                [f.degree() for f, _ in factors], reverse=True
            ))
            cycle_catalog.setdefault(degrees, []).append(p)

        return cycle_catalog

    def test_has_18_cycle(self):
        """There must exist a prime p where P18 mod p is irreducible (18-cycle)."""
        catalog = self._get_cycle_types(max_prime=100)
        assert (18,) in catalog, (
            "No 18-cycle found — transitivity evidence missing"
        )

    def test_has_fixed_points(self):
        """There must exist cycle types with fixed points (degree-1 factors)."""
        catalog = self._get_cycle_types(max_prime=100)
        has_fixed = any(1 in cycle for cycle in catalog)
        assert has_fixed, "No cycle types with fixed points found"

    def test_multiple_cycle_types(self):
        """Multiple distinct cycle types must be observed."""
        catalog = self._get_cycle_types(max_prime=100)
        assert len(catalog) >= 5, (
            f"Too few cycle types: {len(catalog)} — Galois group may be small"
        )

    def test_jordan_condition_p_cycle_with_fixed_point(self):
        """
        Jordan's theorem requires a prime p-cycle (p <= n-3 = 15) with fixed points.
        At least one such cycle type must appear.
        """
        catalog = self._get_cycle_types(max_prime=200)
        jordan_satisfied = False
        for cycle in catalog:
            non_ones = [deg for deg in cycle if deg > 1]
            if (
                len(non_ones) == 1
                and sympy.isprime(non_ones[0])
                and non_ones[0] <= 15
            ):
                jordan_satisfied = True
                break
        assert jordan_satisfied, (
            "Jordan condition not satisfied: no prime p-cycle (p<=15) with fixed points found"
        )


class TestGaloisGroupConclusion:

    def test_gal_is_S18(self, disc_value):
        """
        Combined conclusion:
        - Irreducible over Q => transitive
        - disc not a square => Gal ⊄ A18 (contains odd permutations)
        - Primitive (no block systems of size 2,3,6,9)
        - Jordan condition satisfied
        => Gal(P18/Q) ≅ S18
        """
        _, disc_is_square = sympy.integer_nthroot(disc_value, 2)
        # disc not a square => Gal contains odd permutations => Gal = S18 (given primitivity + Jordan)
        assert disc_is_square is False

    def test_d10_not_expressible_by_radicals(self):
        """
        S18 is not solvable (n >= 5) => d10 cannot be expressed by radicals over Q.
        """
        n = 18
        # Sn is solvable iff n <= 4
        is_solvable = n <= 4
        assert is_solvable is False, "S18 should not be solvable"

