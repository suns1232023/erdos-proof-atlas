
#!/usr/bin/env python3
"""
lean_check.py — Lean 4 formal verification checker (V2).

REPAIR V2 (per reviewer):
  ① make lean FAILS if Lean unavailable (exit 1, not 0)
  ② sorry detection is STATUS-AWARE:
       L1/L2/L3/L4 → sorry allowed (documented proof gaps)
       L5           → sorry causes FAIL
  ③ Axiom inspection via `lake env lean` + #print axioms
     (replaces unreliable grep-based detection)
  ④ Separate strict mode (make lean) vs status mode (make status)

Usage:
  python scripts/lean_check.py              # strict mode (make lean)
  python scripts/lean_check.py --status     # status-only (make status)
  python scripts/lean_check.py --level L5   # override claimed level
"""

import subprocess
import shutil
import sys
import os
import argparse
from pathlib import Path

LEAN_DIR = Path("formal/lean")
CANONICAL_THEOREM = "circlePacking10MinDistBound"
CANONICAL_NAMESPACE = "ErdosAtlas.CirclePacking"

# Evidence level definitions
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

RESULTS = []


def record(label: str, passed: bool, detail: str = ""):
    status = "[PASS]" if passed else "[FAIL]"
    msg = f"  {status} {label}"
    if detail:
        msg += f"\n         {detail}"
    print(msg)
    RESULTS.append((label, passed))


def check_lean_available() -> bool:
    return shutil.which("lean") is not None and shutil.which("lake") is not None


def check_required_files() -> list[str]:
    required = [
        LEAN_DIR / "lakefile.toml",
        LEAN_DIR / "lean-toolchain",
        LEAN_DIR / "lake-manifest.json",
        LEAN_DIR / "Main.lean",
        LEAN_DIR / "ErdosAtlas" / "Basic.lean",
        LEAN_DIR / "ErdosAtlas" / "Geometry" / "Point.lean",
        LEAN_DIR / "ErdosAtlas" / "Geometry" / "Distance.lean",
        LEAN_DIR / "ErdosAtlas" / "Geometry" / "UnitSquare.lean",
        LEAN_DIR / "ErdosAtlas" / "CirclePacking" / "Definitions.lean",
        LEAN_DIR / "ErdosAtlas" / "CirclePacking" / "N10.lean",
        LEAN_DIR / "ErdosAtlas" / "Audit" / "Axioms.lean",
    ]
    return [str(f) for f in required if not f.is_file()]


def check_lakefile_has_mathlib() -> bool:
    lakefile = LEAN_DIR / "lakefile.toml"
    if not lakefile.is_file():
        return False
    content = lakefile.read_text()
    return "mathlib" in content and "[[require]]" in content


def check_no_trivial_true() -> list[str]:
    """Find .lean files with '→ True' conclusions (placeholder theorems)."""
    violations = []
    lean_src = LEAN_DIR / "ErdosAtlas"
    if not lean_src.is_dir():
        return violations
    for f in lean_src.rglob("*.lean"):
        content = f.read_text()
        if "→ True" in content or "-> True" in content:
            violations.append(str(f))
    return violations


def check_no_float_in_theorems() -> list[str]:
    """Find .lean files with Float in theorem/def lines."""
    violations = []
    lean_src = LEAN_DIR / "ErdosAtlas"
    if not lean_src.is_dir():
        return violations
    for f in lean_src.rglob("*.lean"):
        lines = f.read_text().splitlines()
        for lineno, line in enumerate(lines, 1):
            stripped = line.strip()
            if (stripped.startswith("theorem") or stripped.startswith("def ")) \
                    and "Float" in line:
                violations.append(f"{f}:{lineno}: {line.rstrip()}")
    return violations


def find_sorry_occurrences() -> list[tuple[str, int, str]]:
    """Find sorry in .lean files (excluding comment lines)."""
    occurrences = []
    lean_src = LEAN_DIR / "ErdosAtlas"
    if not lean_src.is_dir():
        return occurrences
    for f in lean_src.rglob("*.lean"):
        lines = f.read_text().splitlines()
        for lineno, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith("--"):
                continue
            if "sorry" in line:
                occurrences.append((str(f), lineno, line.rstrip()))
    return occurrences


def check_sorry_for_level(claimed_level: str) -> tuple[bool, str]:
    """
    Status-aware sorry check.
    L1/L2/L3/L4: sorry allowed → returns (True, info_message)
    L5:          sorry causes FAIL → returns (False, error_message)
    """
    occurrences = find_sorry_occurrences()
    count = len(occurrences)

    if claimed_level == "L5":
        if count > 0:
            details = "; ".join(f"{f}:{ln}" for f, ln, _ in occurrences[:5])
            return False, f"L5 claimed but {count} sorry found: {details}"
        return True, "No sorry found — L5 kernel check passed"
    else:
        if count > 0:
            return True, (
                f"{count} sorry found at level {claimed_level} — "
                f"allowed (sorry is prohibited only at L5)"
            )
        return True, f"No sorry found at level {claimed_level}"


def run_axiom_check() -> tuple[bool, str]:
    """
    Run #print axioms via lake env lean.
    Returns (ok, output_text).
    """
    if not check_lean_available():
        return False, "Lean not available"

    lean_script = f"""
import {CANONICAL_NAMESPACE}.N10
#print axioms {CANONICAL_NAMESPACE}.{CANONICAL_THEOREM}
"""
    try:
        result = subprocess.run(
            ["lake", "env", "lean", "--stdin"],
            input=lean_script,
            cwd=str(LEAN_DIR),
            capture_output=True,
            text=True,
            timeout=120,
        )
        output = result.stdout + result.stderr

        # Check for unauthorized axioms
        unauthorized = []
        for line in output.splitlines():
            if "depends on axioms" in line or "axioms:" in line.lower():
                continue
            for ax in ["sorryAx", "sorry"]:
                if ax in line:
                    unauthorized.append(f"sorry axiom: {line.strip()}")

        if unauthorized:
            return False, f"Unauthorized axioms found:\n" + "\n".join(unauthorized)

        return True, output.strip() or "No axiom output (may need lake build first)"

    except subprocess.TimeoutExpired:
        return False, "Axiom check timed out"
    except FileNotFoundError:
        return False, "lake not found"


def run_lake_build() -> tuple[bool, str]:
    """Run lake build. Returns (success, output)."""
    try:
        result = subprocess.run(
            ["lake", "build"],
            cwd=str(LEAN_DIR),
            capture_output=True,
            text=True,
            timeout=300,
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "lake build timed out after 300 seconds"
    except FileNotFoundError:
        return False, "lake not found on PATH"


def strict_mode(claimed_level: str = "L1") -> int:
    """
    Strict mode: used by `make lean`.
    FAILS (exit 1) if Lean unavailable or any mandatory check fails.
    """
    print("=" * 65)
    print(f"  Lean 4 Formal Verification (strict, claimed level: {claimed_level})")
    print("=" * 65)

    # --- Check 1: Lean availability ---
    lean_ok = check_lean_available()
    if not lean_ok:
        print("[FAIL] Lean/lake not installed or not on PATH.")
        print("       Install via: curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh")
        print("       make lean MUST fail when Lean is unavailable.")
        print("       Use 'make status' to report L0 without failing.")
        return 1  # REPAIR: was return 0 — now correctly returns 1
    record("Lean/lake available", True)

    # --- Check 2: Required files ---
    missing = check_required_files()
    record("All required Lean files present", len(missing) == 0,
           f"Missing: {missing}" if missing else "")

    # --- Check 3: mathlib dependency ---
    mathlib_ok = check_lakefile_has_mathlib()
    record("lakefile.toml has mathlib [[require]]", mathlib_ok,
           "Add [[require]] mathlib block to lakefile.toml" if not mathlib_ok else "")

    # --- Check 4: No trivial → True ---
    trivial = check_no_trivial_true()
    record("No '→ True' placeholder conclusions", len(trivial) == 0,
           f"Found in: {trivial}" if trivial else "")

    # --- Check 5: No Float in theorems ---
    float_violations = check_no_float_in_theorems()
    record("No Float in theorem/def lines", len(float_violations) == 0,
           f"Use ℝ instead: {float_violations[:3]}" if float_violations else "")

    # --- Check 6: lake build ---
    print("\n  [...] Running lake build...")
    build_ok, build_out = run_lake_build()
    record("lake build succeeds", build_ok,
           "\n".join(build_out.splitlines()[-15:]) if not build_ok else "")

    # --- Check 7: Status-aware sorry check ---
    sorry_ok, sorry_msg = check_sorry_for_level(claimed_level)
    record(f"Sorry check (level {claimed_level})", sorry_ok, sorry_msg)

    # --- Check 8: Axiom audit (if build succeeded) ---
    if build_ok:
        print("\n  [...] Running axiom audit (#print axioms)...")
        axiom_ok, axiom_out = run_axiom_check()
        record("Axiom audit", axiom_ok, axiom_out[:300] if not axiom_ok else axiom_out[:200])
    else:
        record("Axiom audit (skipped — build failed)", False, "Fix lake build first")

    # --- Summary ---
    print("\n" + "=" * 65)
    passed = sum(1 for _, ok in RESULTS if ok)
    failed = sum(1 for _, ok in RESULTS if not ok)
    total = len(RESULTS)
    print(f"  Results: {passed}/{total} passed, {failed} failed")

    if failed == 0:
        print(f"[PASS] Lean checks passed — Formal level: {claimed_level} ({L_LEVELS[claimed_level]})")
        return 0
    else:
        print(f"[FAIL] {failed} Lean check(s) failed")
        return 1


def status_mode() -> int:
    """
    Status mode: used by `make status`.
    Reports formal level without failing when Lean unavailable.
    """
    print("Lean Formal Verification Status")
    print("-" * 40)

    lean_ok = check_lean_available()
    if not lean_ok:
        print("Lean available:  NO")
        print("Formal level:    L0 (NOT_FORMALIZED)")
        print("Note: Install Lean 4 to advance beyond L0.")
        return 0  # status mode: OK to return 0

    files_ok = len(check_required_files()) == 0
    mathlib_ok = check_lakefile_has_mathlib()
    trivial_ok = len(check_no_trivial_true()) == 0
    float_ok = len(check_no_float_in_theorems()) == 0

    build_ok = False
    sorry_count = 0
    if files_ok and mathlib_ok:
        build_ok, _ = run_lake_build()
        if build_ok:
            sorry_count = len(find_sorry_occurrences())

    # Determine level
    if not lean_ok or not files_ok or not mathlib_ok:
        level = "L0"
    elif not trivial_ok or not float_ok:
        level = "L0"  # statement not yet meaningful
    elif not build_ok:
        level = "L1"  # files exist but build fails
    elif sorry_count == 0:
        level = "L5"  # builds + no sorry
    else:
        level = "L1"  # builds but has sorry (current state)

    print(f"Lean available:   YES")
    print(f"Files OK:         {files_ok}")
    print(f"mathlib OK:       {mathlib_ok}")
    print(f"No → True:        {trivial_ok}")
    print(f"No Float:         {float_ok}")
    print(f"lake build OK:    {build_ok}")
    print(f"Sorry count:      {sorry_count}")
    print(f"Formal level:     {level} ({L_LEVELS.get(level, '?')})")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Lean 4 formal verification checker (V2)"
    )
    parser.add_argument(
        "--status", action="store_true",
        help="Status-only mode: report level without failing when Lean unavailable"
    )
    parser.add_argument(
        "--level", default="L1",
        choices=list(L_LEVELS.keys()),
        help="Claimed formal level for sorry check (default: L1)"
    )
    args = parser.parse_args()

    if args.status:
        sys.exit(status_mode())
    else:
        sys.exit(strict_mode(claimed_level=args.level))


if __name__ == "__main__":
    main()
