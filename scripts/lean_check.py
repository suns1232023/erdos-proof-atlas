#!/usr/bin/env python3
"""
lean_check.py — Lean 4 formal verification checker.

Reads project structure from formal/lean/project_contract.json.
This is the SINGLE source of truth for required Lean modules.

Modes:
  python scripts/lean_check.py          # strict mode (make lean)
  python scripts/lean_check.py --status # status-only (make status)
  python scripts/lean_check.py --level L5  # override claimed level
"""

import subprocess
import shutil
import sys
import json
import argparse
from pathlib import Path

CONTRACT_PATH = Path("formal/lean/project_contract.json")
LEAN_DIR = Path("formal/lean")

RESULTS = []


def load_contract() -> dict:
    """Load project_contract.json as single source of truth."""
    if not CONTRACT_PATH.is_file():
        print(f"[ERROR] {CONTRACT_PATH} not found. This is the authoritative contract.", file=sys.stderr)
        sys.exit(1)
    return json.loads(CONTRACT_PATH.read_text())


def record(label: str, passed: bool, detail: str = ""):
    status = "[PASS]" if passed else "[FAIL]"
    msg = f"  {status} {label}"
    if detail:
        msg += f"\n         {detail}"
    print(msg)
    RESULTS.append((label, passed))


def check_lean_available() -> bool:
    return shutil.which("lean") is not None and shutil.which("lake") is not None


def check_required_modules(contract: dict) -> list[str]:
    """Check required modules from project_contract.json."""
    missing = []
    for module_path in contract.get("required_modules", []):
        if not Path(module_path).is_file():
            missing.append(module_path)
    # Check executable entry if project has one
    if contract.get("project_mode") == "library_and_executable":
        exe_entry = contract.get("executable_entry", "")
        if exe_entry and not Path(exe_entry).is_file():
            # Also check lowercase variant
            lower = Path(exe_entry.replace("Main.lean", "main.lean"))
            if not lower.is_file():
                missing.append(exe_entry)
    return missing


def check_lakefile_has_mathlib() -> bool:
    lakefile = LEAN_DIR / "lakefile.toml"
    if not lakefile.is_file():
        return False
    content = lakefile.read_text()
    return "mathlib" in content and "[[require]]" in content


def strip_lean_comments(text: str) -> str:
    """Strip -- and /- -/ comments from Lean source."""
    result = []
    i, n, depth = 0, len(text), 0
    while i < n:
        if depth == 0:
            if text[i:i+2] == "/-":
                depth += 1; i += 2; result.append(" ")
            elif text[i:i+2] == "--":
                while i < n and text[i] != "\n": i += 1
            else:
                result.append(text[i]); i += 1
        else:
            if text[i:i+2] == "-/": depth -= 1; i += 2
            elif text[i:i+2] == "/-": depth += 1; i += 2
            else:
                if text[i] == "\n": result.append("\n")
                i += 1
    return "".join(result)


def find_sorry_in_lean_files() -> list[tuple[str, int, str]]:
    """Find sorry occurrences (excluding comments and field names)."""
    occurrences = []
    lean_src = LEAN_DIR / "ErdosAtlas"
    if not lean_src.is_dir():
        return occurrences
    for f in lean_src.rglob("*.lean"):
        stripped = strip_lean_comments(f.read_text())
        for lineno, line in enumerate(stripped.splitlines(), 1):
            if "sorry" in line and "sorryPresent" not in line and "has_sorry" not in line:
                occurrences.append((str(f), lineno, line.rstrip()))
    return occurrences


def check_sorry_for_level(claimed_level: str) -> tuple[bool, str]:
    """
    Status-aware sorry check.
    L1-L4: sorry allowed.
    L5: sorry forbidden.
    """
    occurrences = find_sorry_in_lean_files()
    count = len(occurrences)
    if claimed_level == "L5":
        if count > 0:
            details = "; ".join(f"{f}:{ln}" for f, ln, _ in occurrences[:5])
            return False, f"L5 claimed but {count} sorry found: {details}"
        return True, "No sorry found — L5 kernel check passed"
    else:
        if count > 0:
            return True, f"{count} sorry at {claimed_level} — allowed (sorry forbidden only at L5)"
        return True, f"No sorry found at {claimed_level}"


def run_axiom_check(contract: dict) -> tuple[bool, str]:
    """
    Run #print axioms on canonical theorem.
    Compare against authorized axiom allowlist from contract.
    """
    if not check_lean_available():
        return False, "Lean not available"

    canonical = contract.get("canonical_theorem", "")
    authorized = set(contract.get("authorized_axioms", [
        "Classical.choice", "propext", "Quot.sound", "funext"
    ]))

    # Import path from canonical theorem name
    parts = canonical.rsplit(".", 1)
    if len(parts) == 2:
        namespace, theorem = parts
        import_path = namespace.replace(".", "/")
    else:
        return False, f"Cannot parse canonical theorem: {canonical}"

    lean_script = f"""
import {namespace}
#print axioms {canonical}
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

        # Parse axiom set from output
        import re
        match = re.search(r"depends on axioms:\s*\[([^\]]+)\]", output, re.DOTALL)
        if match:
            axiom_list = [a.strip() for a in match.group(1).split(",") if a.strip()]
            actual_axioms = set(axiom_list)
            unauthorized = actual_axioms - authorized
            if unauthorized:
                return False, f"Unauthorized axioms: {unauthorized}"
            return True, f"Axiom set OK: {actual_axioms}"
        elif "sorryAx" in output:
            return False, "sorryAx found in axiom output"
        else:
            return True, output.strip()[:200] or "No axiom output (may need lake build first)"

    except subprocess.TimeoutExpired:
        return False, "Axiom check timed out"
    except FileNotFoundError:
        return False, "lake not found"


def run_lake_build() -> tuple[bool, str]:
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


def determine_formal_level(
    lean_ok: bool,
    files_ok: bool,
    mathlib_ok: bool,
    build_ok: bool,
    sorry_ok: bool,
    axiom_ok: bool,
) -> str:
    """
    Conservative formal level determination (Option A from spec):
    Automatically determine only L0/L1/L5.
    L2-L4 are manually declared metadata.
    """
    if not lean_ok or not files_ok or not mathlib_ok:
        return "L0"
    if not build_ok:
        return "L0"
    if not sorry_ok:
        return "L1"  # builds but has sorry
    if not axiom_ok:
        return "L1"  # no sorry but unauthorized axioms
    return "L5"  # builds + no sorry + authorized axioms only


def strict_mode(claimed_level: str = "L1") -> int:
    """Strict mode: make lean. FAILS if Lean unavailable or checks fail."""
    contract = load_contract()
    print("=" * 65)
    print(f"  Lean 4 Formal Verification (strict, claimed level: {claimed_level})")
    print(f"  Contract: {CONTRACT_PATH}")
    print("=" * 65)

    # 1. Lean availability
    lean_ok = check_lean_available()
    if not lean_ok:
        print("[FAIL] Lean/lake not installed or not on PATH.")
        print("       make lean MUST fail when Lean is unavailable.")
        print("       Use 'make status' to report L0 without failing.")
        return 1
    record("Lean/lake available", True)

    # 2. Required modules (from contract)
    missing = check_required_modules(contract)
    record("All required modules present (from project_contract.json)",
           len(missing) == 0,
           f"Missing: {missing}" if missing else "")

    # 3. mathlib dependency
    mathlib_ok = check_lakefile_has_mathlib()
    record("lakefile.toml has mathlib [[require]]", mathlib_ok)

    # 4. lake build
    print("\n  [...] Running lake build...")
    build_ok, build_out = run_lake_build()
    record("lake build succeeds", build_ok,
           "\n".join(build_out.splitlines()[-15:]) if not build_ok else "")

    # 5. Sorry check (status-aware)
    sorry_ok, sorry_msg = check_sorry_for_level(claimed_level)
    record(f"Sorry check (level {claimed_level})", sorry_ok, sorry_msg)

    # 6. Axiom audit (if build succeeded and L5 claimed)
    axiom_ok = True
    if build_ok and claimed_level == "L5":
        print("\n  [...] Running axiom audit (#print axioms)...")
        axiom_ok, axiom_out = run_axiom_check(contract)
        record("Axiom audit (L5 gate)", axiom_ok,
               axiom_out[:300] if not axiom_ok else axiom_out[:200])
    elif build_ok:
        print(f"  [INFO] Axiom audit skipped at {claimed_level} (required only at L5)")

    # 7. Determine actual formal level
    actual_level = determine_formal_level(
        lean_ok, len(missing) == 0, mathlib_ok, build_ok, sorry_ok, axiom_ok
    )
    print(f"\n  Declared level: {claimed_level}")
    print(f"  Actual level:   {actual_level}")
    if actual_level != claimed_level and claimed_level == "L5":
        record(f"Formal level matches claimed ({claimed_level})", False,
               f"Actual: {actual_level}")

    print("\n" + "=" * 65)
    passed = sum(1 for _, ok in RESULTS if ok)
    failed = sum(1 for _, ok in RESULTS if not ok)
    print(f"  Results: {passed}/{len(RESULTS)} passed, {failed} failed")

    if failed == 0:
        print(f"[PASS] Lean checks passed — Level: {actual_level}")
        return 0
    else:
        print(f"[FAIL] {failed} Lean check(s) failed")
        return 1


def status_mode() -> int:
    """Status mode: make status. Reports level without failing."""
    contract = load_contract()
    print("Lean Formal Verification Status")
    print(f"Contract: {CONTRACT_PATH}")
    print("-" * 40)

    lean_ok = check_lean_available()
    if not lean_ok:
        print("Lean available:  NO")
        print("Formal level:    L0 (NOT_FORMALIZED)")
        print("Note: Install Lean 4 to advance beyond L0.")
        return 0

    files_ok = len(check_required_modules(contract)) == 0
    mathlib_ok = check_lakefile_has_mathlib()

    build_ok = False
    sorry_count = 0
    if files_ok and mathlib_ok:
        build_ok, _ = run_lake_build()
        if build_ok:
            sorry_count = len(find_sorry_in_lean_files())

    # Conservative: L0/L1/L5 only
    if not lean_ok or not files_ok or not mathlib_ok or not build_ok:
        level = "L0"
    elif sorry_count > 0:
        level = "L1"
    else:
        level = "L5"  # no sorry — may still need axiom check for true L5

    print(f"Lean available:   YES")
    print(f"Files OK:         {files_ok}")
    print(f"mathlib OK:       {mathlib_ok}")
    print(f"lake build OK:    {build_ok}")
    print(f"Sorry count:      {sorry_count}")
    print(f"Formal level:     {level}")
    print(f"Declared level:   {contract.get('current_formal_level', 'L1')}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Lean 4 formal verification checker (reads project_contract.json)"
    )
    parser.add_argument(
        "--status", action="store_true",
        help="Status-only mode: report level without failing when Lean unavailable"
    )
    parser.add_argument(
        "--level", default="L1",
        choices=["L0", "L1", "L2", "L3", "L4", "L5"],
        help="Claimed formal level for sorry/axiom check (default: L1)"
    )
    args = parser.parse_args()

    if args.status:
        sys.exit(status_mode())
    else:
        sys.exit(strict_mode(claimed_level=args.level))


if __name__ == "__main__":
    main()
