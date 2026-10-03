
"""
Formal verification tests: check Lean project structure and integrity.

Uses lean_text.py utilities to strip Lean comments before pattern matching,
avoiding false positives from historical notes in comment lines.
"""
import os
import sys
import subprocess
import shutil
import pytest
from pathlib import Path

# Add scripts/ to path so we can import lean_text
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
try:
    from lean_text import (
        lean_file_contains,
        lean_file_has_theorem,
        lean_file_has_conflicting_point_def,
        lean_file_has_trivial_true,
        lean_file_has_float_in_theorem,
        find_sorry_in_lean_files,
    )
    LEAN_TEXT_AVAILABLE = True
except ImportError:
    LEAN_TEXT_AVAILABLE = False

LEAN_DIR = Path("formal/lean")
LAKEFILE = LEAN_DIR / "lakefile.toml"
LEAN_TOOLCHAIN = LEAN_DIR / "lean-toolchain"
LAKE_MANIFEST = LEAN_DIR / "lake-manifest.json"
ERDOS_ATLAS_LEAN = LEAN_DIR / "ErdosAtlas" / "Basic.lean"
N10_LEAN = LEAN_DIR / "ErdosAtlas" / "CirclePacking" / "N10.lean"
GEOMETRY_LEAN = LEAN_DIR / "ErdosAtlas" / "Geometry" / "Basic.lean"

CANONICAL_THEOREM_NAME = "circlePacking10MinDistBound"
CURRENT_FORMAL_LEVEL = "L1"


class TestLeanProjectStructure:

    def test_lean_dir_exists(self):
        assert LEAN_DIR.is_dir(), f"Lean directory missing: {LEAN_DIR}"

    def test_lakefile_exists(self):
        assert LAKEFILE.is_file(), f"lakefile.toml missing"

    def test_lean_toolchain_exists(self):
        assert LEAN_TOOLCHAIN.is_file(), f"lean-toolchain missing"

    def test_lake_manifest_exists(self):
        assert LAKE_MANIFEST.is_file(), (
            "lake-manifest.json missing. Run 'lake update' in formal/lean/"
        )

    def test_main_lean_exists(self):
        """Accept both Main.lean (correct) and main.lean (needs git mv)."""
        main_upper = (LEAN_DIR / "Main.lean").is_file()
        main_lower = (LEAN_DIR / "main.lean").is_file()
        if main_upper:
            pass
        elif main_lower:
            pytest.fail(
                "Found 'main.lean' (lowercase) but lakefile expects 'Main.lean'.\n"
                "Fix: git mv formal/lean/main.lean formal/lean/Main.lean"
            )
        else:
            pytest.fail("Neither Main.lean nor main.lean found")

    def test_erdos_atlas_basic_exists(self):
        assert ERDOS_ATLAS_LEAN.is_file()

    def test_n10_lean_exists(self):
        assert N10_LEAN.is_file()

    def test_geometry_lean_exists(self):
        assert GEOMETRY_LEAN.is_file()


class TestLakefileContent:

    def _read(self):
        if not LAKEFILE.is_file():
            pytest.skip("lakefile.toml not found")
        return LAKEFILE.read_text()

    def test_lakefile_has_mathlib_require(self):
        content = self._read()
        assert "mathlib" in content
        assert "[[require]]" in content

    def test_lakefile_uses_hash_comments(self):
        """TOML requires # comments, not -- comments."""
        content = self._read()
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("--"):
                pytest.fail(
                    f"lakefile.toml uses Lean-style '--' comment: {line}\n"
                    "TOML requires '#' comments. Fix: replace '--' with '#'."
                )

    def test_lakefile_has_lean_lib(self):
        content = self._read()
        assert "[[lean_lib]]" in content

    def test_lakefile_has_erdos_atlas(self):
        content = self._read()
        assert "ErdosAtlas" in content


class TestLeanTheoremNaming:

    def test_n10_lean_has_canonical_theorem(self):
        if not N10_LEAN.is_file():
            pytest.skip("N10.lean not found")
        if LEAN_TEXT_AVAILABLE:
            found = lean_file_has_theorem(N10_LEAN, CANONICAL_THEOREM_NAME)
        else:
            found = CANONICAL_THEOREM_NAME in N10_LEAN.read_text()
        assert found, f"N10.lean does not declare theorem {CANONICAL_THEOREM_NAME}"

    def test_n10_lean_no_trivial_True_conclusion(self):
        """N10 theorem must not have '→ True' conclusion (after stripping comments)."""
        if not N10_LEAN.is_file():
            pytest.skip("N10.lean not found")
        if LEAN_TEXT_AVAILABLE:
            has_trivial = lean_file_has_trivial_true(N10_LEAN)
        else:
            content = N10_LEAN.read_text()
            # Crude: skip comment lines manually
            non_comment = "\n".join(
                l for l in content.splitlines() if not l.strip().startswith("--")
            )
            has_trivial = "→ True" in non_comment or "-> True" in non_comment
        assert not has_trivial, "N10.lean has '→ True' placeholder conclusion"

    def test_n10_lean_no_float_type(self):
        """Theorem/def lines must not use Float (after stripping comments)."""
        if not N10_LEAN.is_file():
            pytest.skip("N10.lean not found")
        if LEAN_TEXT_AVAILABLE:
            violations = lean_file_has_float_in_theorem(N10_LEAN)
        else:
            violations = []
            for line in N10_LEAN.read_text().splitlines():
                stripped = line.strip()
                if stripped.startswith("--"):
                    continue
                if (stripped.startswith("theorem") or stripped.startswith("def ")) \
                        and "Float" in line:
                    violations.append(line)
        assert not violations, f"Float in theorem/def: {violations}"

    def test_geometry_basic_no_conflicting_point_def(self):
        """
        Geometry/Basic.lean must NOT define 'def Point : Type := Fin 2 → ℝ'.
        Uses comment-stripping to avoid matching historical notes.
        """
        if not GEOMETRY_LEAN.is_file():
            pytest.skip("Geometry/Basic.lean not found")
        if LEAN_TEXT_AVAILABLE:
            has_conflict = lean_file_has_conflicting_point_def(GEOMETRY_LEAN)
        else:
            content = "\n".join(
                l for l in GEOMETRY_LEAN.read_text().splitlines()
                if not l.strip().startswith("--")
            )
            has_conflict = "def Point : Type := Fin 2" in content
        assert not has_conflict, (
            "Geometry/Basic.lean has conflicting 'def Point := Fin 2 → ℝ'.\n"
            "This conflicts with Point.lean's 'structure Point where x y : ℝ'."
        )


class TestSorryPolicy:
    """Level-aware sorry policy. Sorry allowed at L1-L4, prohibited at L5."""

    def test_sorry_policy_level_aware(self):
        """At L1, sorry is allowed. Only at L5 does sorry cause failure."""
        if not LEAN_DIR.is_dir():
            pytest.skip("Lean directory not found")

        if LEAN_TEXT_AVAILABLE:
            occurrences = find_sorry_in_lean_files(LEAN_DIR)
        else:
            occurrences = []
            for lean_file in LEAN_DIR.rglob("*.lean"):
                for lineno, line in enumerate(lean_file.read_text().splitlines(), 1):
                    if not line.strip().startswith("--") and "sorry" in line:
                        occurrences.append((str(lean_file), lineno, line))

        count = len(occurrences)

        if CURRENT_FORMAL_LEVEL == "L5":
            if count > 0:
                details = "\n".join(f"  {f}:{ln}: {l}" for f, ln, l in occurrences)
                pytest.fail(f"L5 claimed but {count} sorry found:\n{details}")
        else:
            # L1-L4: sorry is allowed, just report
            if count > 0:
                print(f"\n[INFO] {count} sorry at {CURRENT_FORMAL_LEVEL} — allowed")

    def test_sorry_count_reasonable(self):
        """Even at L1, more than 5 sorry in proof bodies is suspicious."""
        if not LEAN_DIR.is_dir():
            pytest.skip("Lean directory not found")

        if LEAN_TEXT_AVAILABLE:
            occurrences = find_sorry_in_lean_files(LEAN_DIR)
        else:
            occurrences = []
            for lean_file in LEAN_DIR.rglob("*.lean"):
                for lineno, line in enumerate(lean_file.read_text().splitlines(), 1):
                    if not line.strip().startswith("--") and "sorry" in line:
                        occurrences.append((str(lean_file), lineno, line))

        # Filter: only count lines where sorry appears as a tactic (not in strings/names)
        real_sorry = [
            (f, ln, l) for f, ln, l in occurrences
            if "sorry" in l and "sorryPresent" not in l and "has_sorry" not in l
        ]
        assert len(real_sorry) <= 10, (
            f"Unusually high sorry count: {len(real_sorry)}. "
            "Check for accidental sorry in definitions."
        )


class TestLeanAvailability:

    def test_lean_available_or_skip(self):
        if shutil.which("lake") is None:
            pytest.skip("lake not installed — install Lean 4 to run this test")

    def test_lake_build_succeeds(self):
        if shutil.which("lake") is None:
            pytest.skip("lake not installed")
        if not LEAN_DIR.is_dir():
            pytest.skip("Lean directory not found")
        result = subprocess.run(
            ["lake", "build"],
            cwd=str(LEAN_DIR),
            capture_output=True,
            text=True,
            timeout=300,
        )
        assert result.returncode == 0, (
            f"lake build FAILED.\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
