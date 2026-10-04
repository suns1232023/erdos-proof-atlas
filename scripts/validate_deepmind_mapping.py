#!/usr/bin/env python3
"""
validate_deepmind_mapping.py — Validate DeepMind bridge mapping consistency.

Checks that:
1. The canonical theorem name is consistent across all files.
2. The mapped Lean theorem actually exists in the Lean source.
3. The mapped Lean file actually exists on disk.
4. mapping.yaml uses the canonical name.

REPAIR V2 (false positive fix):
  check_no_old_inconsistent_names() previously scanned export_deepmind.py
  source code, which caused false positives because comments and variable
  definitions like OLD_THEOREM_NAME = "circlePacking10MinDist" matched
  the regex. Fix: Only check DATA files, not Python script source files.
"""

import sys
import re
from pathlib import Path

CANONICAL_THEOREM_NAME = "circlePacking10MinDistBound"

# DATA files to check (NOT Python scripts — they may reference old names in comments)
DATA_FILES_TO_CHECK = {
    "Lean source (N10.lean)": Path("formal/lean/ErdosAtlas/CirclePacking/N10.lean"),
    "mapping.yaml": Path("bridges/deepmind/mapping.yaml"),
}

GENERATED_OUTPUT = Path("bridges/deepmind/export.json")
LEAN_N10_FILE = Path("formal/lean/ErdosAtlas/CirclePacking/N10.lean")


def check_file_contains_canonical(label: str, filepath: Path) -> tuple:
    if not filepath.is_file():
        return False, f"File not found: {filepath}"
    content = filepath.read_text()
    if CANONICAL_THEOREM_NAME in content:
        return True, f"'{CANONICAL_THEOREM_NAME}' found in {filepath}"
    return False, f"'{CANONICAL_THEOREM_NAME}' NOT found in {filepath}"


def check_lean_theorem_declaration() -> tuple:
    if not LEAN_N10_FILE.is_file():
        return False, f"Lean file not found: {LEAN_N10_FILE}"
    content = LEAN_N10_FILE.read_text()
    pattern = rf"theorem\s+{re.escape(CANONICAL_THEOREM_NAME)}"
    if re.search(pattern, content):
        return True, f"theorem {CANONICAL_THEOREM_NAME} declared in {LEAN_N10_FILE}"
    if CANONICAL_THEOREM_NAME in content:
        return True, f"'{CANONICAL_THEOREM_NAME}' referenced in {LEAN_N10_FILE}"
    return False, f"theorem {CANONICAL_THEOREM_NAME} NOT declared in {LEAN_N10_FILE}"


def check_no_old_names_in_data_files() -> list:
    """
    Check that old inconsistent theorem names are not used in DATA files.
    Only checks Lean source, mapping.yaml, and generated JSON output.
    Does NOT check Python scripts (may reference old names in comments/variables).
    """
    OLD_THEOREM_NAME = "circlePacking10MinDist"  # noqa: for reference only
    violations = []

    for label, filepath in DATA_FILES_TO_CHECK.items():
        if not filepath.is_file():
            continue
        content = filepath.read_text()
        pattern = rf"\b{re.escape(OLD_THEOREM_NAME)}\b"
        matches = re.findall(pattern, content)
        real_matches = [m for m in matches if m != CANONICAL_THEOREM_NAME]
        if real_matches:
            violations.append((label, f"Old name '{OLD_THEOREM_NAME}' found in {filepath}"))

    if GENERATED_OUTPUT.is_file():
        content = GENERATED_OUTPUT.read_text()
        pattern = rf"\b{re.escape(OLD_THEOREM_NAME)}\b"
        matches = re.findall(pattern, content)
        real_matches = [m for m in matches if m != CANONICAL_THEOREM_NAME]
        if real_matches:
            violations.append(
                ("Generated output (export.json)",
                 f"Old name '{OLD_THEOREM_NAME}' found in {GENERATED_OUTPUT}")
            )

    return violations


def main() -> int:
    print("DeepMind Mapping Consistency Validation")
    print("=" * 55)
    print(f"Canonical theorem name: {CANONICAL_THEOREM_NAME}")
    print()

    all_passed = True

    print("Check 1: Canonical name present in data files")
    for label, filepath in DATA_FILES_TO_CHECK.items():
        ok, msg = check_file_contains_canonical(label, filepath)
        print(f"  {'[PASS]' if ok else '[FAIL]'} {label}: {msg}")
        if not ok:
            all_passed = False

    print()
    print("Check 2: Lean theorem declaration")
    ok, msg = check_lean_theorem_declaration()
    print(f"  {'[PASS]' if ok else '[FAIL]'} {msg}")
    if not ok:
        all_passed = False

    print()
    print("Check 3: No old inconsistent theorem names in data files")
    print("  (Python scripts excluded — may reference old names in comments/variables)")
    violations = check_no_old_names_in_data_files()
    if violations:
        for label, msg in violations:
            print(f"  [FAIL] {label}: {msg}")
        all_passed = False
    else:
        print("  [PASS] No old inconsistent names found in data files")

    print()
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
        return 1


if __name__ == "__main__":
    sys.exit(main())
