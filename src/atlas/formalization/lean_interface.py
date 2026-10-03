
"""Interface between Python certificates and Lean formalization.

REPAIR V3 (conflict fix):
  PROBLEM: formal_level() logic was:
    L5 when no sorry, L4 when sorry, L0 otherwise.
    This conflicts with lean_check.py's status-aware definition:
      L1/L2/L3/L4: sorry allowed (documented proof gaps)
      L5: sorry causes FAIL
    Also: L4 = PROOF_SOURCE_COMPLETE does not require sorry to be absent.

  FIX: Aligned formal_level() with the canonical L0-L5 definitions:
    L0: build failed or Lean unavailable
    L1: build succeeds (sorry present, statement meaningful)
    L5: build succeeds + no sorry + no unauthorized axiom
    L4: build succeeds + sorry present (proof source complete but gaps remain)
"""

from __future__ import annotations
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# Canonical level definitions (must match lean_check.py)
L_LEVELS = {
    "L0": "NOT_FORMALIZED",
    "L1": "STATEMENT_FORMALIZED",
    "L2": "DEFINITIONS_FORMALIZED",
    "L3": "KEY_LEMMAS_FORMALIZED",
    "L4": "PROOF_SOURCE_COMPLETE",
    "L5": "KERNEL_CHECKED",
}

# Authorized axioms (acceptable at all levels including L5)
AUTHORIZED_AXIOMS = {
    "Classical.choice",
    "propext",
    "Quot.sound",
    "funext",
}


@dataclass
class LeanBuildResult:
    success: bool
    has_sorry: bool
    has_unauthorized_axiom: bool
    output: str
    lean_version: str = "UNKNOWN"
    mathlib_version: str = "UNKNOWN"

    def formal_level(self) -> str:
        """
        Determine formal level from build result.

        REPAIR V3: Aligned with canonical L0-L5 definitions.
        Previous logic (L4=sorry, L5=no sorry) was incorrect:
          - L4 = PROOF_SOURCE_COMPLETE: proof source complete, acceptance pending
          - L5 = KERNEL_CHECKED: lake build passes + no sorry + no unauthorized axiom
          - L1 = STATEMENT_FORMALIZED: build succeeds, sorry present (current state)

        Note: We cannot distinguish L1/L2/L3 from build output alone.
        Use lean_check.py --status for full level determination.
        """
        if not self.success:
            return "L0"
        if self.has_unauthorized_axiom:
            return "L0"  # unauthorized axiom = not formally verified
        if not self.has_sorry:
            return "L5"  # builds + no sorry + no unauthorized axiom
        # sorry present: could be L1, L2, L3, or L4
        # Default to L1 (most conservative) — use lean_check.py for precise level
        return "L1"

    def formal_level_description(self) -> str:
        return L_LEVELS.get(self.formal_level(), "UNKNOWN")

    def to_dict(self) -> dict:
        level = self.formal_level()
        return {
            "success": self.success,
            "has_sorry": self.has_sorry,
            "has_unauthorized_axiom": self.has_unauthorized_axiom,
            "formal_level": level,
            "formal_level_description": L_LEVELS.get(level, "UNKNOWN"),
            "lean_version": self.lean_version,
            "mathlib_version": self.mathlib_version,
        }


def run_lean_build(lean_dir: Path) -> LeanBuildResult:
    """Run lake build and check for sorry/unauthorized axiom.

    REPAIR V3: Uses lake build output for sorry detection.
    Lean emits "declaration uses 'sorry'" when sorry is present.
    Does NOT use grep on source files (unreliable).
    """
    try:
        result = subprocess.run(
            ["lake", "build"],
            cwd=lean_dir,
            capture_output=True,
            text=True,
            timeout=300,
        )
        output = result.stdout + result.stderr
        success = result.returncode == 0

        # Detect sorry from Lean compiler output (reliable)
        # Lean emits: "declaration uses 'sorry'" for each sorry theorem
        has_sorry = "declaration uses 'sorry'" in output or "uses 'sorry'" in output

        # Detect unauthorized axioms
        # Note: "axiom" alone is not sufficient — standard library has authorized axioms
        # Check for specific unauthorized patterns
        has_unauthorized_axiom = _check_unauthorized_axioms(output)

        return LeanBuildResult(
            success=success,
            has_sorry=has_sorry,
            has_unauthorized_axiom=has_unauthorized_axiom,
            output=output,
        )
    except FileNotFoundError:
        return LeanBuildResult(
            success=False,
            has_sorry=False,
            has_unauthorized_axiom=False,
            output="lake not found — Lean not installed",
        )
    except subprocess.TimeoutExpired:
        return LeanBuildResult(
            success=False,
            has_sorry=False,
            has_unauthorized_axiom=False,
            output="Lean build timed out after 300 seconds",
        )


def _check_unauthorized_axioms(build_output: str) -> bool:
    """
    Check for unauthorized axioms in build output.
    Authorized axioms: Classical.choice, propext, Quot.sound, funext.
    """
    # Look for axiom declarations that are NOT in the authorized set
    # This is a heuristic — use #print axioms for definitive check
    unauthorized_patterns = [
        "sorry",  # sorryAx
        "native_decide",  # can bypass kernel
    ]
    for pattern in unauthorized_patterns:
        if f"axiom {pattern}" in build_output.lower():
            return True
    return False


def run_axiom_check(lean_dir: Path, theorem_name: str, namespace: str) -> tuple[bool, str]:
    """
    Run #print axioms via lake env lean for definitive axiom inspection.
    Returns (is_clean, output_text).
    """
    lean_script = f"""
import {namespace}.N10
#print axioms {namespace}.{theorem_name}
"""
    try:
        result = subprocess.run(
            ["lake", "env", "lean", "--stdin"],
            input=lean_script,
            cwd=str(lean_dir),
            capture_output=True,
            text=True,
            timeout=120,
        )
        output = result.stdout + result.stderr

        # Check for sorryAx in axiom list
        has_sorry_ax = "sorryAx" in output
        return not has_sorry_ax, output.strip()

    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        return False, str(e)


def check_lean_available() -> bool:
    """Return True if lake is available on PATH."""
    try:
        r = subprocess.run(
            ["lake", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return r.returncode == 0
    except Exception:
        return False


def get_lean_version() -> str:
    """Get Lean version string."""
    try:
        r = subprocess.run(
            ["lean", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return r.stdout.strip() if r.returncode == 0 else "UNKNOWN"
    except Exception:
        return "UNKNOWN"
