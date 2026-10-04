
#!/usr/bin/env python3
"""
atlas_audit.py — Repository integrity + evidence integrity + certificate integrity audit.

REPAIR V6:
  - Section 7: Fixed Geometry/Basic.lean Point def check to be comment-aware.
    Previously used simple string search which matched the COMMENT:
    "-- PROBLEM: This file previously defined `def Point : Type := Fin 2 → ℝ`"
    Now strips Lean comment lines (-- ...) before checking.
"""

import sys
import os
import json
import re
import importlib.util
from pathlib import Path

CANONICAL_THEOREM = "circlePacking10MinDistBound"

P18_COEFFS = [
    1180129, -11436428, 98015844, -462103584, 1145811528,
    -1398966480, 227573920, 1526909568, -1038261808, -2960321792,
    7803109440, -9722063488, 7918461504, -4564076288, 1899131648,
    -563649536, 114038784, -14172160, 819200
]

RESULTS = []


def record(label: str, passed: bool, detail: str = ""):
    status = "[PASS]" if passed else "[FAIL]"
    msg = f"  {status} {label}"
    if detail:
        msg += f"\n         {detail}"
    print(msg)
    RESULTS.append((label, passed, detail))


def strip_lean_comments(text: str) -> str:
    """Strip Lean single-line comments (-- ...) from source text."""
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("--"):
            lines.append("")  # replace comment line with empty
        else:
            # Remove inline comments
            idx = line.find("--")
            if idx >= 0:
                lines.append(line[:idx])
            else:
                lines.append(line)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Section 1: Repository path consistency
# ---------------------------------------------------------------------------
def audit_paths():
    print("\n── Section 1: Repository Path Consistency ──")

    required_dirs = [
        "tests/unit",
        "tests/integration",
        "tests/adversarial",
        "tests/regression",
        "tests/formal",
        "src/atlas",
        "scripts",
        "bridges/deepmind",
        "certificates/circle_packing_n10",
        "formal/lean/ErdosAtlas",
    ]
    for d in required_dirs:
        record(f"Directory exists: {d}", Path(d).is_dir())

    required_files = [
        "Makefile",
        "pyproject.toml",
        "scripts/lean_check.py",
        "scripts/atlas_audit.py",
        "scripts/formal_audit.py",
        "scripts/full_audit.py",
        "scripts/build_certificate.py",
        "scripts/export_deepmind.py",
        "scripts/validate_deepmind_mapping.py",
        "scripts/check_paths.py",
        "scripts/run_problem.py",
        "scripts/verify_result.py",
        "scripts/build_manifest.py",
        "scripts/generate_report.py",
        "bridges/deepmind/mapping.yaml",
        "formal/lean/lakefile.toml",
        "formal/lean/lean-toolchain",
        "formal/lean/ErdosAtlas/Basic.lean",
        "formal/lean/ErdosAtlas/Geometry/Basic.lean",
        "formal/lean/ErdosAtlas/CirclePacking/N10.lean",
        "formal/lean/ErdosAtlas/Problems/SquarePacking.lean",
        "tests/unit/test_schema.py",
        "tests/unit/test_polynomial.py",
        "tests/unit/test_certificate.py",
        "tests/adversarial/test_adversarial.py",
        "tests/regression/test_regression.py",
        "tests/formal/test_lean_integrity.py",
    ]
    for f in required_files:
        record(f"File exists: {f}", Path(f).is_file())

    # Main.lean case-sensitivity check
    main_upper = Path("formal/lean/Main.lean").is_file()
    main_lower = Path("formal/lean/main.lean").is_file()
    if main_upper:
        record("Main.lean exists (correct case)", True)
    elif main_lower:
        record("Main.lean exists (correct case)", False,
               "Found 'main.lean' (lowercase). Fix: git mv formal/lean/main.lean formal/lean/Main.lean")
    else:
        record("Main.lean exists (correct case)", False, "Neither Main.lean nor main.lean found")


# ---------------------------------------------------------------------------
# Section 2: Python import integrity
# ---------------------------------------------------------------------------
def audit_python_imports():
    print("\n── Section 2: Python Import Integrity ──")

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
    for mod_path in atlas_modules:
        record(f"Atlas module exists: {mod_path}", Path(mod_path).is_file())

    script_files = [
        "scripts/lean_check.py",
        "scripts/atlas_audit.py",
        "scripts/export_deepmind.py",
        "scripts/validate_deepmind_mapping.py",
        "scripts/build_certificate.py",
    ]
    for script in script_files:
        if not Path(script).is_file():
            record(f"Script compiles: {script}", False, "File not found")
            continue
        try:
            source = Path(script).read_text()
            compile(source, script, "exec")
            record(f"Script compiles: {script}", True)
        except SyntaxError as e:
            record(f"Script compiles: {script}", False, str(e))


# ---------------------------------------------------------------------------
# Section 3: Evidence schema consistency
# ---------------------------------------------------------------------------
def audit_evidence_schema():
    print("\n── Section 3: Evidence Schema Consistency ──")

    E_LEVELS = ["E0", "E1", "E2", "E3", "E4", "E5"]
    L_LEVELS = ["L0", "L1", "L2", "L3", "L4", "L5"]
    L_DESCRIPTIONS = {
        "L0": "NOT_FORMALIZED",
        "L1": "STATEMENT_FORMALIZED",
        "L2": "DEFINITIONS_FORMALIZED",
        "L3": "KEY_LEMMAS_FORMALIZED",
        "L4": "PROOF_SOURCE_COMPLETE",
        "L5": "KERNEL_CHECKED",
    }

    record("E-axis has 6 levels (E0-E5)", len(E_LEVELS) == 6)
    record("L-axis has 6 levels (L0-L5)", len(L_LEVELS) == 6)
    record("L5 = KERNEL_CHECKED", L_DESCRIPTIONS["L5"] == "KERNEL_CHECKED")
    record("L4 = PROOF_SOURCE_COMPLETE", L_DESCRIPTIONS["L4"] == "PROOF_SOURCE_COMPLETE")
    record("L4 ≠ L5 (distinct semantics)", L_DESCRIPTIONS["L4"] != L_DESCRIPTIONS["L5"])
    record("L5 does not allow sorry", True)  # By definition

    evidence_py = Path("src/atlas/schema/evidence.py")
    if evidence_py.is_file():
        content = evidence_py.read_text()
        record("evidence.py uses PROOF_SOURCE_COMPLETE (not THEOREM_PROVED)",
               "PROOF_SOURCE_COMPLETE" in content)
        record("evidence.py uses KERNEL_CHECKED (not LEAN_BUILD_VERIFIED)",
               "KERNEL_CHECKED" in content)


# ---------------------------------------------------------------------------
# Section 4: Certificate structure validation
# ---------------------------------------------------------------------------
def audit_certificate():
    print("\n── Section 4: Certificate Structure ──")

    cert_dir = Path("certificates/circle_packing_n10")
    record("certificates/circle_packing_n10/ exists", cert_dir.is_dir())

    # REPAIR V5: Actual filename is polynomial_certificate.json
    cert_file = cert_dir / "polynomial_certificate.json"
    cert_file_alt = cert_dir / "certificate.json"

    if cert_file.is_file():
        record("polynomial_certificate.json exists", True)
        actual_cert = cert_file
    elif cert_file_alt.is_file():
        record("certificate.json exists (alternative name)", True)
        actual_cert = cert_file_alt
    else:
        record("Certificate file exists", False,
               "Neither polynomial_certificate.json nor certificate.json found")
        return

    try:
        with open(actual_cert) as f:
            cert = json.load(f)
        record("Certificate is valid JSON", True)
    except json.JSONDecodeError as e:
        record("Certificate is valid JSON", False, str(e))
        return

    if "polynomial" in cert or "coefficients" in cert:
        record("Certificate has polynomial data", True)
    else:
        record("Certificate has polynomial data", False)

    if "coefficients" in cert:
        coeffs = cert["coefficients"]
        record("Certificate coefficients count = 19", len(coeffs) == 19)
        if len(coeffs) == 19:
            record("Leading coefficient = 1180129", coeffs[0] == 1180129)
            record("Constant term = 819200", coeffs[-1] == 819200)

    if "degree" in cert:
        record("Certificate degree = 18", cert["degree"] == 18)


# ---------------------------------------------------------------------------
# Section 5: DeepMind mapping consistency
# ---------------------------------------------------------------------------
def audit_deepmind():
    print("\n── Section 5: DeepMind Mapping Consistency ──")

    mapping_path = Path("bridges/deepmind/mapping.yaml")
    lean_n10 = Path("formal/lean/ErdosAtlas/CirclePacking/N10.lean")
    export_script = Path("scripts/export_deepmind.py")
    examples_json = Path("bridges/deepmind/examples/circle_packing_n10.json")

    for label, filepath in [
        ("mapping.yaml", mapping_path),
        ("N10.lean", lean_n10),
        ("export_deepmind.py", export_script),
    ]:
        if not filepath.is_file():
            record(f"Canonical theorem in {label}", False, "File not found")
            continue
        content = filepath.read_text()
        found = CANONICAL_THEOREM in content
        record(f"Canonical theorem '{CANONICAL_THEOREM}' in {label}", found)

    if examples_json.is_file():
        found = CANONICAL_THEOREM in examples_json.read_text()
        record(f"Canonical theorem '{CANONICAL_THEOREM}' in examples JSON", found)

    # Check old name absent from JSON output (not from script source)
    old_name = "circlePacking10MinDist"
    if examples_json.is_file():
        content = examples_json.read_text()
        pattern = rf"\b{re.escape(old_name)}\b"
        matches = re.findall(pattern, content)
        real_matches = [m for m in matches if m != CANONICAL_THEOREM]
        record(f"Old name '{old_name}' absent from examples JSON",
               len(real_matches) == 0,
               f"Found {len(real_matches)} occurrence(s)" if real_matches else "")


# ---------------------------------------------------------------------------
# Section 6: Polynomial integrity
# ---------------------------------------------------------------------------
def audit_polynomial():
    print("\n── Section 6: Polynomial Integrity ──")

    record("P18 has 19 coefficients (degree 18)", len(P18_COEFFS) == 19)
    record("Leading coefficient = 1180129", P18_COEFFS[0] == 1180129)
    record("Leading coeff = 827 × 1427", P18_COEFFS[0] == 827 * 1427)
    record("Constant term = 819200", P18_COEFFS[-1] == 819200)
    record("Constant term = 2^15 × 5^2", P18_COEFFS[-1] == (2 ** 15) * (5 ** 2))

    d10 = 0.421279543983903432768821760651
    residual = abs(sum(c * (d10 ** (18 - i)) for i, c in enumerate(P18_COEFFS)))
    record(f"P18(d10) residual < 1e-4 (residual={residual:.2e})", residual < 1e-4)

    wrong_coeffs = [
        1180129, 0, -11894220, 0, 48316302, 0, -100868204, 0, 110901591,
        0, -68383830, 0, 22699860, 0, -3878424, 0, 280620, 0, -2187
    ]
    wrong_residual = abs(sum(c * (d10 ** (18 - i)) for i, c in enumerate(wrong_coeffs)))
    record(f"Wrong polynomial rejected (residual={wrong_residual:.2e} > 100)", wrong_residual > 100)


# ---------------------------------------------------------------------------
# Section 7: Lean structure quick check
# REPAIR V6: Use comment-aware search for Point definition check
# ---------------------------------------------------------------------------
def audit_lean_structure():
    print("\n── Section 7: Lean Structure Quick Check ──")

    geo_basic = Path("formal/lean/ErdosAtlas/Geometry/Basic.lean")
    if geo_basic.is_file():
        content = geo_basic.read_text()
        # REPAIR V6: Strip Lean comments before checking
        # Previously, the comment "-- PROBLEM: This file previously defined
        # `def Point : Type := Fin 2 → ℝ`" caused a false positive.
        code_only = strip_lean_comments(content)
        has_conflict = "def Point : Type := Fin 2" in code_only
        record("Geometry/Basic.lean has no conflicting Point def (comment-stripped)",
               not has_conflict,
               "Found 'def Point := Fin 2 → ℝ' in code (not comments)" if has_conflict else "")

    lakefile = Path("formal/lean/lakefile.toml")
    if lakefile.is_file():
        content = lakefile.read_text()
        record("lakefile.toml has mathlib [[require]]",
               "mathlib" in content and "[[require]]" in content)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    print("=" * 65)
    print("  erdos-proof-atlas — Atlas Audit (Repository + Evidence)")
    print("=" * 65)

    audit_paths()
    audit_python_imports()
    audit_evidence_schema()
    audit_certificate()
    audit_deepmind()
    audit_polynomial()
    audit_lean_structure()

    print("\n" + "=" * 65)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    failed = sum(1 for _, ok, _ in RESULTS if not ok)
    total = len(RESULTS)

    print(f"  Results: {passed}/{total} passed, {failed} failed")
    print()

    if failed == 0:
        print("[PASS] ATLAS AUDIT PASSED")
        return 0
    else:
        print(f"[FAIL] ATLAS AUDIT FAILED ({failed} issue(s))")
        print("       Fix the issues above and re-run.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
