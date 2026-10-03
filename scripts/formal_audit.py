
#!/usr/bin/env python3
"""
formal_audit.py — Lean formalization integrity audit.

REPAIR V9:
  - Uses lean_text for ALL comment-stripped checks (including /- -/ block comments)
  - Scans all .lean files with rglob (not just N10.lean)
  - Formal level determination is monotone: L2 requires L1 to pass first
  - l2_ok checks real definitions (structure Point, def squaredDist, def IsPacking)
"""

import sys
import re
import shutil
import subprocess
from pathlib import Path

_scripts_dir = Path(__file__).parent
sys.path.insert(0, str(_scripts_dir))
try:
    from lean_text import (
        lean_file_has_theorem,
        lean_file_has_conflicting_point_def,
        lean_file_has_trivial_true,
        lean_file_has_float_in_theorem,
        lean_files_with_trivial_true,
        find_sorry_in_lean_files,
        strip_lean_comments,
    )
    LEAN_TEXT_OK = True
except ImportError:
    LEAN_TEXT_OK = False

LEAN_DIR = Path("formal/lean")
CANONICAL_THEOREM = "circlePacking10MinDistBound"
CURRENT_FORMAL_LEVEL = "L1"

RESULTS = []


def record(label: str, passed: bool, detail: str = ""):
    status = "[PASS]" if passed else "[FAIL]"
    msg = f"  {status} {label}"
    if detail:
        msg += f"\n         {detail}"
    print(msg)
    RESULTS.append((label, passed, detail))


def _strip(text: str) -> str:
    """Strip comments using lean_text if available, else strip -- lines."""
    if LEAN_TEXT_OK:
        from lean_text import strip_lean_comments
        return strip_lean_comments(text)
    return "\n".join(
        l for l in text.splitlines() if not l.strip().startswith("--")
    )


# ---------------------------------------------------------------------------
# Section 1: Lean project structure
# ---------------------------------------------------------------------------
def audit_lean_structure():
    print("\n── Section 1: Lean Project Structure ──")

    required_files = [
        LEAN_DIR / "lakefile.toml",
        LEAN_DIR / "lean-toolchain",
        LEAN_DIR / "lake-manifest.json",
        LEAN_DIR / "ErdosAtlas" / "Basic.lean",
        LEAN_DIR / "ErdosAtlas" / "Geometry" / "Basic.lean",
        LEAN_DIR / "ErdosAtlas" / "CirclePacking" / "N10.lean",
    ]
    for f in required_files:
        record(f"File exists: {f}", f.is_file())

    # Main.lean: strict check (main.lean lowercase is a real error)
    main_upper = (LEAN_DIR / "Main.lean").is_file()
    main_lower = (LEAN_DIR / "main.lean").is_file()
    if main_upper:
        record("Main.lean exists (correct case)", True)
    elif main_lower:
        record("Main.lean exists (correct case)", False,
               "Found 'main.lean' (lowercase). Fix: git mv formal/lean/main.lean formal/lean/Main.lean")
    else:
        record("Main.lean exists", False, "Neither Main.lean nor main.lean found")


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
    record("lakefile has [[require]] block", "[[require]]" in content)
    record("lakefile has mathlib dependency", "mathlib" in content)
    record("lakefile has [[lean_lib]]", "[[lean_lib]]" in content)
    record("lakefile has ErdosAtlas library", "ErdosAtlas" in content)

    # TOML requires # comments, not -- comments
    dash_comments = [l for l in content.splitlines() if l.strip().startswith("--")]
    record("lakefile uses # comments (not --)", len(dash_comments) == 0,
           f"Found {len(dash_comments)} '--' comment lines — TOML requires '#'" if dash_comments else "")

    record("lakefile has no bare || true", "|| true" not in content)


# ---------------------------------------------------------------------------
# Section 3: Lean theorem naming (scans ALL .lean files)
# ---------------------------------------------------------------------------
def audit_theorem_naming():
    print("\n── Section 3: Lean Theorem Naming (all .lean files) ──")

    n10_file = LEAN_DIR / "ErdosAtlas" / "CirclePacking" / "N10.lean"
    lean_src = LEAN_DIR / "ErdosAtlas"

    if not n10_file.is_file():
        record("N10.lean readable", False, "File not found")
        return

    # Canonical theorem declared
    if LEAN_TEXT_OK:
        declared = lean_file_has_theorem(n10_file, CANONICAL_THEOREM)
    else:
        declared = CANONICAL_THEOREM in n10_file.read_text()
    record(f"theorem {CANONICAL_THEOREM} declared in N10.lean", declared)

    # Scan ALL .lean files for → True (using block-comment stripping)
    if LEAN_TEXT_OK and lean_src.is_dir():
        trivial_files = lean_files_with_trivial_true(lean_src)
        record("No '→ True' in any .lean file (comment-stripped)",
               len(trivial_files) == 0,
               f"Found in: {trivial_files[:3]}" if trivial_files else "")
    else:
        # Fallback: check N10.lean only
        content = _strip(n10_file.read_text())
        has_trivial = "→ True" in content or "-> True" in content
        record("No '→ True' in N10.lean (comment-stripped)", not has_trivial)

    # Float in theorem/def lines (scan all .lean files)
    if lean_src.is_dir():
        float_violations = []
        for lean_file in lean_src.rglob("*.lean"):
            if LEAN_TEXT_OK:
                violations = lean_file_has_float_in_theorem(lean_file)
            else:
                violations = [
                    l for l in _strip(lean_file.read_text()).splitlines()
                    if (l.strip().startswith("theorem") or l.strip().startswith("def "))
                    and "Float" in l
                ]
            float_violations.extend(violations)
        record("No Float in theorem/def lines (all .lean files)",
               len(float_violations) == 0,
               f"Found: {float_violations[:2]}" if float_violations else "")

    # Geometry/Basic.lean: no conflicting Point definition
    geo_basic = LEAN_DIR / "ErdosAtlas" / "Geometry" / "Basic.lean"
    if geo_basic.is_file():
        if LEAN_TEXT_OK:
            has_conflict = lean_file_has_conflicting_point_def(geo_basic)
        else:
            has_conflict = "def Point : Type := Fin 2" in _strip(geo_basic.read_text())
        record("Geometry/Basic.lean has no conflicting Point def",
               not has_conflict,
               "Found 'def Point := Fin 2 → ℝ' in code" if has_conflict else "")


# ---------------------------------------------------------------------------
# Section 4: Sorry detection (level-aware)
# ---------------------------------------------------------------------------
def audit_sorry():
    print("\n── Section 4: Sorry Detection (Level-Aware) ──")

    lean_src = LEAN_DIR / "ErdosAtlas"
    if not lean_src.is_dir():
        record("ErdosAtlas directory exists", False)
        return

    if LEAN_TEXT_OK:
        occurrences = find_sorry_in_lean_files(LEAN_DIR)
    else:
        occurrences = []
        for lean_file in lean_src.rglob("*.lean"):
            for lineno, line in enumerate(lean_file.read_text().splitlines(), 1):
                if not line.strip().startswith("--") and "sorry" in line:
                    occurrences.append((str(lean_file), lineno, line.rstrip()))

    # Filter out field names / variable names containing "sorry"
    real_sorry = [
        (f, ln, l) for f, ln, l in occurrences
        if "sorry" in l
        and "sorryPresent" not in l
        and "has_sorry" not in l
    ]
    count = len(real_sorry)

    if CURRENT_FORMAL_LEVEL == "L5":
        record(f"No sorry at L5 ({count} found)", count == 0,
               f"L5 claimed but {count} sorry found" if count > 0 else "")
    else:
        record(f"Sorry at {CURRENT_FORMAL_LEVEL} ({count} found — allowed)", True,
               f"{count} sorry occurrence(s) — allowed at {CURRENT_FORMAL_LEVEL}")

    print(f"         Current formal level: {CURRENT_FORMAL_LEVEL}")


# ---------------------------------------------------------------------------
# Section 5: Lean build
# ---------------------------------------------------------------------------
def audit_lean_build():
    print("\n── Section 5: Lean Availability & lake build ──")

    lean_ok = shutil.which("lean") is not None
    lake_ok = shutil.which("lake") is not None

    record("lean on PATH", lean_ok)
    record("lake on PATH", lake_ok)

    if not lean_ok or not lake_ok:
        print("         NOTE: Lean not available — skipping lake build.")
        record("lake build (skipped — Lean unavailable)", False,
               "Install Lean 4 to run lake build")
        return

    manifest = LEAN_DIR / "lake-manifest.json"
    record("lake-manifest.json exists", manifest.is_file())

    if not manifest.is_file():
        record("lake build (skipped — no manifest)", False, "Run lake update first")
        return

    print("         Running lake build...")
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
            record("lake build succeeds", False, "\n         ".join(output_tail))
        else:
            record("lake build succeeds", True)
    except subprocess.TimeoutExpired:
        record("lake build succeeds", False, "Timed out after 300 seconds")
    except FileNotFoundError:
        record("lake build succeeds", False, "lake not found")


# ---------------------------------------------------------------------------
# Section 6: Formal level assessment (MONOTONE)
# ---------------------------------------------------------------------------
def audit_formal_level():
    print("\n── Section 6: Formal Level Assessment (Monotone) ──")

    n10_file = LEAN_DIR / "ErdosAtlas" / "CirclePacking" / "N10.lean"
    geo_file = LEAN_DIR / "ErdosAtlas" / "Geometry" / "Basic.lean"
    point_file = LEAN_DIR / "ErdosAtlas" / "Geometry" / "Point.lean"
    dist_file = LEAN_DIR / "ErdosAtlas" / "Geometry" / "Distance.lean"
    defs_file = LEAN_DIR / "ErdosAtlas" / "CirclePacking" / "Definitions.lean"

    # L1: meaningful statement exists (canonical theorem, no → True, no Float)
    l1_ok = False
    if n10_file.is_file():
        if LEAN_TEXT_OK:
            has_canonical = lean_file_has_theorem(n10_file, CANONICAL_THEOREM)
            no_trivial = not lean_file_has_trivial_true(n10_file)
            no_float = len(lean_file_has_float_in_theorem(n10_file)) == 0
        else:
            content = _strip(n10_file.read_text())
            has_canonical = CANONICAL_THEOREM in content
            no_trivial = "→ True" not in content
            no_float = True
        l1_ok = has_canonical and no_trivial and no_float

    record("L1 (STATEMENT_FORMALIZED): meaningful statement in Lean", l1_ok)

    # L2: real geometry definitions exist (requires L1 first — MONOTONE)
    l2_ok = False
    if l1_ok:
        # Check for actual structure/def declarations (comment-stripped)
        checks = []
        for fpath, pattern in [
            (point_file, "structure Point"),
            (dist_file, "def squaredDist"),
            (defs_file, "def IsPacking"),
        ]:
            if fpath.is_file():
                content = _strip(fpath.read_text())
                checks.append(pattern in content)
        l2_ok = len(checks) >= 2 and all(checks)

    # MONOTONE: L2 requires L1
    if l2_ok and not l1_ok:
        print("         ERROR: L2 claimed but L1 failed — impossible (monotone violation)")
        l2_ok = False

    record("L2 (DEFINITIONS_FORMALIZED): real geometry definitions exist", l2_ok)

    # Determine level (monotone)
    if l2_ok:
        level = "L2"
    elif l1_ok:
        level = "L1"
    else:
        level = "L0"

    print(f"\n         Current formal level: {level}")
    print(f"         Target: L5 (KERNEL_CHECKED)")
    print(f"         Path: L2 → L3 (key lemmas) → L4 (proof complete) → L5 (lake build, no sorry)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    print("=" * 65)
    print("  erdos-proof-atlas — Formal Audit (Lean Formalization)")
    print("=" * 65)
    print(f"  lean_text available: {LEAN_TEXT_OK}")

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
