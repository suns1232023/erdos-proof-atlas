
#!/usr/bin/env python3
"""
check_paths.py — Repository path consistency checker.

REPAIR V5:
  - Section 7: Fixed Python module paths to match actual repo structure.
    Actual modules are in subdirectories (src/atlas/schema/evidence.py etc.),
    NOT flat files (src/atlas/schema.py etc.).
  - Section 2: Fixed Makefile script references to match actual scripts.
  - Added Main.lean case-sensitivity check.
  - Added check for conflicting Point definition in Geometry/Basic.lean.
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

    tests_exists = Path("tests").is_dir()
    test_exists = Path("test").is_dir()

    record("tests/ directory exists", tests_exists)
    record("No obsolete test/ directory", not test_exists,
           "Found 'test/' directory — migrate to 'tests/' and remove" if test_exists else "")

    for subdir in ["unit", "integration", "adversarial", "regression", "formal"]:
        record(f"tests/{subdir}/ exists", Path(f"tests/{subdir}").is_dir())


# ---------------------------------------------------------------------------
# Section 2: Makefile path consistency
# REPAIR V5: Updated to check actual script names
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
        record("Makefile uses tests/ (not test/)", True)

    # Check no bare || true in mandatory steps (allow in clean)
    lines_with_or_true = []
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if "|| true" in line:
            # Allow in clean target
            if not any(kw in line for kw in ["clean", "rm -rf", "find.*delete", "rmdir"]):
                lines_with_or_true.append(stripped)
    record("No '|| true' in mandatory Makefile steps",
           len(lines_with_or_true) == 0,
           f"Found: {lines_with_or_true}" if lines_with_or_true else "")

    # Check required make targets exist
    required_targets = [
        "install", "test", "lean", "audit", "report",
        "deepmind-export", "manifest", "all", "clean",
        "search", "verify", "certify"
    ]
    for target in required_targets:
        pattern = rf"^{re.escape(target)}[:\s]"
        found = bool(re.search(pattern, content, re.MULTILINE))
        record(f"Makefile has target: {target}", found)

    # REPAIR V5: Check scripts referenced in Makefile actually exist
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

        # Check for bare || true (not in comments or echo lines)
        bare_or_true = []
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith("echo") or stripped.startswith("printf"):
                continue
            if re.search(r'\|\| true\s*$', line):
                bare_or_true.append(stripped[:80])
        record(f"No bare '|| true' in {wf.name}", len(bare_or_true) == 0,
               f"Found: {bare_or_true[:3]}" if bare_or_true else "")

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
        lean_dir / "ErdosAtlas" / "Basic.lean",
        lean_dir / "ErdosAtlas" / "Geometry" / "Basic.lean",
        lean_dir / "ErdosAtlas" / "CirclePacking" / "N10.lean",
        lean_dir / "ErdosAtlas" / "Problems" / "SquarePacking.lean",
    ]

    for f in required_lean_files:
        record(f"Lean file exists: {f}", f.is_file())

    # REPAIR V5: Check Main.lean case sensitivity
    main_upper = (lean_dir / "Main.lean").is_file()
    main_lower = (lean_dir / "main.lean").is_file()
    if main_upper:
        record("Main.lean exists (correct case for Linux)", True)
    elif main_lower:
        record("Main.lean exists (correct case for Linux)", False,
               "Found 'main.lean' (lowercase) — lakefile expects 'Main.lean'.\n"
               "         Fix: git mv formal/lean/main.lean formal/lean/Main.lean")
    else:
        record("Main.lean exists (correct case for Linux)", False, "Neither found")

    # Check lakefile.toml has mathlib
    lakefile = lean_dir / "lakefile.toml"
    if lakefile.is_file():
        content = lakefile.read_text()
        record("lakefile.toml has mathlib [[require]]",
               "mathlib" in content and "[[require]]" in content)
        record("lakefile.toml has no || true", "|| true" not in content)

    # REPAIR V5: Check Geometry/Basic.lean has no conflicting Point definition
    geo_basic = lean_dir / "ErdosAtlas" / "Geometry" / "Basic.lean"
    if geo_basic.is_file():
        content = geo_basic.read_text()
        has_conflict = "def Point : Type := Fin 2 → ℝ" in content
        record("Geometry/Basic.lean has no conflicting Point def", not has_conflict,
               "Found 'def Point := Fin 2 → ℝ' — conflicts with Point.lean structure" if has_conflict else "")

    # Check Main.lean imports ErdosAtlas
    for main_path in [lean_dir / "Main.lean", lean_dir / "main.lean"]:
        if main_path.is_file():
            content = main_path.read_text()
            record("Main.lean imports ErdosAtlas", "ErdosAtlas" in content)
            break


# ---------------------------------------------------------------------------
# Section 5: DeepMind mapping targets
# ---------------------------------------------------------------------------
def check_deepmind_targets():
    print("\n── Section 5: DeepMind Mapping Targets ──")

    canonical = "circlePacking10MinDistBound"
    mapping = Path("bridges/deepmind/mapping.yaml")
    lean_n10 = Path("formal/lean/ErdosAtlas/CirclePacking/N10.lean")
    export_script = Path("scripts/export_deepmind.py")
    examples_json = Path("bridges/deepmind/examples/circle_packing_n10.json")

    record("bridges/deepmind/mapping.yaml exists", mapping.is_file())
    record("scripts/export_deepmind.py exists", export_script.is_file())
    record("bridges/deepmind/examples/circle_packing_n10.json exists", examples_json.is_file())

    for label, filepath in [
        ("mapping.yaml", mapping),
        ("N10.lean", lean_n10),
        ("export_deepmind.py", export_script),
        ("examples/circle_packing_n10.json", examples_json),
    ]:
        if filepath.is_file():
            found = canonical in filepath.read_text()
            record(f"Canonical theorem '{canonical}' in {label}", found)

    # Check old inconsistent name is absent
    old_name = "circlePacking10MinDist"
    for label, filepath in [
        ("export_deepmind.py", export_script),
        ("examples/circle_packing_n10.json", examples_json),
    ]:
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
# REPAIR V5: Check actual filename (polynomial_certificate.json)
# ---------------------------------------------------------------------------
def check_certificate_paths():
    print("\n── Section 6: Certificate Paths ──")

    cert_dir = Path("certificates/circle_packing_n10")
    record("certificates/circle_packing_n10/ exists", cert_dir.is_dir())

    # REPAIR V5: Actual filename is polynomial_certificate.json
    poly_cert = cert_dir / "polynomial_certificate.json"
    cert_json = cert_dir / "certificate.json"

    if poly_cert.is_file():
        record("polynomial_certificate.json exists", True)
        cert_file = poly_cert
    elif cert_json.is_file():
        record("certificate.json exists (alternative)", True)
        cert_file = cert_json
    else:
        record("Certificate file exists", False,
               "Neither polynomial_certificate.json nor certificate.json found")
        return

    try:
        import json
        with open(cert_file) as f:
            cert = json.load(f)
        record("Certificate is valid JSON", True)
        record("Certificate has polynomial data",
               "polynomial" in cert or "coefficients" in cert)
    except Exception as e:
        record("Certificate is valid JSON", False, str(e))


# ---------------------------------------------------------------------------
# Section 7: Python import targets
# REPAIR V5: Fixed to check actual module paths (subdirectory structure)
# ---------------------------------------------------------------------------
def check_python_imports():
    print("\n── Section 7: Python Import Targets ──")

    # REPAIR V5: Actual module paths in subdirectories
    atlas_modules = [
        "src/atlas/schema/evidence.py",
        "src/atlas/geometry/circle_packing.py",
        "src/atlas/certification/certificate.py",
        "src/atlas/provenance/tracker.py",
        "src/atlas/search/multistart.py",
        "src/atlas/verification/verifier.py",
        "src/atlas/reporting/generator.py",
        "src/atlas/formalization/lean_interface.py",
    ]

    for mod in atlas_modules:
        record(f"Atlas module exists: {mod}", Path(mod).is_file())

    # Check all scripts compile (syntax check)
    scripts = list(Path("scripts").glob("*.py")) if Path("scripts").is_dir() else []
    for script in sorted(scripts):
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
        print("       Fix all path mismatches before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
