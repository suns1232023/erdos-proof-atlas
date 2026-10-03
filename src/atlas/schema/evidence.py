"""
Dual-axis evidence model.

Axis E: Computational evidence (E0-E5)
Axis L: Formal/Lean evidence (L0-L5)

A result is represented as (E-level, L-level), e.g. E5/L0 or E3/L5.
No automated component may silently upgrade either axis.
"""

from __future__ import annotations
from enum import IntEnum
from dataclasses import dataclass, field
from typing import Optional


class ComputationalEvidence(IntEnum):
    """E-axis: computational evidence level."""
    IDEA = 0
    NUMERICAL = 1
    COMPUTATIONAL = 2
    INDEPENDENTLY_VERIFIED = 3
    EXACTIFIED = 4
    SYMBOLICALLY_CERTIFIED = 5

    def label(self) -> str:
        return f"E{self.value}"

    def description(self) -> str:
        return {
            0: "Idea or conjecture",
            1: "Numerical result (not a proof)",
            2: "Computational result",
            3: "Independently verified computationally",
            4: "Exactified (exact algebraic form)",
            5: "Symbolically certified (algebraic certificate)",
        }[self.value]


class FormalEvidence(IntEnum):
    """L-axis: formal/Lean evidence level."""
    NOT_FORMALIZED = 0
    STATEMENT_FORMALIZED = 1
    DEFINITIONS_FORMALIZED = 2
    KEY_LEMMAS_FORMALIZED = 3
    THEOREM_PROVED = 4
    LEAN_BUILD_VERIFIED = 5

    def label(self) -> str:
        return f"L{self.value}"

    def description(self) -> str:
        return {
            0: "Not formalized",
            1: "Statement formalized in Lean",
            2: "Definitions formalized",
            3: "Key lemmas formalized",
            4: "Theorem proved (may use sorry)",
            5: "Lean build verified (no sorry, no axiom)",
        }[self.value]

    def is_formally_proved(self) -> bool:
        """Only L5 (no sorry, no axiom) counts as formally proved."""
        return self == FormalEvidence.LEAN_BUILD_VERIFIED


@dataclass
class EvidenceStatus:
    """Combined evidence status for a mathematical result."""
    computational: ComputationalEvidence
    formal: FormalEvidence
    notes: str = ""

    def label(self) -> str:
        return f"{self.computational.label()}/{self.formal.label()}"

    def is_theorem(self) -> bool:
        """Only E5/L5 with no sorry qualifies as formally proved."""
        return (
            self.computational >= ComputationalEvidence.SYMBOLICALLY_CERTIFIED
            and self.formal == FormalEvidence.LEAN_BUILD_VERIFIED
        )

    def is_formally_proved(self) -> bool:
        """Alias for is_theorem() — only L5 qualifies."""
        return self.formal.is_formally_proved()

    def to_dict(self) -> dict:
        return {
            "computational": self.computational.name,
            "computational_label": self.computational.label(),
            "computational_description": self.computational.description(),
            "formal": self.formal.name,
            "formal_label": self.formal.label(),
            "formal_description": self.formal.description(),
            "combined": self.label(),
            "is_formally_proved": self.is_formally_proved(),
            "notes": self.notes,
        }


# Forbidden auto-upgrades (enforced in code)
_FORBIDDEN_UPGRADES: list[tuple[str, str]] = [
    ("NUMERICAL", "THEOREM"),
    ("COMPUTATIONAL", "THEOREM"),
    ("AI_GENERATED", "VERIFIED"),
    ("CERTIFICATE", "FORMAL_PROOF"),
    ("GITHUB_ACTIONS_PASS", "EPISTEMIC_STATUS_CHANGE"),
]


def validate_upgrade(from_status: str, to_status: str) -> None:
    """Raise ValueError if upgrade is forbidden."""
    for forbidden_from, forbidden_to in _FORBIDDEN_UPGRADES:
        if from_status == forbidden_from and to_status == forbidden_to:
            raise ValueError(
                f"FORBIDDEN: Cannot auto-upgrade {from_status} -> {to_status}. "
                "This requires actual formal evidence."
            )
