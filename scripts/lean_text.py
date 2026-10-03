
"""
lean_text.py — Utilities for parsing Lean source files.

Provides comment-stripping and pattern matching that avoids
false positives from Lean comment lines (-- ...).

Used by: check_paths.py, atlas_audit.py, formal_audit.py,
         tests/formal/test_lean_integrity.py
"""
from __future__ import annotations
from pathlib import Path


def strip_lean_comments(text: str) -> str:
    """
    Remove Lean single-line comments (-- ...) from source text.
    Returns only the non-comment portions of each line.
    Does NOT handle block comments /- ... -/ (rare in our codebase).
    """
    lines = []
    for line in text.splitlines():
        # Find -- comment start (not inside a string, but good enough for our checks)
        idx = line.find("--")
        if idx >= 0:
            lines.append(line[:idx])
        else:
            lines.append(line)
    return "\n".join(lines)


def lean_file_contains(filepath: Path, pattern: str, strip_comments: bool = True) -> bool:
    """
    Check if a Lean file contains a pattern, optionally stripping comments first.
    """
    if not filepath.is_file():
        return False
    content = filepath.read_text(encoding="utf-8", errors="replace")
    if strip_comments:
        content = strip_lean_comments(content)
    return pattern in content


def lean_file_has_theorem(filepath: Path, theorem_name: str) -> bool:
    """
    Check if a Lean file declares a theorem with the given name.
    Strips comments before checking to avoid false positives.
    """
    if not filepath.is_file():
        return False
    content = strip_lean_comments(filepath.read_text(encoding="utf-8", errors="replace"))
    import re
    pattern = rf"theorem\s+{re.escape(theorem_name)}"
    return bool(re.search(pattern, content))


def lean_file_has_conflicting_point_def(filepath: Path) -> bool:
    """
    Check if a Lean file has the conflicting function-type Point definition:
      def Point : Type := Fin 2 → ℝ
    Strips comments to avoid matching historical notes.
    """
    if not filepath.is_file():
        return False
    content = strip_lean_comments(filepath.read_text(encoding="utf-8", errors="replace"))
    return "def Point : Type := Fin 2" in content


def lean_file_has_trivial_true(filepath: Path) -> bool:
    """
    Check if a Lean file has a trivial '→ True' conclusion.
    Strips comments to avoid matching documentation.
    """
    if not filepath.is_file():
        return False
    content = strip_lean_comments(filepath.read_text(encoding="utf-8", errors="replace"))
    return "→ True" in content or "-> True" in content


def lean_file_has_float_in_theorem(filepath: Path) -> list[str]:
    """
    Find theorem/def lines containing 'Float' (after stripping comments).
    Returns list of offending lines.
    """
    if not filepath.is_file():
        return []
    content = strip_lean_comments(filepath.read_text(encoding="utf-8", errors="replace"))
    violations = []
    for line in content.splitlines():
        stripped = line.strip()
        if (stripped.startswith("theorem") or stripped.startswith("def ")) \
                and "Float" in line:
            violations.append(line.rstrip())
    return violations


def find_sorry_in_lean_files(directory: Path) -> list[tuple[str, int, str]]:
    """
    Find 'sorry' occurrences in .lean files, excluding comment lines.
    Returns list of (filepath, line_number, line_content).
    """
    occurrences = []
    if not directory.is_dir():
        return occurrences
    for lean_file in directory.rglob("*.lean"):
        lines = lean_file.read_text(encoding="utf-8", errors="replace").splitlines()
        for lineno, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith("--"):
                continue  # skip comment lines
            if "sorry" in line:
                occurrences.append((str(lean_file), lineno, line.rstrip()))
    return occurrences
