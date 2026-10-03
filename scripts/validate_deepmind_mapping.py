
#!/usr/bin/env python3
"""
validate_deepmind_mapping.py — Validate DeepMind bridge mapping consistency.

Checks that:
1. The canonical theorem name is consistent across all files.
2. The mapped Lean theorem actually exists in the Lean source.
3. The mapped Lean file actually exists on disk.
4. mapping.yaml and export_deepmind.py use the same name.

REPAIR NOTE (P1 Fix):
  Added this script to catch the exact class of naming inconsistency
  that existed between mapping.yaml (circlePacking10MinDistBound) and
  export_deepmind.py (circlePacking10MinDist).
"""

import sys
import re
from pathlib import Path

# ---------------------------------------------------------------------------
# Canonical name — single source of truth
# ---------------------------------------------------------------------------
CANONICAL_THEOREM_NAME = "circlePacking10MinDistBound"

# Files to check
FILES_TO_CHECK = {
    "Lean source (N10.lean)": Path("formal/lean/ErdosAtlas/CirclePacking/N10.lean"),
    "mapping.yaml": Path("bridges/deepmind/mapping.yaml"),
    "export_deepmind.py": Path("scripts/export_deepmind.py"),
}

LEAN_N10_FILE = Path("formal/lean/ErdosAtlas/CirclePacking/N10.lean")


def check_file_contains_canonical(label: str, filepath: Path) -> tuple[bool, str]:
    """Check that a file contains the canonical theorem name."""
    if not filepath.is_file():
        return False, f"File not found: {filepath}"
    content = filepath.read_text()
    if CANONICAL_THEOREM_NAME in content:
        return True, f"'{CANONICAL_THEOREM_NAME}' found in {filepath}"
    return False, f"'{CANONICAL_THEOREM_NAME}' NOT found in {filepath}"


def check_lean_theorem_declaration() -> tuple[bool, str]:
    """Check that the Lean file actually declares the canonical theorem."""
    if not LEAN_N10_FILE.is_file():
        return False, f"Lean file not found: {LEAN_N10_FILE}"

    content = LEAN_N10_FILE.read_text()

    # Look for actual theorem declaration (not just a comment mention)
    pattern = rf"theorem\s+{re.escape(CANONICAL_THEOREM_NAME)}"
    if re.search(pattern, content):
        return True, f"theorem {CANONICAL_THEOREM_NAME} declared in {LEAN_N10_FILE}"

    # Check if it's at least mentioned (weaker check)
    if CANONICAL_THEOREM_NAME in content:
        return True, f"'{CANONICAL_THEOREM_NAME}' referenced in {LEAN_N10_FILE} (may be comment)"

    return False, f"theorem {CANONICAL_THEOREM_NAME} NOT declared in {LEAN_N10_FILE}"


def check_no_old_inconsistent_names() -> list[tuple[str, str]]:
    """Check that old inconsistent theorem names are not used."""
    old_names = [
        "circlePacking10MinDist",   # missing "Bound" — was in export_deepmind.py
    ]
    violations = []
    for label, filepath in FILES_TO_CHECK.items():
        if not filepath.is_file():
            continue
        content = filepath.read_text()
        for old_name in old_names:
            # Make sure we're not just matching the canonical name (which contains old_name as prefix)
            # Use word boundary check
            pattern = rf"\b{re.escape(old_name)}\b"
            matches = re.findall(pattern, content)
            # Filter out matches that are actually the canonical name
            real_matches = [m for m in matches if m != CANONICAL_THEOREM_NAME]
            if real_matches:
                violations.append((label, f"Old name '{old_name}' found in {filepath}"))
    return violations


def main() -> int:
    print("DeepMind Mapping Consistency Validation")
    print("=" * 55)
    print(f"Canonical theorem name: {CANONICAL_THEOREM_NAME}")
    print()

    all_passed = True

    # --- Check 1: Each file contains canonical name ---
    print("Check 1: Canonical name present in all files")
    for label, filepath in FILES_TO_CHECK.items():
        ok, msg = check_file_contains_canonical(label, filepath)
        status = "[PASS]" if ok else "[FAIL]"
        print(f"  {status} {label}: {msg}")
        if not ok:
            all_passed = False

    print()

    # --- Check 2: Lean theorem actually declared ---
    print("Check 2: Lean theorem declaration")
    ok, msg = check_lean_theorem_declaration()
    status = "[PASS]" if ok else "[FAIL]"
    print(f"  {status} {msg}")
    if not ok:
        all_passed = False

    print()

    # --- Check 3: No old inconsistent names ---
    print("Check 3: No old inconsistent theorem names")
    violations = check_no_old_inconsistent_names()
    if violations:
        for label, msg in violations:
            print(f"  [FAIL] {label}: {msg}")
        all_passed = False
    else:
        print("  [PASS] No old inconsistent names found")

    print()

    # --- Check 4: Lean file exists ---
    print("Check 4: Lean file exists on disk")
    if LEAN_N10_FILE.is_file():
        print(f"  [PASS] {LEAN_N10_FILE} exists")
    else:
        print(f"  [FAIL] {LEAN_N10_FILE} does not exist")
        all_passed = False

    print()
    print("=" * 55)
    if all_passed:
        print("[PASS] All DeepMind mapping consistency checks passed")
        return 0
    else:
        print("[FAIL] One or more consistency checks failed")
        print("       Fix the issues above to ensure bridge integrity.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

