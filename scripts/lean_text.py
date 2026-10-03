
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
    Remove Lean comments: line comments (-- ...), block comments (/- ... -/) and
    doc comments (/-- ... -/).  Lean block comments NEST, so a small state machine
    is used instead of a regex.  Newlines are preserved so line numbers stay valid.
    """
    out: list[str] = []
    i, n, depth = 0, len(text), 0
    while i < n:
        two = text[i:i + 2]
        if depth == 0 and two == "--":
            while i < n and text[i] != "\n":      # skip to end of line
                i += 1
            continue
        if two == "/-":
            depth += 1
            i += 2
            continue
        if depth > 0 and two == "-/":
            depth -= 1
            i += 2
            continue
        ch = text[i]
        if depth == 0 or ch == "\n":
            out.append(ch)
        i += 1
    return "".join(out)


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
    Find real `sorry` tokens in .lean files (comments and docstrings excluded).
    Returns list of (filepath, line_number, line_content).
    """
    import re
    occurrences = []
    if not directory.is_dir():
        return occurrences
    for lean_file in directory.rglob("*.lean"):
        if ".lake" in lean_file.parts:
            continue
        raw = lean_file.read_text(encoding="utf-8", errors="replace").splitlines()
        stripped = strip_lean_comments(lean_file.read_text(encoding="utf-8", errors="replace")).splitlines()
        for lineno, line in enumerate(stripped, 1):
            if re.search(r"\bsorry\b", line):
                occurrences.append((str(lean_file), lineno, raw[lineno - 1].rstrip()))
    return occurrences
