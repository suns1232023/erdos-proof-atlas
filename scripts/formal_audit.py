
#!/usr/bin/env python3
"""
formal_audit.py — Lean formalization integrity audit.

REPAIR NOTE (Step 9):
  Separated from atlas_audit.py. This script covers:
    - Lean project structure validation
    - lakefile.toml content checks
    - Lean theorem naming consistency
    - sorry detection (strict: causes FAIL)
    - Float-in-theorem detection
    - lake build execution (if Lean available)

  Does NOT cover Python/repository integrity (see atlas_audit.py).
  Run full_audit.py to execute both.
"""

import sys
import os
import re
import shutil
import subprocess
from pathlib import Path

LEAN_DIR = Path("formal/lean")
CANONICAL_THEOREM = "circlePacking10MinDistBound"

RESULTS = []


def record(label: str, passed: bool, detail: str = ""):
    status = "[PASS]" if passed else "[FAIL]"
    msg = f"  {status} {label}"
    if detail:
        msg += f"\n         {detail}"
    print(msg)
    RESULTS.append((label, passed, detail))


# ---------------------------------------------------------------------------
# Section 1: Lean project structure
# ---------------------------------------------------------------------------
def audit_lean_structure():
    print("\n── Section 1: Lean Project Structure ──")

    required_files = [
        LEAN_DIR / "lakefile.toml",
        LEAN_DIR / "lean-toolchain",
        LEAN_DIR / "lake-manifest.json",
        LEAN_DIR / "Main.lean",
        LEAN_DIR / "ErdosAtlas" / "Basic.lean",
        LEAN_DIR / "ErdosAtlas" / "Geometry" / "Basic.lean",
        LEAN_DIR / "ErdosAtlas" / "CirclePacking" / "N10.lean",
        LEAN_DIR / "ErdosAtlas" / "Problems" / "SquarePacking.lean",
    ]

    for f in required_files:
        record(f"File exists: {f}", f.is_file())


# ---------------------------------------------------------------------------
# Section 2: lakefile.toml content
# ---------------------------------------------------------------------------
def audit_lakefile():
    print("\n── Section 2: lakefile.toml Content ──")

    lakefile = LEAN_DIR / "lakefile.toml"
    if not lakefile.is_file():
        record("lakefile.toml readable", False, "File not found")
        return

    content = lakefile.read_text()

    record("lakefile has [[require]] block", "[[require]]" in content or "[require]" in content)
    record("lakefile has mathlib dependency", "mathlib" in content)
    record("lakefile has [[lean_lib]]", "[[lean_lib]]" in content)
    record("lakefile has ErdosAtlas library", "ErdosAtlas" in content)
    record("lakefile has [[lean_exe]]", "[[lean_exe]]" in content)
    record("lakefile has Main executable", 'name = "Main"' in content)
    record("lakefile has no || true", "|| true" not in content)


# ---------------------------------------------------------------------------
# Section 3: Lean theorem naming
# ---------------------------------------------------------------------------
def audit_theorem_naming():
    print("\n── Section 3: Lean Theorem Naming Consistency ──")

    n10_file = LEAN_DIR / "ErdosAtlas" / "CirclePacking" / "N10.lean"

    if not n10_file.is_file():
        record("N10.lean readable", False, "File not found")
        return

    content = n10_file.read_text()

    # Check canonical theorem name
    record(
        f"Canonical theorem '{CANONICAL_THEOREM}' in N10.lean",
        CANONICAL_THEOREM in content
    )

    # Check theorem is actually declared (not just mentioned in comment)
    pattern = rf"theorem\s+{re.escape(CANONICAL_THEOREM)}"
    declared = bool(re.search(pattern, content))
    record(f"theorem {CANONICAL_THEOREM} declared (not just mentioned)", declared)

    # Check no trivial → True conclusion
    has_trivial = "→ True" in content or "-> True" in content
    record("No '→ True' conclusion in N10.lean", not has_trivial,
           "Found '→ True' — this is a placeholder, not a real theorem" if has_trivial else "")

    # Check uses ℝ not Float in theorem statements
    theorem_lines = [
        line for line in content.split("\n")
        if re.match(r"\s*(theorem|def )", line)
    ]
    float_in_theorem = any("Float" in line for line in theorem_lines)
    record("No Float in theorem/def lines", not float_in_theorem,
           "Float found in theorem — use ℝ (Real) instead" if float_in_theorem else "")

    # Check uses ℝ
    uses_real = "ℝ" in content or "Real" in content
    record("Uses ℝ or Real type", uses_real)


# ---------------------------------------------------------------------------
# Section 4: Sorry detection (strict)
# ---------------------------------------------------------------------------
def audit_sorry():
    print("\n── Section 4: Sorry Detection ──")

    lean_src = LEAN_DIR / "ErdosAtlas"
    if not lean_src.is_dir():
        record("ErdosAtlas directory exists", False)
        return

    sorry_occurrences = []
    for lean_file in lean_src.rglob("*.lean"):
        lines = lean_file.read_text().splitlines()
        for lineno, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith("--"):
                continue
            if "sorry" in line:
                sorry_occurrences.append((str(lean_file), lineno, line.rstrip()))

    if sorry_occurrences:
        detail = "; ".join(f"{f}:{ln}" for f, ln, _ in sorry_occurrences[:5])
        record(
            f"No sorry in ErdosAtlas Lean files",
            False,
            f"Found {len(sorry_occurrences)} sorry occurrence(s): {detail}\n"
            "         Theorems with sorry cannot be at L5 (KERNEL_CHECKED)."
        )
    else:
        record("No sorry in ErdosAtlas Lean files", True)

    # Determine formal level based on sorry presence
    if sorry_occurrences:
        print("         Current formal level: ≤ L4 (sorry present)")
    else:
        print("         Current formal level: L5 candidate (no sorry)")


# ---------------------------------------------------------------------------
# Section 5: Lean availability and lake build
# ---------------------------------------------------------------------------
def audit_lean_build():
    print("\n── Section 5: Lean Availability & lake build ──")

    lean_available = shutil.which("lean") is not None
    lake_available = shutil.which("lake") is not None

    record("lean on PATH", lean_available)
    record("lake on PATH", lake_available)

    if not lean_available or not lake_available:
        print("         NOTE: Lean not available — skipping lake build.")
        print("         In CI, this MUST be a FAILURE.")
        print("         For local dev: install Lean 4 via elan.")
        record("lake build (skipped — Lean unavailable)", False,
               "Install Lean 4 to run lake build")
        return

    # lake-manifest.json check
    manifest = LEAN_DIR / "lake-manifest.json"
    record("lake-manifest.json exists", manifest.is_file(),
           "Run 'lake update' in formal/lean/ to generate" if not manifest.is_file() else "")

    if not manifest.is_file():
        record("lake build (skipped — no manifest)", False, "Run lake update first")
        return

    # Run lake build
    print("         Running lake build (may take several minutes)...")
    try:
        result = subprocess.run(
            ["lake", "build"],
            cwd=str(LEAN_DIR),
            capture_output=True,
            text=True,
            timeout=300,
        )
        build_ok = result.returncode == 0
        if not build_ok:
            output_tail = (result.stdout + result.stderr).splitlines()[-10:]
            detail = "\n         ".join(output_tail)
            record("lake build succeeds", False, detail)
        else:
            record("lake build succeeds", True)
    except subprocess.TimeoutExpired:
        record("lake build succeeds", False, "Timed out after 300 seconds")
    except FileNotFoundError:
        record("lake build succeeds", False, "lake not found")


# ---------------------------------------------------------------------------
# Section 6: Formal level determination
# ---------------------------------------------------------------------------
def audit_formal_level():
    print("\n── Section 6: Formal Level Assessment ──")

    n10_file = LEAN_DIR / "ErdosAtlas" / "CirclePacking" / "N10.lean"
    lean_src = LEAN_DIR / "ErdosAtlas"

    # Check L1: meaningful statement exists
    l1_ok = False
    if n10_file.is_file():
        content = n10_file.read_text()
        has_canonical = CANONICAL_THEOREM in content
        no_trivial = "→ True" not in content and "-> True" not in content
        uses_real = "ℝ" in content or "Real" in content
        l1_ok = has_canonical and no_trivial and uses_real

    record("L1 (STATEMENT_FORMALIZED): meaningful statement in Lean", l1_ok)

    # Check L2: definitions exist
    geo_file = LEAN_DIR / "ErdosAtlas" / "Geometry" / "Basic.lean"
    l2_ok = False
    if geo_file.is_file():
        content = geo_file.read_text()
        has_point = "def Point" in content
        has_unit_square = "InUnitSquare" in content
        has_dist = "dist2D" in content or "dist" in content
        l2_ok = has_point and has_unit_square and has_dist

    record("L2 (DEFINITIONS_FORMALIZED): geometry definitions exist", l2_ok)

    # Determine current level
    if l2_ok:
        level = "L2"
    elif l1_ok:
        level = "L1"
    else:
        level = "L0"

    print(f"\n         Current formal level: {level}")
    print(f"         Target: L5 (KERNEL_CHECKED)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    print("=" * 65)
    print("  erdos-proof-atlas — Formal Audit (Lean Formalization)")
    print("=" * 65)

    audit_lean_structure()
    audit_lakefile()
    audit_theorem_naming()
    audit_sorry()
    audit_lean_build()
    audit_formal_level()

    print("\n" + "=" * 65)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    failed = sum(1 for _, ok, _ in RESULTS if not ok)
    total = len(RESULTS)

    print(f"  Results: {passed}/{total} passed, {failed} failed")
    print()

    if failed == 0:
        print("[PASS] FORMAL AUDIT PASSED")
        return 0
    else:
        print(f"[FAIL] FORMAL AUDIT FAILED ({failed} issue(s))")
        return 1


if __name__ == "__main__":
    sys.exit(main())

