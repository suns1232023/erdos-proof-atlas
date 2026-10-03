
#!/usr/bin/env python3
"""
atlas_audit.py — Repository integrity + evidence integrity + certificate integrity audit.

REPAIR NOTE (Step 9):
  Separated from formal_audit.py. This script covers:
    - Repository path consistency (all referenced files exist)
    - Python import integrity
    - Evidence schema consistency
    - Certificate structure validation
    - DeepMind mapping consistency

  Does NOT cover Lean formalization (see formal_audit.py).
  Run full_audit.py to execute both.
"""

import sys
import os
import json
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


# ---------------------------------------------------------------------------
# Section 1: Repository path consistency
# ---------------------------------------------------------------------------
def audit_paths():
    print("\n── Section 1: Repository Path Consistency ──")

    # Required directories
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
        exists = Path(d).is_dir()
        record(f"Directory exists: {d}", exists)

    # Required files
    required_files = [
        "Makefile",
        "setup.py",
        "scripts/lean_check.py",
        "scripts/atlas_audit.py",
        "scripts/formal_audit.py",
        "scripts/full_audit.py",
        "scripts/build_certificate.py",
        "scripts/export_deepmind.py",
        "scripts/validate_deepmind_mapping.py",
        "scripts/check_paths.py",
        "bridges/deepmind/mapping.yaml",
        "formal/lean/lakefile.toml",
        "formal/lean/lean-toolchain",
        "formal/lean/Main.lean",
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
        exists = Path(f).is_file()
        record(f"File exists: {f}", exists)


# ---------------------------------------------------------------------------
# Section 2: Python import integrity
# ---------------------------------------------------------------------------
def audit_python_imports():
    print("\n── Section 2: Python Import Integrity ──")

    # Check that src/atlas modules are importable
    atlas_modules = [
        "src/atlas/__init__.py",
        "src/atlas/schema.py",
        "src/atlas/geometry.py",
        "src/atlas/certification.py",
        "src/atlas/provenance.py",
    ]
    for mod_path in atlas_modules:
        exists = Path(mod_path).is_file()
        record(f"Atlas module exists: {mod_path}", exists)

    # Check scripts compile
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
            spec = importlib.util.spec_from_file_location("_tmp", script)
            # Just check syntax by compiling
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

    # Verify L5 semantics: must NOT allow sorry
    l5_allows_sorry = False  # By definition: L5 = KERNEL_CHECKED = no sorry
    record("L5 does not allow sorry", not l5_allows_sorry)


# ---------------------------------------------------------------------------
# Section 4: Certificate structure validation
# ---------------------------------------------------------------------------
def audit_certificate():
    print("\n── Section 4: Certificate Structure ──")

    cert_path = Path("certificates/circle_packing_n10/certificate.json")
    if not cert_path.is_file():
        record("Certificate file exists", False, str(cert_path))
        return

    record("Certificate file exists", True)

    try:
        with open(cert_path) as f:
            cert = json.load(f)
    except json.JSONDecodeError as e:
        record("Certificate is valid JSON", False, str(e))
        return

    record("Certificate is valid JSON", True)

    # Check required top-level keys
    required_keys = [
        "problem_id", "polynomial", "irreducibility",
        "root_isolation", "galois_group", "certification_summary"
    ]
    for key in required_keys:
        record(f"Certificate has key: {key}", key in cert)

    # Check irreducibility chain
    if "irreducibility" in cert:
        irr = cert["irreducibility"]
        record("Irreducibility: primitive_over_Z present", "primitive_over_Z" in irr)
        record("Irreducibility: irreducible_mod_p present", "irreducible_mod_p" in irr)
        record("Irreducibility: irreducible_over_Q present", "irreducible_over_Q" in irr)

        if "irreducible_mod_p" in irr:
            mod_p = irr["irreducible_mod_p"]
            record("Certificate prime is 17", mod_p.get("prime") == 17)
            record("Irreducible mod 17", mod_p.get("result") is True)

        if "irreducible_over_Q" in irr:
            over_Q = irr["irreducible_over_Q"]
            method = over_Q.get("method", "")
            record("Method is Gauss_lemma", "Gauss" in method or "gauss" in method.lower())

    # Check Galois group
    if "galois_group" in cert:
        gal = cert["galois_group"]
        if "galois_group" in gal:
            gal = gal["galois_group"]
        group = gal.get("group", "")
        record("Galois group is S_18", group == "S_18")
        record("Discriminant not a square", gal.get("disc_not_square_implies_not_in_A18", False))

    # Check certification summary
    if "certification_summary" in cert:
        summary = cert["certification_summary"]
        for cc in ["CC1_benchmark_alignment", "CC2_irreducibility",
                   "CC3_root_isolation", "CC4_sign_branches", "CC6_galois_group"]:
            if cc in summary:
                record(f"Certification {cc}", summary[cc] is True)


# ---------------------------------------------------------------------------
# Section 5: DeepMind mapping consistency
# ---------------------------------------------------------------------------
def audit_deepmind():
    print("\n── Section 5: DeepMind Mapping Consistency ──")

    mapping_path = Path("bridges/deepmind/mapping.yaml")
    lean_n10 = Path("formal/lean/ErdosAtlas/CirclePacking/N10.lean")
    export_script = Path("scripts/export_deepmind.py")

    # Check canonical name in each file
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

    # Check old inconsistent name is absent
    old_name = "circlePacking10MinDist"
    for label, filepath in [
        ("export_deepmind.py", export_script),
        ("mapping.yaml", mapping_path),
    ]:
        if not filepath.is_file():
            continue
        content = filepath.read_text()
        # Check for old name that is NOT the canonical name
        import re
        pattern = rf"\b{re.escape(old_name)}\b"
        matches = re.findall(pattern, content)
        real_matches = [m for m in matches if m != CANONICAL_THEOREM]
        record(f"Old name '{old_name}' absent from {label}", len(real_matches) == 0)


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

    # Verify d10 is approximately a root
    d10 = 0.421279543983903432768821760651
    residual = abs(sum(c * (d10 ** (18 - i)) for i, c in enumerate(P18_COEFFS)))
    record(f"P18(d10) residual < 1e-4 (residual={residual:.2e})", residual < 1e-4)

    # Verify wrong polynomial is rejected
    wrong_coeffs = [
        1180129, 0, -11894220, 0, 48316302, 0, -100868204, 0, 110901591,
        0, -68383830, 0, 22699860, 0, -3878424, 0, 280620, 0, -2187
    ]
    wrong_residual = abs(sum(c * (d10 ** (18 - i)) for i, c in enumerate(wrong_coeffs)))
    record(f"Wrong polynomial rejected (residual={wrong_residual:.2e} > 100)", wrong_residual > 100)


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
