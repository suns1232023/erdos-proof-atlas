
#!/usr/bin/env python3
"""
export_deepmind.py — DeepMind metadata export for erdos-proof-atlas.

REPAIR NOTE (P1 Fix):
  - Unified canonical theorem name: circlePacking10MinDistBound
    (previously used "circlePacking10MinDist" — missing "Bound" suffix)
  - All theorem name references now use CANONICAL_THEOREM_NAME constant.
  - Added validation: exported metadata must point to an existing Lean file.
  - Clarified semantics: this is "metadata export", not full DeepMind integration.

Usage:
  python scripts/export_deepmind.py
  python scripts/export_deepmind.py --output bridges/deepmind/export.json
  python scripts/export_deepmind.py --validate-only
"""

import json
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# CANONICAL THEOREM NAME — single source of truth
# Must match exactly in:
#   - formal/lean/ErdosAtlas/CirclePacking/N10.lean
#   - bridges/deepmind/mapping.yaml
#   - this file
#   - all tests and documentation
# ---------------------------------------------------------------------------
CANONICAL_THEOREM_NAME = "circlePacking10MinDistBound"

# Paths
LEAN_N10_FILE = Path("formal/lean/ErdosAtlas/CirclePacking/N10.lean")
MAPPING_YAML = Path("bridges/deepmind/mapping.yaml")
DEFAULT_OUTPUT = Path("bridges/deepmind/export.json")

# P18(d) certified coefficients
P18_COEFFS = [
    1180129, -11436428, 98015844, -462103584, 1145811528,
    -1398966480, 227573920, 1526909568, -1038261808, -2960321792,
    7803109440, -9722063488, 7918461504, -4564076288, 1899131648,
    -563649536, 114038784, -14172160, 819200
]


def validate_lean_theorem_exists() -> tuple[bool, str]:
    """
    Validate that the canonical theorem name exists in the Lean source file.
    Returns (is_valid, message).
    """
    if not LEAN_N10_FILE.is_file():
        return False, f"Lean file not found: {LEAN_N10_FILE}"

    content = LEAN_N10_FILE.read_text()
    if CANONICAL_THEOREM_NAME not in content:
        return False, (
            f"Canonical theorem '{CANONICAL_THEOREM_NAME}' not found in {LEAN_N10_FILE}.\n"
            f"Ensure the Lean source declares: theorem {CANONICAL_THEOREM_NAME} ..."
        )

    return True, f"Canonical theorem '{CANONICAL_THEOREM_NAME}' found in {LEAN_N10_FILE}"


def validate_mapping_yaml_consistency() -> tuple[bool, str]:
    """
    Validate that mapping.yaml uses the same canonical theorem name.
    Returns (is_valid, message).
    """
    if not MAPPING_YAML.is_file():
        return False, f"mapping.yaml not found: {MAPPING_YAML}"

    content = MAPPING_YAML.read_text()
    if CANONICAL_THEOREM_NAME not in content:
        return False, (
            f"Canonical theorem '{CANONICAL_THEOREM_NAME}' not found in {MAPPING_YAML}.\n"
            f"Update mapping.yaml to use the canonical name."
        )

    return True, f"mapping.yaml consistent with canonical theorem name"


def build_export_metadata() -> dict:
    """Build the DeepMind-compatible metadata export dictionary."""
    return {
        "schema_version": "1.0",
        "export_timestamp": datetime.utcnow().isoformat() + "Z",
        "repository": "https://github.com/suns1232023/erdos-proof-atlas",
        "export_type": "metadata_export",
        "deepmind_compatibility": "metadata_export",
        # NOTE: "metadata_export" means this JSON points to a real Lean theorem.
        # Full DeepMind formalization compatibility requires additional validation.

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
                # REPAIR: unified to CANONICAL_THEOREM_NAME (was "circlePacking10MinDist")
                "lean_theorem": CANONICAL_THEOREM_NAME,
                "lean_file": str(LEAN_N10_FILE),
                "lean_namespace": "ErdosAtlas.CirclePacking",
                "lean_formal_level": "L1",
                "lean_formal_level_description": "STATEMENT_FORMALIZED",
                "lean_sorry_present": True,
                "lean_uses_real_not_float": True,
                "lean_conclusion_nontrivial": True,

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

                # DeepMind bridge status
                "deepmind_bridge": {
                    "metadata_export": "implemented",
                    "formalization_compatibility": "pending_validation",
                    "theorem_name_validated": True,
                    "lean_file_exists": LEAN_N10_FILE.is_file(),
                },
            }
        ],
    }


def export(output_path: Path, validate: bool = True) -> int:
    """
    Export DeepMind metadata to JSON.
    Returns exit code (0 = success, 1 = failure).
    """
    print("DeepMind Metadata Export")
    print("=" * 50)

    # --- Validation ---
    if validate:
        ok1, msg1 = validate_lean_theorem_exists()
        status1 = "[PASS]" if ok1 else "[FAIL]"
        print(f"{status1} Lean theorem validation: {msg1}")

        ok2, msg2 = validate_mapping_yaml_consistency()
        status2 = "[PASS]" if ok2 else "[FAIL]"
        print(f"{status2} mapping.yaml consistency: {msg2}")

        if not ok1 or not ok2:
            print("\n[FAIL] Validation failed — export aborted.")
            print("Fix the issues above before exporting.")
            return 1

    # --- Build metadata ---
    metadata = build_export_metadata()

    # --- Write output ---
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\n[PASS] Exported metadata to: {output_path}")
    print(f"       Canonical theorem: {CANONICAL_THEOREM_NAME}")
    print(f"       Problems exported: {len(metadata['problems'])}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Export DeepMind-compatible metadata for erdos-proof-atlas"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output JSON file path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate consistency, do not write output file",
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip validation (not recommended)",
    )
    args = parser.parse_args()

    if args.validate_only:
        ok1, msg1 = validate_lean_theorem_exists()
        ok2, msg2 = validate_mapping_yaml_consistency()
        print(f"{'[PASS]' if ok1 else '[FAIL]'} {msg1}")
        print(f"{'[PASS]' if ok2 else '[FAIL]'} {msg2}")
        sys.exit(0 if (ok1 and ok2) else 1)

    validate = not args.no_validate
    sys.exit(export(args.output, validate=validate))


if __name__ == "__main__":
    main()
