"""Certificate system with cryptographic hashing."""

from __future__ import annotations
import hashlib, json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class PolynomialCertificate:
    polynomial_str: str
    degree: int
    variable: str
    content: int
    coefficients: list[int]
    irreducible_status: str
    irreducible_method: str
    root_interval_lower: str
    root_interval_upper: str
    target_root_approx: str
    residual: str
    source: str
    historical_note: str = ""
    status: str = "SYMBOLICALLY_CERTIFIED"

    def to_dict(self) -> dict:
        return {"polynomial": self.polynomial_str, "degree": self.degree, "variable": self.variable,
                "content": self.content, "coefficients": self.coefficients,
                "irreducible": {"status": self.irreducible_status, "method": self.irreducible_method},
                "root_interval": [self.root_interval_lower, self.root_interval_upper],
                "target_root": self.target_root_approx, "residual": self.residual,
                "source": self.source, "historical_note": self.historical_note, "status": self.status}

    def sha256(self) -> str:
        return hashlib.sha256(json.dumps(self.to_dict(), sort_keys=True).encode()).hexdigest()

    def save(self, path: Path) -> None:
        d = self.to_dict()
        d["certificate_hash"] = self.sha256()
        path.write_text(json.dumps(d, indent=2))


@dataclass
class GaloisCertificate:
    polynomial_id: str
    degree: int
    irreducible: bool
    discriminant_positive: Optional[bool]
    discriminant_is_square: Optional[bool]
    discriminant_digits: Optional[int]
    factorization_mod_primes: list[dict]
    jordan_cycle_types: int
    primitivity_evidence: str
    group_claim: str
    method: str
    radical_solvable: Optional[bool]
    radical_solvability_source: str
    status: str = "SYMBOLICALLY_CERTIFIED"
    notes: str = ""

    def __post_init__(self) -> None:
        if self.status in ("THEOREM", "FORMAL_PROOF"):
            raise ValueError(f"GaloisCertificate cannot have status {self.status}. Use SYMBOLICALLY_CERTIFIED.")

    def to_dict(self) -> dict:
        return {"polynomial": self.polynomial_id, "degree": self.degree, "irreducible": self.irreducible,
                "discriminant": {"positive": self.discriminant_positive, "is_perfect_square": self.discriminant_is_square,
                                 "digits": self.discriminant_digits},
                "factorization_mod_primes": self.factorization_mod_primes,
                "jordan_cycle_types_count": self.jordan_cycle_types,
                "primitivity_evidence": self.primitivity_evidence,
                "group_claim": self.group_claim, "method": self.method,
                "radical_solvable": self.radical_solvable,
                "radical_solvability_source": self.radical_solvability_source,
                "status": self.status, "notes": self.notes}

    def sha256(self) -> str:
        return hashlib.sha256(json.dumps(self.to_dict(), sort_keys=True).encode()).hexdigest()

    def save(self, path: Path) -> None:
        d = self.to_dict()
        d["certificate_hash"] = self.sha256()
        path.write_text(json.dumps(d, indent=2))
