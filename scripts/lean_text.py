
"""
lean_text.py — Utilities for parsing Lean source files.

Strips both single-line (--) and block (/- ... -/, /-- ... -/) comments
before pattern matching, avoiding false positives from documentation.

REPAIR V9: Added /- ... -/ block comment stripping (was missing).
Lean doc comments /-- ... -/ are also block comments and must be stripped.
"""
from __future__ import annotations
import re
from pathlib import Path


def strip_lean_comments(text: str) -> str:
    """
    Remove all Lean comments from source text:
      -- single line comment (to end of line)
      /- block comment -/  (may span multiple lines, may be nested)
      /-- doc comment -/   (doc strings, also block comments)

    Returns only the non-comment code portions, preserving line structure.
    """
    result = []
    i = 0
    n = len(text)
    depth = 0  # nesting depth for block comments

    while i < n:
        if depth == 0:
            # Check for block comment start /- (includes /-- doc comments)
            if text[i:i+2] == '/-':
                depth += 1
                i += 2
                result.append(' ')  # preserve spacing
            # Check for single-line comment --
            elif text[i:i+2] == '--':
                # Skip to end of line, preserve the newline
                while i < n and text[i] != '\n':
                    i += 1
            else:
                result.append(text[i])
                i += 1
        else:
            # Inside block comment: look for -/ (close) or /- (nested open)
            if text[i:i+2] == '-/':
                depth -= 1
                i += 2
            elif text[i:i+2] == '/-':
                depth += 1
                i += 2
            else:
                # Preserve newlines to keep line numbers meaningful
                if text[i] == '\n':
                    result.append('\n')
                i += 1

    return ''.join(result)


def lean_file_contains(filepath: Path, pattern: str, strip_comments: bool = True) -> bool:
    """Check if a Lean file contains a pattern, optionally stripping comments."""
    if not filepath.is_file():
        return False
    content = filepath.read_text(encoding="utf-8", errors="replace")
    if strip_comments:
        content = strip_lean_comments(content)
    return pattern in content


def lean_file_has_theorem(filepath: Path, theorem_name: str) -> bool:
    """Check if a Lean file declares a theorem with the given name (strips all comments)."""
    if not filepath.is_file():
        return False
    content = strip_lean_comments(
        filepath.read_text(encoding="utf-8", errors="replace")
    )
    pattern = rf"theorem\s+{re.escape(theorem_name)}"
    return bool(re.search(pattern, content))


def lean_file_has_conflicting_point_def(filepath: Path) -> bool:
    """
    Check if a Lean file has the conflicting function-type Point definition
    in actual code (after stripping all comments including doc comments).
    """
    if not filepath.is_file():
        return False
    content = strip_lean_comments(
        filepath.read_text(encoding="utf-8", errors="replace")
    )
    return "def Point : Type := Fin 2" in content


def lean_file_has_trivial_true(filepath: Path) -> bool:
    """
    Check if a Lean file has a trivial '→ True' conclusion in actual code.
    Strips both -- single-line and /- -/ block comments (including /-- doc -/).
    """
    if not filepath.is_file():
        return False
    content = strip_lean_comments(
        filepath.read_text(encoding="utf-8", errors="replace")
    )
    return "→ True" in content or "-> True" in content


def lean_file_has_float_in_theorem(filepath: Path) -> list[str]:
    """
    Find theorem/def lines containing 'Float' (after stripping all comments).
    Returns list of offending lines.
    """
    if not filepath.is_file():
        return []
    content = strip_lean_comments(
        filepath.read_text(encoding="utf-8", errors="replace")
    )
    violations = []
    for line in content.splitlines():
        stripped = line.strip()
        if (stripped.startswith("theorem") or stripped.startswith("def ")) \
                and "Float" in line:
            violations.append(line.rstrip())
    return violations


def lean_files_with_trivial_true(directory: Path) -> list[str]:
    """
    Find all .lean files in directory that have '→ True' in actual code.
    Strips all comments before checking.
    """
    violations = []
    if not directory.is_dir():
        return violations
    for lean_file in directory.rglob("*.lean"):
        if lean_file_has_trivial_true(lean_file):
            violations.append(str(lean_file))
    return violations


def find_sorry_in_lean_files(directory: Path) -> list[tuple[str, int, str]]:
    """
    Find 'sorry' occurrences in .lean files, excluding all comment lines.
    Strips both -- and /- -/ block comments.
    Returns list of (filepath, line_number, original_line_content).
    """
    occurrences = []
    if not directory.is_dir():
        return occurrences

    for lean_file in directory.rglob("*.lean"):
        raw = lean_file.read_text(encoding="utf-8", errors="replace")
        stripped = strip_lean_comments(raw)

        raw_lines = raw.splitlines()
        stripped_lines = stripped.splitlines()

        # Pad to same length if block comment removal changed line count
        min_len = min(len(raw_lines), len(stripped_lines))
        for lineno in range(min_len):
            if "sorry" in stripped_lines[lineno]:
                occurrences.append((str(lean_file), lineno + 1, raw_lines[lineno].rstrip()))

    return occurrences
