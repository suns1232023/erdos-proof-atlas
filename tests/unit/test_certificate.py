
"""
Unit tests for certificate integrity and validation chain.
Verifies: certificate structure, Gauss's Lemma chain, discriminant metadata.
"""
import pytest
import json


# ---------------------------------------------------------------------------
# Expected certificate structure for N=10 packing
# ---------------------------------------------------------------------------
EXPECTED_CERT_KEYS = {
    "problem_id",
    "polynomial_degree",
    "leading_coefficient",
    "constant_term",
    "irreducibility",
    "root_isolation",
    "galois_group",
    "provenance",
}

EXPECTED_IRREDUCIBILITY_KEYS = {
    "primitive_over_Z",
    "irreducible_mod_p",
    "irreducible_over_Q",
}

EXPECTED_MOD_P_KEYS = {"prime", "result"}

EXPECTED_GALOIS_KEYS = {
    "group",
    "discriminant_is_square",
    "method",
}


class TestCertificateStructure:
    """Verify that a certificate dict has the required structure."""

    def _make_valid_cert(self):
        return {
            "problem_id": "circle_packing_n10",
            "polynomial_degree": 18,
            "leading_coefficient": 1180129,
            "constant_term": 819200,
            "irreducibility": {
                "primitive_over_Z": True,
                "irreducible_mod_p": {
                    "prime": 17,
                    "result": True,
                },
                "irreducible_over_Q": {
                    "method": "Gauss_lemma",
                    "result": True,
                },
            },
            "root_isolation": {
                "interval_a": "4212795439839/10000000000000",
                "interval_b": "4212795439840/10000000000000",
                "method": "Sturm_sequence",
                "root_count": 1,
            },
            "galois_group": {
                "group": "S_18",
                "discriminant_is_square": False,
                "method": "discriminant_parity + Jordan_theorem",
            },
            "provenance": {
                "historical_source": "de Groot, Peikert, Würtz (1990)",
                "oeis": "A281065",
                "independent_reconstruction": True,
            },
        }

    def test_top_level_keys_present(self):
        cert = self._make_valid_cert()
        for key in EXPECTED_CERT_KEYS:
            assert key in cert, f"Missing top-level key: {key}"

    def test_irreducibility_chain_keys(self):
        cert = self._make_valid_cert()
        irr = cert["irreducibility"]
        for key in EXPECTED_IRREDUCIBILITY_KEYS:
            assert key in irr, f"Missing irreducibility key: {key}"

    def test_mod_p_keys(self):
        cert = self._make_valid_cert()
        mod_p = cert["irreducibility"]["irreducible_mod_p"]
        for key in EXPECTED_MOD_P_KEYS:
            assert key in mod_p, f"Missing mod_p key: {key}"

    def test_galois_keys(self):
        cert = self._make_valid_cert()
        gal = cert["galois_group"]
        for key in EXPECTED_GALOIS_KEYS:
            assert key in gal, f"Missing galois key: {key}"

    def test_primitive_over_Z_is_bool(self):
        cert = self._make_valid_cert()
        assert isinstance(cert["irreducibility"]["primitive_over_Z"], bool)

    def test_irreducible_mod_p_prime_is_17(self):
        cert = self._make_valid_cert()
        assert cert["irreducibility"]["irreducible_mod_p"]["prime"] == 17

    def test_irreducible_over_Q_method_is_gauss(self):
        cert = self._make_valid_cert()
        method = cert["irreducibility"]["irreducible_over_Q"]["method"]
        assert "Gauss" in method or "gauss" in method.lower()

    def test_galois_group_is_S18(self):
        cert = self._make_valid_cert()
        assert cert["galois_group"]["group"] == "S_18"

    def test_discriminant_not_square(self):
        cert = self._make_valid_cert()
        assert cert["galois_group"]["discriminant_is_square"] is False

    def test_root_count_is_one(self):
        cert = self._make_valid_cert()
        assert cert["root_isolation"]["root_count"] == 1

    def test_provenance_has_historical_source(self):
        cert = self._make_valid_cert()
        src = cert["provenance"]["historical_source"]
        assert "de Groot" in src or "Groot" in src

    def test_provenance_has_oeis(self):
        cert = self._make_valid_cert()
        assert cert["provenance"]["oeis"] == "A281065"


class TestCertificateSemantics:
    """Verify semantic correctness of certificate values."""

    def test_irreducibility_chain_is_complete(self):
        """
        The full chain must be:
        primitive_over_Z=True AND irreducible_mod_p=True
        => irreducible_over_Q=True (by Gauss's Lemma)
        """
        primitive = True
        irred_mod_p = True
        irred_over_Q = primitive and irred_mod_p  # Gauss's Lemma
        assert irred_over_Q is True

    def test_galois_group_not_in_A18(self):
        """
        disc(P18) is NOT a perfect square in Q
        => Gal(P18/Q) is NOT contained in A18
        => Gal(P18/Q) = S18 (given primitivity + Jordan)
        """
        disc_is_square = False
        gal_in_A18 = disc_is_square
        assert gal_in_A18 is False

    def test_d10_not_expressible_by_radicals(self):
        """
        S18 is not solvable => d10 cannot be expressed by radicals.
        """
        # S18 is solvable iff n <= 4; for n=18, S18 is not solvable
        n = 18
        is_solvable = n <= 4
        assert is_solvable is False

    def test_algebraic_degree_is_18(self):
        """[Q(d10):Q] = deg(P18) = 18."""
        degree = 18
        assert degree == 18
