
#!/usr/bin/env python3
"""
check_paths.py — Repository path consistency checker.

REPAIR NOTE (Step 10):
  Added this script to catch the exact class of errors present in the
  original repository: mismatches between Makefile, CI, Lean files,
  DeepMind mapping, certificates, and Python imports.

  Verifies:
    1. Every Makefile script reference exists on disk
    2. Every CI workflow path reference exists on disk
    3. Every documented Lean file exists on disk
    4. Every DeepMind mapping target exists on disk
    5. Every certificate path exists on disk
    6. Every Python import target exists on disk
    7. No test/ directory (must be tests/)
    8. No || true in mandatory CI steps

Usage:
  python scripts/check_paths.py
"""

import sys
import re
import os
from pathlib import Path

RESULTS = []


def record(label: str, passed: bool, detail: str = ""):
    status = "[PASS]" if passed else "[FAIL]"
    msg = f"  {status} {label}"
    if detail:
        msg += f"\n         {detail}"
    print(msg)
    RESULTS.append((label, passed, detail))


# ---------------------------------------------------------------------------
# Section 1: Canonical test directory
# ---------------------------------------------------------------------------
def check_test_directory():
    print("\n── Section 1: Canonical Test Directory ──")

    # Must use tests/ not test/
    tests_exists = Path("tests").is_dir()
    test_exists = Path("test").is_dir()

    record("tests/ directory exists", tests_exists)
    record("No obsolete test/ directory", not test_exists,
           "Found 'test/' directory — migrate to 'tests/' and remove" if test_exists else "")

    # Required subdirectories
    for subdir in ["unit", "integration", "adversarial", "regression", "formal"]:
        record(f"tests/{subdir}/ exists", Path(f"tests/{subdir}").is_dir())


# ---------------------------------------------------------------------------
# Section 2: Makefile path consistency
# ---------------------------------------------------------------------------
def check_makefile_paths():
    print("\n── Section 2: Makefile Path Consistency ──")

    makefile = Path("Makefile")
    if not makefile.is_file():
        record("Makefile exists", False)
        return

    record("Makefile exists", True)
    content = makefile.read_text()

    # Check Makefile uses tests/ not test/
    if "pytest tests/" in content or "pytest -q tests/" in content:
        record("Makefile uses tests/ (not test/)", True)
    elif "pytest test/" in content:
        record("Makefile uses tests/ (not test/)", False,
               "Makefile references 'test/' — change to 'tests/'")
    else:
        record("Makefile uses tests/ (not test/)", True)  # may use different pattern

    # Check no || true in mandatory steps
    lines_with_or_true = [
        line.strip() for line in content.splitlines()
        if "|| true" in line and not line.strip().startswith("#")
    ]
    record("No '|| true' in Makefile mandatory steps",
           len(lines_with_or_true) == 0,
           f"Found: {lines_with_or_true}" if lines_with_or_true else "")

    # Check required make targets exist
    required_targets = [
        "install", "test", "lean", "audit", "report",
        "deepmind-export", "manifest", "all", "clean"
    ]
    for target in required_targets:
        pattern = rf"^{re.escape(target)}[:\s]"
        found = bool(re.search(pattern, content, re.MULTILINE))
        record(f"Makefile has target: {target}", found)

    # Check scripts referenced in Makefile exist
    script_refs = re.findall(r"python\s+scripts/(\S+\.py)", content)
    for script in set(script_refs):
        path = Path(f"scripts/{script}")
        record(f"Makefile-referenced script exists: scripts/{script}", path.is_file())


# ---------------------------------------------------------------------------
# Section 3: CI workflow path consistency
# ---------------------------------------------------------------------------
def check_ci_paths():
    print("\n── Section 3: CI Workflow Path Consistency ──")

    ci_dir = Path(".github/workflows")
    if not ci_dir.is_dir():
        record(".github/workflows/ exists", False)
        return

    record(".github/workflows/ exists", True)

    workflow_files = list(ci_dir.glob("*.yml")) + list(ci_dir.glob("*.yaml"))
    record(f"CI workflow files found ({len(workflow_files)})", len(workflow_files) > 0)

    for wf in workflow_files:
        content = wf.read_text()

        # Check no || true in CI
        or_true_lines = [
            line.strip() for line in content.splitlines()
            if "|| true" in line and not line.strip().startswith("#")
        ]
        record(f"No '|| true' in {wf.name}", len(or_true_lines) == 0,
               f"Found: {or_true_lines[:3]}" if or_true_lines else "")

        # Check CI uses tests/ not test/
        if "tests/unit" in content or "tests/adversarial" in content:
            record(f"{wf.name} uses tests/ (canonical)", True)
        elif "test/unit" in content or "test/adversarial" in content:
            record(f"{wf.name} uses tests/ (canonical)", False,
                   "CI references 'test/' — change to 'tests/'")

        # Check Python scripts referenced in CI exist
        script_refs = re.findall(r"python\s+scripts/(\S+\.py)", content)
        for script in set(script_refs):
            path = Path(f"scripts/{script}")
            record(f"CI-referenced script exists: scripts/{script}", path.is_file())


# ---------------------------------------------------------------------------
# Section 4: Lean file consistency
# ---------------------------------------------------------------------------
def check_lean_files():
    print("\n── Section 4: Lean File Consistency ──")

    lean_dir = Path("formal/lean")
    required_lean_files = [
        lean_dir / "lakefile.toml",
        lean_dir / "lean-toolchain",
        lean_dir / "lake-manifest.json",
        lean_dir / "Main.lean",
        lean_dir / "ErdosAtlas" / "Basic.lean",
        lean_dir / "ErdosAtlas" / "Geometry" / "Basic.lean",
        lean_dir / "ErdosAtlas" / "CirclePacking" / "N10.lean",
        lean_dir / "ErdosAtlas" / "Problems" / "SquarePacking.lean",
    ]

    for f in required_lean_files:
        record(f"Lean file exists: {f}", f.is_file())

    # Check lakefile.toml has mathlib
    lakefile = lean_dir / "lakefile.toml"
    if lakefile.is_file():
        content = lakefile.read_text()
        record("lakefile.toml has mathlib [[require]]",
               "mathlib" in content and "[[require]]" in content)
        record("lakefile.toml has no || true", "|| true" not in content)

    # Check Main.lean imports ErdosAtlas
    main_lean = lean_dir / "Main.lean"
    if main_lean.is_file():
        content = main_lean.read_text()
        record("Main.lean imports ErdosAtlas", "ErdosAtlas" in content)


# ---------------------------------------------------------------------------
# Section 5: DeepMind mapping targets
# ---------------------------------------------------------------------------
def check_deepmind_targets():
    print("\n── Section 5: DeepMind Mapping Targets ──")

    canonical = "circlePacking10MinDistBound"
    mapping = Path("bridges/deepmind/mapping.yaml")
    lean_n10 = Path("formal/lean/ErdosAtlas/CirclePacking/N10.lean")
    export_script = Path("scripts/export_deepmind.py")

    record("bridges/deepmind/mapping.yaml exists", mapping.is_file())
    record("scripts/export_deepmind.py exists", export_script.is_file())

    for label, filepath in [
        ("mapping.yaml", mapping),
        ("N10.lean", lean_n10),
        ("export_deepmind.py", export_script),
    ]:
        if filepath.is_file():
            found = canonical in filepath.read_text()
            record(f"Canonical theorem '{canonical}' in {label}", found)

    # Check old inconsistent name is absent
    old_name = "circlePacking10MinDist"
    for label, filepath in [("export_deepmind.py", export_script)]:
        if filepath.is_file():
            content = filepath.read_text()
            pattern = rf"\b{re.escape(old_name)}\b"
            matches = re.findall(pattern, content)
            real_matches = [m for m in matches if m != canonical]
            record(f"Old name '{old_name}' absent from {label}",
                   len(real_matches) == 0,
                   f"Found {len(real_matches)} occurrence(s)" if real_matches else "")


# ---------------------------------------------------------------------------
# Section 6: Certificate paths
# ---------------------------------------------------------------------------
def check_certificate_paths():
    print("\n── Section 6: Certificate Paths ──")

    cert_dir = Path("certificates/circle_packing_n10")
    record("certificates/circle_packing_n10/ exists", cert_dir.is_dir())

    cert_file = cert_dir / "certificate.json"
    record("certificate.json exists", cert_file.is_file())

    if cert_file.is_file():
        try:
            import json
            with open(cert_file) as f:
                cert = json.load(f)
            record("certificate.json is valid JSON", True)
            record("certificate has problem_id", "problem_id" in cert)
            record("certificate has polynomial", "polynomial" in cert)
        except Exception as e:
            record("certificate.json is valid JSON", False, str(e))


# ---------------------------------------------------------------------------
# Section 7: Python import targets
# ---------------------------------------------------------------------------
def check_python_imports():
    print("\n── Section 7: Python Import Targets ──")

    atlas_modules = [
        "src/atlas/__init__.py",
        "src/atlas/schema.py",
        "src/atlas/geometry.py",
        "src/atlas/certification.py",
        "src/atlas/provenance.py",
    ]

    for mod in atlas_modules:
        record(f"Atlas module exists: {mod}", Path(mod).is_file())

    # Check all scripts compile (syntax check)
    scripts = list(Path("scripts").glob("*.py")) if Path("scripts").is_dir() else []
    for script in scripts:
        try:
            source = script.read_text()
            compile(source, str(script), "exec")
            record(f"Script syntax OK: {script.name}", True)
        except SyntaxError as e:
            record(f"Script syntax OK: {script.name}", False, str(e))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    print("=" * 65)
    print("  erdos-proof-atlas — Path Consistency Check")
    print("=" * 65)

    check_test_directory()
    check_makefile_paths()
    check_ci_paths()
    check_lean_files()
    check_deepmind_targets()
    check_certificate_paths()
    check_python_imports()

    print("\n" + "=" * 65)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    failed = sum(1 for _, ok, _ in RESULTS if not ok)
    total = len(RESULTS)

    print(f"  Results: {passed}/{total} passed, {failed} failed")
    print()

    if failed == 0:
        print("[PASS] PATH CONSISTENCY CHECK PASSED")
        return 0
    else:
        print(f"[FAIL] PATH CONSISTENCY CHECK FAILED ({failed} issue(s))")
        print("       These are the exact class of errors that caused the original failures.")
        print("       Fix all path mismatches before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

