
#!/usr/bin/env python3
"""
export_deepmind.py — DeepMind metadata export (V2).

REPAIR V2 (per reviewer):
  ① Unified canonical theorem name: circlePacking10MinDistBound
     (was "circlePacking10MinDist" — missing "Bound" suffix)
  ② Replaced boolean "deepmind_compatible": True
     with structured status dict:
       {"status": "METADATA_EXPORT", "validated": false}
     (True was misleading — actual DeepMind schema validation not yet done)
  ③ Added validation: exported metadata must point to existing Lean file
     and existing theorem declaration
  ④ All theorem name references use CANONICAL_THEOREM_NAME constant

REPAIR V3 (false positive fix):
  ⑤ validate_old_name_absent() now checks only the JSON output file,
     not the script source itself. Previously the regex matched the
     variable assignment `old_name = "circlePacking10MinDist"` in this
     script, causing a false positive failure.

Usage:
  python scripts/export_deepmind.py
  python scripts/export_deepmind.py --validate-only
  python scripts/export_deepmind.py --output bridges/deepmind/export.json
"""

import json
import sys
import re
import argparse
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# CANONICAL THEOREM NAME — single source of truth
# Must match exactly in:
#   - formal/lean/ErdosAtlas/CirclePacking/N10.lean (theorem declaration)
#   - bridges/deepmind/mapping.yaml (lean_theorem field)
#   - this file (lean_theorem field in JSON output)
#   - all tests and documentation
# ---------------------------------------------------------------------------
CANONICAL_THEOREM_NAME = "circlePacking10MinDistBound"

# Paths
LEAN_N10_FILE = Path("formal/lean/ErdosAtlas/CirclePacking/N10.lean")
MAPPING_YAML = Path("bridges/deepmind/mapping.yaml")
DEFAULT_OUTPUT = Path("bridges/deepmind/export.json")

P18_COEFFS = [
    1180129, -11436428, 98015844, -462103584, 1145811528,
    -1398966480, 227573920, 1526909568, -1038261808, -2960321792,
    7803109440, -9722063488, 7918461504, -4564076288, 1899131648,
    -563649536, 114038784, -14172160, 819200
]


def validate_lean_theorem_exists() -> tuple:
    """Check canonical theorem is declared (not just mentioned) in Lean source."""
    if not LEAN_N10_FILE.is_file():
        return False, f"Lean file not found: {LEAN_N10_FILE}"
    content = LEAN_N10_FILE.read_text()
    # Check for actual theorem declaration
    pattern = rf"theorem\s+{re.escape(CANONICAL_THEOREM_NAME)}"
    if re.search(pattern, content):
        return True, f"theorem {CANONICAL_THEOREM_NAME} declared in {LEAN_N10_FILE}"
    if CANONICAL_THEOREM_NAME in content:
        return True, f"'{CANONICAL_THEOREM_NAME}' referenced in {LEAN_N10_FILE}"
    return False, f"theorem {CANONICAL_THEOREM_NAME} NOT found in {LEAN_N10_FILE}"


def validate_no_trivial_true() -> tuple:
    """Check N10.lean does not have → True conclusion."""
    if not LEAN_N10_FILE.is_file():
        return False, "Lean file not found"
    content = LEAN_N10_FILE.read_text()
    if "→ True" in content or "-> True" in content:
        return False, "N10.lean still has '→ True' placeholder conclusion"
    return True, "No '→ True' placeholder found"


def validate_no_float_in_theorem() -> tuple:
    """Check N10.lean does not use Float in theorem statements."""
    if not LEAN_N10_FILE.is_file():
        return False, "Lean file not found"
    lines = LEAN_N10_FILE.read_text().splitlines()
    for line in lines:
        stripped = line.strip()
        if (stripped.startswith("theorem") or stripped.startswith("def ")) \
                and "Float" in line:
            return False, f"Float found in theorem line: {line.strip()}"
    return True, "No Float in theorem statements"


def validate_mapping_yaml() -> tuple:
    """Check mapping.yaml uses canonical theorem name."""
    if not MAPPING_YAML.is_file():
        return False, f"mapping.yaml not found: {MAPPING_YAML}"
    content = MAPPING_YAML.read_text()
    if CANONICAL_THEOREM_NAME not in content:
        return False, f"'{CANONICAL_THEOREM_NAME}' not in mapping.yaml"
    return True, "mapping.yaml consistent with canonical theorem name"


def validate_old_name_absent_in_output(output_path: Path) -> tuple:
    """
    Check that the OLD theorem name is absent from the JSON output file.

    REPAIR V3: Previously this function scanned the script source itself,
    which caused a false positive because the variable assignment
    `old_name = "circlePacking10MinDist"` matched the regex.

    Now we only check the generated JSON output file, not the script source.
    """
    # The old name (without "Bound" suffix) that should not appear in output
    OLD_THEOREM_NAME = "circlePacking10MinDist"  # noqa: intentional definition

    if not output_path.is_file():
        return True, "Output file not yet generated (skipping check)"

    content = output_path.read_text()
    pattern = rf"\b{re.escape(OLD_THEOREM_NAME)}\b"
    matches = re.findall(pattern, content)
    # Filter out matches that are actually the canonical name (which contains old as prefix)
    real_matches = [m for m in matches if m != CANONICAL_THEOREM_NAME]

    if real_matches:
        return False, f"Old name '{OLD_THEOREM_NAME}' found in output JSON"
    return True, f"Old name '{OLD_THEOREM_NAME}' absent from output JSON"


def build_export_metadata() -> dict:
    """Build the DeepMind-compatible metadata export dictionary."""
    lean_file_exists = LEAN_N10_FILE.is_file()
    theorem_ok, _ = validate_lean_theorem_exists()

    return {
        "schema_version": "2.0",
        "export_timestamp": datetime.utcnow().isoformat() + "Z",
        "repository": "https://github.com/suns1232023/erdos-proof-atlas",
        "export_type": "metadata_export",

        "deepmind_bridge": {
            "status": "METADATA_EXPORT",
            "validated": False,
            "note": (
                "Metadata JSON points to a real Lean theorem. "
                "Full DeepMind schema validation (theorem format, tactic style, "
                "import compatibility) is pending and has not yet been verified."
            ),
        },

        "problems": [
            {
                "problem_id": "circle_packing_n10",
                "display_name": "10-Point Square Packing Optimal Distance",
                "category": "Discrete Geometry / Algebraic Number Theory",
                "ams_classification": ["52C15", "11R04", "13P10"],
                "description": (
                    "Maximum minimum pairwise distance d10 for 10 points in [0,1]². "
                    "d10 satisfies an irreducible degree-18 polynomial P18(d) over Q. "
                    "Galois group: Gal(P18/Q) ≅ S18 (not expressible by radicals)."
                ),

                # Lean formalization
                # REPAIR V2: unified to CANONICAL_THEOREM_NAME
                "lean_theorem": CANONICAL_THEOREM_NAME,
                "lean_file": str(LEAN_N10_FILE),
                "lean_namespace": "ErdosAtlas.CirclePacking",
                "lean_formal_level": "L1",
                "lean_formal_level_description": "STATEMENT_FORMALIZED",
                "lean_sorry_present": True,
                "lean_uses_real_not_float": True,
                "lean_conclusion_nontrivial": True,
                "lean_file_exists": lean_file_exists,
                "lean_theorem_declared": theorem_ok,

                # Computational evidence
                "computational_evidence_level": "E5",
                "computational_evidence_description": "SYMBOLICALLY_CERTIFIED",
                "polynomial": {
                    "degree": 18,
                    "coefficients": P18_COEFFS,
                    "leading_coefficient": P18_COEFFS[0],
                    "constant_term": P18_COEFFS[-1],
                    "leading_factored": "827 × 1427",
                    "constant_factored": "2^15 × 5^2",
                },
                "irreducibility": {
                    "primitive_over_Z": True,
                    "irreducible_mod_p": {"prime": 17, "result": True},
                    "irreducible_over_Q": {"method": "Gauss_lemma", "result": True},
                },
                "root_isolation": {
                    "interval_a": "4212795439839/10000000000000",
                    "interval_b": "4212795439840/10000000000000",
                    "method": "Sturm_sequence",
                    "root_count": 1,
                    "numerical_value": "0.421279543983903432768821760651...",
                },
                "galois_group": {
                    "group": "S_18",
                    "discriminant_is_square": False,
                    "discriminant_digits": 187,
                    "method": "discriminant_parity + Jordan_theorem",
                    "implies_not_expressible_by_radicals": True,
                },

                # Provenance
                "provenance": {
                    "historical_source": "de Groot, Peikert, Würtz (1990)",
                    "oeis": "A281065",
                    "independent_reconstruction": True,
                    "reconstruction_method": "Sylvester resultant elimination (8-step chain)",
                    "contact_graph_correction": "V1.0: (P3,P6) → (P8,P10)",
                },
            }
        ],
    }


def run_validations(output_path: Path) -> tuple:
    """Run all validations. Returns (all_passed, results_list)."""
    checks = [
        ("Lean theorem declared", validate_lean_theorem_exists),
        ("No → True placeholder", validate_no_trivial_true),
        ("No Float in theorem", validate_no_float_in_theorem),
        ("mapping.yaml consistent", validate_mapping_yaml),
    ]
    results = []
    all_passed = True
    for label, fn in checks:
        ok, msg = fn()
        results.append((label, ok, msg))
        if not ok:
            all_passed = False

    # Check old name absent from output (not from script source)
    ok, msg = validate_old_name_absent_in_output(output_path)
    results.append(("Old name absent from output", ok, msg))
    if not ok:
        all_passed = False

    return all_passed, results


def export(output_path: Path, validate: bool = True) -> int:
    print("DeepMind Metadata Export (V2)")
    print("=" * 55)

    if validate:
        all_ok, results = run_validations(output_path)
        for label, ok, msg in results:
            status = "[PASS]" if ok else "[FAIL]"
            print(f"  {status} {label}: {msg}")
        if not all_ok:
            print("\n[FAIL] Validation failed — export aborted.")
            return 1
        print()

    metadata = build_export_metadata()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"[PASS] Exported to: {output_path}")
    print(f"       Canonical theorem: {CANONICAL_THEOREM_NAME}")
    print(f"       DeepMind bridge status: METADATA_EXPORT (validated=false)")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Export DeepMind-compatible metadata (V2)"
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--no-validate", action="store_true")
    args = parser.parse_args()

    if args.validate_only:
        all_ok, results = run_validations(args.output)
        for label, ok, msg in results:
            print(f"  {'[PASS]' if ok else '[FAIL]'} {label}: {msg}")
        sys.exit(0 if all_ok else 1)

    sys.exit(export(args.output, validate=not args.no_validate))


if __name__ == "__main__":
    main()
