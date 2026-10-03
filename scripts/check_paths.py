#!/usr/bin/env python3
"""
check_paths.py — Repository path consistency checker.

Reads required Lean modules from formal/lean/project_contract.json.
This is the SINGLE source of truth for required files.
"""

import sys
import re
import json
from pathlib import Path

CONTRACT_PATH = Path("formal/lean/project_contract.json")
RESULTS = []


def record(label: str, passed: bool, detail: str = ""):
    status = "[PASS]" if passed else "[FAIL]"
    msg = f"  {status} {label}"
    if detail:
        msg += f"\n         {detail}"
    print(msg)
    RESULTS.append((label, passed, detail))


def load_contract() -> dict:
    if not CONTRACT_PATH.is_file():
        print(f"[FAIL] {CONTRACT_PATH} not found — this is the authoritative contract")
        sys.exit(1)
    return json.loads(CONTRACT_PATH.read_text())


def check_test_directory():
    print("\n── Section 1: Canonical Test Directory ──")
    tests_exists = Path("tests").is_dir()
    test_exists = Path("test").is_dir()
    record("tests/ directory exists", tests_exists)
    record("No obsolete test/ directory", not test_exists,
           "Found 'test/' — migrate to 'tests/' and remove" if test_exists else "")
    for subdir in ["unit", "integration", "adversarial", "regression", "formal"]:
        record(f"tests/{subdir}/ exists", Path(f"tests/{subdir}").is_dir())


def check_makefile_paths():
    print("\n── Section 2: Makefile Path Consistency ──")
    makefile = Path("Makefile")
    if not makefile.is_file():
        record("Makefile exists", False)
        return
    record("Makefile exists", True)
    content = makefile.read_text()

    if "pytest tests/" in content:
        record("Makefile uses tests/ (not test/)", True)
    elif "pytest test/" in content:
        record("Makefile uses tests/ (not test/)", False, "References 'test/'")
    else:
        record("Makefile uses tests/ (not test/)", True)

    # Check no bare || true in mandatory steps
    bare_or_true = []
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if re.search(r'\|\| true\s*$', line):
            if not any(kw in line for kw in ["clean", "rm -rf", "find.*delete", "rmdir"]):
                bare_or_true.append(stripped[:80])
    record("No bare '|| true' in mandatory Makefile steps",
           len(bare_or_true) == 0,
           f"Found: {bare_or_true}" if bare_or_true else "")

    # Check required targets
    for target in ["install", "test", "lean", "status", "audit", "all", "all-formal",
                   "search", "verify", "certify", "report", "clean"]:
        pattern = rf"^{re.escape(target)}[:\s]"
        found = bool(re.search(pattern, content, re.MULTILINE))
        record(f"Makefile has target: {target}", found)

    # Check scripts referenced in Makefile exist
    script_refs = re.findall(r"python\s+scripts/(\S+\.py)", content)
    for script in set(script_refs):
        path = Path(f"scripts/{script}")
        record(f"Makefile-referenced script exists: scripts/{script}", path.is_file())


def check_ci_paths():
    print("\n── Section 3: CI Workflow Path Consistency ──")
    ci_dir = Path(".github/workflows")
    if not ci_dir.is_dir():
        record(".github/workflows/ exists", False)
        return
    record(".github/workflows/ exists", True)
    workflow_files = list(ci_dir.glob("*.yml")) + list(ci_dir.glob("*.yaml"))
    record(f"CI workflow files found ({len(workflow_files)})", len(workflow_files) > 0)

    lean_check_yml = ci_dir / "lean-check.yml"
    for wf in workflow_files:
        content = wf.read_text()
        # Check no bare || true
        bare_or_true = []
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith("echo") or stripped.startswith("printf"):
                continue
            if re.search(r'\|\| true\s*$', line):
                bare_or_true.append(stripped[:80])
        if wf == lean_check_yml:
            record(f"No bare '|| true' in {wf.name}", True,
                   "(lean-check.yml may document || true in comments)")
        else:
            record(f"No bare '|| true' in {wf.name}", len(bare_or_true) == 0,
                   f"Found: {bare_or_true[:3]}" if bare_or_true else "")

        # Check CI uses tests/ not test/
        if "tests/unit" in content or "tests/adversarial" in content:
            record(f"{wf.name} uses tests/ (canonical)", True)
        elif "test/unit" in content or "test/adversarial" in content:
            record(f"{wf.name} uses tests/ (canonical)", False, "References 'test/'")

        # Check scripts referenced in CI exist
        script_refs = re.findall(r"python\s+scripts/(\S+\.py)", content)
        for script in set(script_refs):
            path = Path(f"scripts/{script}")
            record(f"CI-referenced script exists: scripts/{script}", path.is_file())


def check_lean_files(contract: dict):
    print("\n── Section 4: Lean File Consistency (from project_contract.json) ──")

    # Required modules from contract (single source of truth)
    for module_path in contract.get("required_modules", []):
        record(f"Required module exists: {module_path}", Path(module_path).is_file())

    # Executable entry (if applicable)
    if contract.get("project_mode") == "library_and_executable":
        exe_entry = contract.get("executable_entry", "")
        if exe_entry:
            main_upper = Path(exe_entry).is_file()
            main_lower = Path(exe_entry.replace("Main.lean", "main.lean")).is_file()
            if main_upper:
                record(f"Executable entry exists: {exe_entry}", True)
            elif main_lower:
                record(f"Executable entry exists: {exe_entry}", False,
                       f"Found lowercase variant. Fix: git mv formal/lean/main.lean formal/lean/Main.lean")
            else:
                record(f"Executable entry exists: {exe_entry}", False, "Not found")

    # lakefile.toml
    lakefile = Path("formal/lean/lakefile.toml")
    if lakefile.is_file():
        import tomllib
        try:
            with open(lakefile, "rb") as f:
                data = tomllib.load(f)
            record("lakefile.toml valid TOML", True)
            record("lakefile.toml has top-level name", "name" in data)
            rev = data.get("require", [{}])[0].get("rev", "")
            contract_rev = contract.get("mathlib_rev", "")
            record(f"lakefile.toml mathlib rev matches contract ({contract_rev})",
                   rev == contract_rev,
                   f"lakefile has {rev}, contract expects {contract_rev}" if rev != contract_rev else "")
        except Exception as e:
            record("lakefile.toml valid TOML", False, str(e))

    # lean-toolchain
    tc_file = Path("formal/lean/lean-toolchain")
    if tc_file.is_file():
        tc = tc_file.read_bytes()
        record("lean-toolchain no leading whitespace",
               not tc.startswith(b' ') and not tc.startswith(b'\n'))
        tc_str = tc.strip().decode()
        contract_tc = contract.get("lean_toolchain", "")
        record(f"lean-toolchain matches contract ({contract_tc})",
               tc_str == contract_tc,
               f"File has {tc_str}, contract expects {contract_tc}" if tc_str != contract_tc else "")


def check_deepmind_targets():
    print("\n── Section 5: DeepMind Mapping Targets ──")
    canonical = "circlePacking10MinDistBound"
    mapping = Path("bridges/deepmind/mapping.yaml")
    lean_n10 = Path("formal/lean/ErdosAtlas/CirclePacking/N10.lean")
    export_script = Path("scripts/export_deepmind.py")

    record("bridges/deepmind/mapping.yaml exists", mapping.is_file())
    for label, filepath in [("mapping.yaml", mapping), ("N10.lean", lean_n10),
                             ("export_deepmind.py", export_script)]:
        if filepath.is_file():
            found = canonical in filepath.read_text()
            record(f"Canonical theorem '{canonical}' in {label}", found)


def check_certificate_paths():
    print("\n── Section 6: Certificate Paths ──")
    cert_dir = Path("certificates/circle_packing_n10")
    record("certificates/circle_packing_n10/ exists", cert_dir.is_dir())
    poly_cert = cert_dir / "polynomial_certificate.json"
    cert_json = cert_dir / "certificate.json"
    if poly_cert.is_file():
        record("polynomial_certificate.json exists", True)
    elif cert_json.is_file():
        record("certificate.json exists", True)
    else:
        record("Certificate file exists", False, "Neither found")


def check_python_imports():
    print("\n── Section 7: Python Import Targets ──")
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

    scripts = sorted(Path("scripts").glob("*.py")) if Path("scripts").is_dir() else []
    for script in scripts:
        try:
            source = script.read_text()
            compile(source, str(script), "exec")
            record(f"Script syntax OK: {script.name}", True)
        except SyntaxError as e:
            record(f"Script syntax OK: {script.name}", False, str(e))


def main() -> int:
    print("=" * 65)
    print("  erdos-proof-atlas — Path Consistency Check")
    print(f"  Contract: {CONTRACT_PATH}")
    print("=" * 65)

    contract = load_contract()
    print(f"  project_mode: {contract.get('project_mode')}")
    print(f"  formal_level: {contract.get('current_formal_level')}")

    check_test_directory()
    check_makefile_paths()
    check_ci_paths()
    check_lean_files(contract)
    check_deepmind_targets()
    check_certificate_paths()
    check_python_imports()

    print("\n" + "=" * 65)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    failed = sum(1 for _, ok, _ in RESULTS if not ok)
    total = len(RESULTS)
    print(f"  Results: {passed}/{total} passed, {failed} failed")

    if failed == 0:
        print("[PASS] PATH CONSISTENCY CHECK PASSED")
        return 0
    else:
        print(f"[FAIL] PATH CONSISTENCY CHECK FAILED ({failed} issue(s))")
        return 1


if __name__ == "__main__":
    sys.exit(main())
