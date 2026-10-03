"""Interface between Python certificates and Lean formalization."""

from __future__ import annotations
import json, subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class LeanBuildResult:
    success: bool
    has_sorry: bool
    has_axiom: bool
    output: str
    lean_version: str = "UNKNOWN"
    mathlib_version: str = "UNKNOWN"

    def formal_level(self) -> str:
        if self.success and not self.has_sorry and not self.has_axiom:
            return "L5"
        elif self.success and self.has_sorry:
            return "L4"
        else:
            return "L0"

    def to_dict(self) -> dict:
        return {"success": self.success, "has_sorry": self.has_sorry, "has_axiom": self.has_axiom,
                "formal_level": self.formal_level(), "lean_version": self.lean_version,
                "mathlib_version": self.mathlib_version}


def run_lean_build(lean_dir: Path) -> LeanBuildResult:
    """Run lake build and check for sorry/axiom."""
    try:
        result = subprocess.run(["lake", "build"], cwd=lean_dir, capture_output=True, text=True, timeout=300)
        output = result.stdout + result.stderr
        success = result.returncode == 0
        has_sorry = "sorry" in output.lower() or "declaration uses 'sorry'" in output
        has_axiom = "axiom" in output.lower()
        return LeanBuildResult(success=success, has_sorry=has_sorry, has_axiom=has_axiom, output=output)
    except FileNotFoundError:
        return LeanBuildResult(success=False, has_sorry=False, has_axiom=False,
                               output="lake not found — Lean not installed")
    except subprocess.TimeoutExpired:
        return LeanBuildResult(success=False, has_sorry=False, has_axiom=False, output="Lean build timed out")


def check_lean_available() -> bool:
    try:
        r = subprocess.run(["lake", "--version"], capture_output=True, text=True, timeout=10)
        return r.returncode == 0
    except Exception:
        return False
