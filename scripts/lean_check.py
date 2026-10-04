#!/usr/bin/env python3
"""
lean_check.py -- Lean verification engine for ErdosAtlas.

Reads ALL configuration from formal/lean/project_contract.json.
Does NOT independently redefine: required modules, executable path,
formal level, authorized axioms, or Mathlib revision.

Separate fields:
  declared_formal_level  -- from project_contract.json (never auto-promoted)
  build_status           -- observed from lake build
  sorry_status           -- observed from source scan
  axiom_status           -- observed from #print axioms
  theorem_presence_status -- observed from Lean source

Usage:
  python scripts/lean_check.py                    # strict mode (make lean)
  python scripts/lean_check.py --status           # status-only (make status)
  python scripts/lean_check.py --level L1         # check at declared level
  python scripts/lean_check.py --report FILE.json # write verification report
"""

import subprocess
import shutil
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone

# Always resolve relative to repository root, regardless of cwd
REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "formal" / "lean" / "project_contract.json"

RESULTS = []


def load_contract() -> dict:
    if not CONTRACT_PATH.is_file():
        print(f"[ERROR] {CONTRACT_PATH} not found.", file=sys.stderr)
        print("        Run: python scripts/validate_contract.py", file=sys.stderr)
        sys.exit(1)
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def record(label: str, passed: bool, detail: str = "") -> bool:
    status = "[PASS]" if passed else "[FAIL]"
    msg = f"  {status} {label}"
    if detail:
        msg += f"\n         {detail}"
    print(msg)
    RESULTS.append((label, passed))
    return passed


def check_lean_available() -> bool:
    return shutil.which("lean") is not None and shutil.which("lake") is not None


def check_required_modules(contract: dict) -> list:
    """Check required modules from project_contract.json (not hardcoded)."""
    missing = []
    for module_path in contract.get("required_modules", []):
        full_path = REPO_ROOT / module_path
        if not full_path.is_file():
            missing.append(module_path)
    # Check executable entry (from contract, not hardcoded)
    if contract.get("project_mode") == "library_and_executable":
        exe_entry = contract.get("executable_entry", "")
        if exe_entry and not (REPO_ROOT / exe_entry).is_file():
            missing.append(exe_entry)
    return missing


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


def find_sorry_in_lean_files(lean_dir: Path) -> list:
    """Find sorry occurrences (excluding comments and field names)."""
    occurrences = []
    lean_src = lean_dir / "ErdosAtlas"
    if not lean_src.is_dir():
        return occurrences
    for f in lean_src.rglob("*.lean"):
        stripped = strip_lean_comments(f.read_text(encoding="utf-8", errors="replace"))
        for lineno, line in enumerate(stripped.splitlines(), 1):
            if "sorry" in line and "sorryPresent" not in line and "has_sorry" not in line:
                occurrences.append((str(f.relative_to(REPO_ROOT)), lineno, line.rstrip()))
    return occurrences


def check_sorry_for_level(contract: dict, claimed_level: str) -> tuple:
    """
    Status-aware sorry check using policy from project_contract.json.
    Returns (passed, message).
    """
    sorry_policy = contract.get("sorry_policy", {})
    policy = sorry_policy.get(claimed_level, "allowed")  # default: allowed

    lean_dir = REPO_ROOT / "formal" / "lean"
    occurrences = find_sorry_in_lean_files(lean_dir)
    count = len(occurrences)

    if policy == "forbidden":
        if count > 0:
            details = "; ".join(f"{f}:{ln}" for f, ln, _ in occurrences[:5])
            return False, f"{claimed_level} policy=forbidden but {count} sorry found: {details}"
        return True, "No sorry found -- policy satisfied"
    else:  # allowed
        if count > 0:
            return True, f"{count} sorry at {claimed_level} -- allowed by policy"
        return True, f"No sorry found at {claimed_level}"


def run_axiom_check(contract: dict, lean_dir: Path) -> tuple:
    """
    Run #print axioms on canonical theorem.
    Compare against authorized_axioms from project_contract.json.
    Returns (passed, output_text).
    """
    if not check_lean_available():
        return False, "Lean not available"

    canonical = contract.get("canonical_theorem", "")
    authorized = set(contract.get("authorized_axioms", []))

    # Build the namespace import path
    parts = canonical.rsplit(".", 1)
    if len(parts) != 2:
        return False, f"Cannot parse canonical theorem: {canonical}"
    namespace = parts[0]

    lean_script = f"""
import {namespace}
#print axioms {canonical}
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
        elif result.returncode != 0:
            return False, f"Lean error (rc={result.returncode}): {output[:200]}"
        else:
            return True, output.strip()[:200] or "No axiom output"

    except subprocess.TimeoutExpired:
        return False, "Axiom check timed out"
    except FileNotFoundError:
        return False, "lake not found"


def run_lake_build(lean_dir: Path) -> tuple:
    """Run lake build. Returns (success, output)."""
    try:
        result = subprocess.run(
            ["lake", "build"],
            cwd=str(lean_dir),
            capture_output=True,
            text=True,
            timeout=300,
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "lake build timed out after 300 seconds"
    except FileNotFoundError:
        return False, "lake not found on PATH"


def get_git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=10,
            cwd=str(REPO_ROOT)
        )
        return result.stdout.strip() if result.returncode == 0 else "UNKNOWN"
    except Exception:
        return "UNKNOWN"


def strict_mode(contract: dict, claimed_level: str, report_path: str = "") -> int:
    """Strict mode: make lean. FAILS if Lean unavailable or checks fail."""
    lean_dir = REPO_ROOT / "formal" / "lean"

    print("=" * 65)
    print(f"  Lean Verification (level: {claimed_level})")
    print(f"  Contract: {CONTRACT_PATH}")
    print(f"  Declared level: {contract.get('current_formal_level', 'L1')}")
    print("=" * 65)

    # Separate observed statuses (never auto-promote declared_formal_level)
    build_status = None
    sorry_status = None
    axiom_status = None
    theorem_presence_status = None

    # 1. Lean availability
    lean_ok = check_lean_available()
    if not lean_ok:
        print("[FAIL] Lean/lake not installed or not on PATH.")
        print("       Use 'make status' to report without failing.")
        return 1
    record("Lean/lake available", True)

    # 2. Required modules (from contract)
    missing = check_required_modules(contract)
    record("All required modules present (from contract)",
           len(missing) == 0,
           f"Missing: {missing}" if missing else "")

    # 3. lake build
    print("\n  [...] Running lake build...")
    build_ok, build_out = run_lake_build(lean_dir)
    build_status = "PASS" if build_ok else "FAIL"
    record("lake build succeeds", build_ok,
           "\n".join(build_out.splitlines()[-15:]) if not build_ok else "")

    # 4. Sorry check (status-aware, policy from contract)
    sorry_ok, sorry_msg = check_sorry_for_level(contract, claimed_level)
    sorry_status = "PASS" if sorry_ok else "FAIL"
    record(f"Sorry check (level {claimed_level}, policy from contract)", sorry_ok, sorry_msg)

    # 5. Axiom audit (only at L5)
    if build_ok and claimed_level == "L5":
        print("\n  [...] Running axiom audit (#print axioms)...")
        axiom_ok, axiom_out = run_axiom_check(contract, lean_dir)
        axiom_status = "PASS" if axiom_ok else "FAIL"
        record("Axiom audit (L5 gate)", axiom_ok,
               axiom_out[:300] if not axiom_ok else axiom_out[:200])
    else:
        axiom_status = "NOT_REQUIRED"
        print(f"  [INFO] Axiom audit skipped at {claimed_level} (required only at L5)")

    # 6. Canonical theorem presence
    canonical = contract.get("canonical_theorem", "")
    if canonical and build_ok:
        lean_src = lean_dir / "ErdosAtlas"
        found = any(
            canonical.split(".")[-1] in f.read_text(encoding="utf-8", errors="replace")
            for f in lean_src.rglob("*.lean")
        ) if lean_src.is_dir() else False
        theorem_presence_status = "FOUND" if found else "NOT_FOUND"
        record(f"Canonical theorem present: {canonical}", found)
    else:
        theorem_presence_status = "NOT_CHECKED"

    # Summary
    print("\n" + "=" * 65)
    passed = sum(1 for _, ok in RESULTS if ok)
    failed = sum(1 for _, ok in RESULTS if not ok)
    print(f"  Results: {passed}/{len(RESULTS)} passed, {failed} failed")

    # IMPORTANT: declared_formal_level comes from contract, NOT from build results
    declared_level = contract.get("current_formal_level", "L1")
    print(f"  Declared formal level: {declared_level} (from project_contract.json)")
    print(f"  Build status: {build_status}")
    print(f"  Sorry status: {sorry_status}")
    print(f"  Axiom status: {axiom_status}")

    # Write verification report if requested
    if report_path:
        report = {
            "schema_version": "1.0",
            "project": contract.get("project_name", "ErdosAtlas"),
            "declared_formal_level": declared_level,
            "lean_toolchain": contract.get("lean_toolchain"),
            "mathlib_revision": contract.get("mathlib_rev"),
            "files_ok": len(missing) == 0,
            "manifest_consistent": None,  # checked by validate_contract.py
            "lake_build": build_status,
            "sorry_count": len(find_sorry_in_lean_files(lean_dir)),
            "axiom_audit_status": axiom_status,
            "canonical_theorem_status": theorem_presence_status,
            "verification_status": "PASS" if failed == 0 else "FAIL",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "git_commit": get_git_commit(),
        }
        Path(report_path).parent.mkdir(parents=True, exist_ok=True)
        Path(report_path).write_text(json.dumps(report, indent=2))
        print(f"  Verification report: {report_path}")

    if failed == 0:
        print(f"[PASS] Lean checks passed")
        return 0
    else:
        print(f"[FAIL] {failed} check(s) failed")
        return 1


def status_mode(contract: dict) -> int:
    """Status mode: make status. Reports without failing."""
    lean_dir = REPO_ROOT / "formal" / "lean"
    print("Lean Formal Verification Status")
    print(f"Contract: {CONTRACT_PATH}")
    print("-" * 40)

    lean_ok = check_lean_available()
    if not lean_ok:
        print("Lean available:  NO")
        print(f"Declared level:  {contract.get('current_formal_level', 'L1')}")
        return 0

    missing = check_required_modules(contract)
    build_ok = False
    sorry_count = 0
    if not missing:
        build_ok, _ = run_lake_build(lean_dir)
        if build_ok:
            sorry_count = len(find_sorry_in_lean_files(lean_dir))

    print(f"Lean available:   YES")
    print(f"Files OK:         {len(missing) == 0}")
    print(f"lake build OK:    {build_ok}")
    print(f"Sorry count:      {sorry_count}")
    print(f"Declared level:   {contract.get('current_formal_level', 'L1')} (from contract)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Lean verification engine (reads project_contract.json)"
    )
    parser.add_argument("--status", action="store_true",
                        help="Status-only mode: report without failing")
    parser.add_argument("--level", default="L1",
                        choices=["L0", "L1", "L2", "L3", "L4", "L5"],
                        help="Claimed formal level (default: L1)")
    parser.add_argument("--report", default="",
                        help="Write verification report to this JSON file")
    args = parser.parse_args()

    contract = load_contract()

    if args.status:
        return status_mode(contract)
    else:
        return strict_mode(contract, claimed_level=args.level, report_path=args.report)


if __name__ == "__main__":
    sys.exit(main())
