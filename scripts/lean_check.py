#!/usr/bin/env python3
"""Check Lean build status."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from atlas.formalization.lean_interface import run_lean_build, check_lean_available

def main() -> int:
    lean_dir = Path("formal/lean")
    if not check_lean_available():
        print("[lean] Lean/lake not installed. Formal level: L0")
        print("[lean] Install Lean 4: https://leanprover.github.io/lean4/doc/setup.html")
        return 0  # Not a failure — just not installed
    result = run_lean_build(lean_dir)
    print(f"[lean] Build success: {result.success}")
    print(f"[lean] Has sorry: {result.has_sorry}")
    print(f"[lean] Formal level: {result.formal_level()}")
    if not result.success:
        print(f"[lean] Output: {result.output[:500]}")
        return 1
    return 0

if __name__ == "__main__": sys.exit(main())
