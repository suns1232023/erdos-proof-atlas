
"""
Dual-axis evidence model.

Axis E: Computational evidence (E0-E5)
Axis L: Formal/Lean evidence (L0-L5)

A result is represented as (E-level, L-level), e.g. E5/L0 or E3/L5.
No automated component may silently upgrade either axis.

REPAIR V5: Aligned FormalEvidence enum names with canonical L0-L5 definitions:
  OLD (wrong):  THEOREM_PROVED (L4), LEAN_BUILD_VERIFIED (L5)
  NEW (correct): PROOF_SOURCE_COMPLETE (L4), KERNEL_CHECKED (L5)
  This matches lean_check.py, lean_interface.py, and all documentation.
"""

from __future__ import annotations
from enum import IntEnum
from dataclasses import dataclass
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
    """
    L-axis: formal/Lean evidence level.

    REPAIR V5: Canonical names aligned with lean_check.py and documentation:
      L0 NOT_FORMALIZED          — no Lean formalization
      L1 STATEMENT_FORMALIZED    — mathematically meaningful statement in Lean
      L2 DEFINITIONS_FORMALIZED  — all definitions in Lean
      L3 KEY_LEMMAS_FORMALIZED   — key supporting lemmas in Lean
      L4 PROOF_SOURCE_COMPLETE   — proof source complete, acceptance checks pending
      L5 KERNEL_CHECKED          — lake build passes, no sorry, no unauthorized axiom
    """
    NOT_FORMALIZED = 0
    STATEMENT_FORMALIZED = 1
    DEFINITIONS_FORMALIZED = 2
    KEY_LEMMAS_FORMALIZED = 3
    PROOF_SOURCE_COMPLETE = 4   # REPAIR: was THEOREM_PROVED (misleading — sorry allowed)
    KERNEL_CHECKED = 5          # REPAIR: was LEAN_BUILD_VERIFIED

    def label(self) -> str:
        return f"L{self.value}"

    def description(self) -> str:
        return {
            0: "Not formalized",
            1: "Statement formalized in Lean (mathematically meaningful)",
            2: "Definitions formalized in Lean",
            3: "Key lemmas formalized in Lean",
            4: "Proof source complete (sorry may be present; acceptance checks pending)",
            5: "Kernel checked: lake build passes, no sorry, no unauthorized axiom",
        }[self.value]

    def sorry_allowed(self) -> bool:
        """
        Sorry is allowed at L1-L4 (documented proof gaps).
        Sorry is PROHIBITED at L5 (KERNEL_CHECKED).
        """
        return self.value < 5

    def is_kernel_checked(self) -> bool:
        """Only L5 (KERNEL_CHECKED) means lake build passes with no sorry."""
        return self == FormalEvidence.KERNEL_CHECKED

    # Backward compatibility aliases
    @classmethod
    def THEOREM_PROVED(cls) -> "FormalEvidence":
        """Deprecated alias for PROOF_SOURCE_COMPLETE (L4)."""
        return cls.PROOF_SOURCE_COMPLETE

    @classmethod
    def LEAN_BUILD_VERIFIED(cls) -> "FormalEvidence":
        """Deprecated alias for KERNEL_CHECKED (L5)."""
        return cls.KERNEL_CHECKED


@dataclass
class EvidenceStatus:
    """Combined evidence status for a mathematical result."""
    computational: ComputationalEvidence
    formal: FormalEvidence
    notes: str = ""

    def label(self) -> str:
        return f"{self.computational.label()}/{self.formal.label()}"

    def is_kernel_checked(self) -> bool:
        """Only E5/L5 with no sorry qualifies as kernel-checked."""
        return (
            self.computational >= ComputationalEvidence.SYMBOLICALLY_CERTIFIED
            and self.formal == FormalEvidence.KERNEL_CHECKED
        )

    def sorry_allowed(self) -> bool:
        """Sorry is allowed at L1-L4, prohibited at L5."""
        return self.formal.sorry_allowed()

    def to_dict(self) -> dict:
        return {
            "computational": self.computational.name,
            "computational_label": self.computational.label(),
            "computational_description": self.computational.description(),
            "formal": self.formal.name,
            "formal_label": self.formal.label(),
            "formal_description": self.formal.description(),
            "combined": self.label(),
            "sorry_allowed": self.sorry_allowed(),
            "is_kernel_checked": self.is_kernel_checked(),
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
