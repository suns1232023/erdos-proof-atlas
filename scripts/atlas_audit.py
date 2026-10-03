#!/usr/bin/env python3
"""Full audit: computational + formal evidence chain."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from atlas.verification.verifier import verify_adversarial_cases
from atlas.schema.evidence import validate_upgrade, ComputationalEvidence, FormalEvidence

def main() -> int:
    print("=" * 60)
    print("ERDŐS PROOF ATLAS — FORMAL AUDIT")
    print("=" * 60)
    errors = 0

    print("\n[1] Adversarial rejection tests...")
    for case, ok in verify_adversarial_cases().items():
        print(f"  {'PASS' if ok else 'FAIL'}: {case}")
        if not ok: errors += 1

    print("\n[2] Evidence guardrail tests...")
    for from_s, to_s in [("NUMERICAL","THEOREM"),("COMPUTATIONAL","THEOREM"),("AI_GENERATED","VERIFIED"),("CERTIFICATE","FORMAL_PROOF")]:
        try:
            validate_upgrade(from_s, to_s)
            print(f"  FAIL: {from_s}->{to_s} should be blocked"); errors += 1
        except ValueError:
            print(f"  PASS: {from_s}->{to_s} correctly blocked")

    print("\n[3] Certificate integrity checks...")
    cert_dir = Path("certificates/circle_packing_n10")
    for cert_name in ["polynomial_certificate.json"]:
        p = cert_dir / cert_name
        if p.exists():
            data = json.loads(p.read_text())
            if data.get("status") in ("THEOREM","FORMAL_PROOF"):
                print(f"  FAIL: {cert_name} has forbidden status"); errors += 1
            else:
                print(f"  PASS: {cert_name} status OK")
        else:
            print(f"  SKIP: {cert_name} not found (run build_certificate.py first)")

    print("\n[4] Result status checks...")
    result_dir = Path("results/latest")
    for fname in ["search_result.json"]:
        p = result_dir / fname
        if p.exists():
            data = json.loads(p.read_text())
            if data.get("status") != "NUMERICAL":
                print(f"  FAIL: {fname} status is not NUMERICAL"); errors += 1
            else:
                print(f"  PASS: {fname} status is NUMERICAL")
        else:
            print(f"  SKIP: {fname} not found")

    print("\n[5] Lean status...")
    from atlas.formalization.lean_interface import check_lean_available, run_lean_build
    if check_lean_available():
        result = run_lean_build(Path("formal/lean"))
        level = result.formal_level()
        print(f"  Lean build: {'PASS' if result.success else 'FAIL'}, level: {level}")
        if not result.success: errors += 1
    else:
        print("  SKIP: Lean not installed (formal level: L0)")

    print(f"\n{'='*60}")
    print(f"AUDIT {'PASSED' if errors == 0 else 'FAILED'} — {errors} error(s)")
    return 0 if errors == 0 else 1

if __name__ == "__main__": sys.exit(main())
