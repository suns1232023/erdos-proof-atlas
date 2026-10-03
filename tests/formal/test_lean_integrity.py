
"""
Formal verification tests: check Lean project structure and integrity.
These tests verify file existence, naming consistency, and sorry-free status.
"""
import os
import subprocess
import shutil
import pytest

# ---------------------------------------------------------------------------
# Paths (relative to repository root)
# ---------------------------------------------------------------------------
LEAN_DIR = "formal/lean"
LAKEFILE = os.path.join(LEAN_DIR, "lakefile.toml")
LEAN_TOOLCHAIN = os.path.join(LEAN_DIR, "lean-toolchain")
LAKE_MANIFEST = os.path.join(LEAN_DIR, "lake-manifest.json")
MAIN_LEAN = os.path.join(LEAN_DIR, "Main.lean")
ERDOS_ATLAS_LEAN = os.path.join(LEAN_DIR, "ErdosAtlas", "Basic.lean")
N10_LEAN = os.path.join(LEAN_DIR, "ErdosAtlas", "CirclePacking", "N10.lean")
GEOMETRY_LEAN = os.path.join(LEAN_DIR, "ErdosAtlas", "Geometry", "Basic.lean")

CANONICAL_THEOREM_NAME = "circlePacking10MinDistBound"


class TestLeanProjectStructure:
    """Verify that all required Lean project files exist."""

    def test_lean_dir_exists(self):
        assert os.path.isdir(LEAN_DIR), f"Lean directory missing: {LEAN_DIR}"

    def test_lakefile_exists(self):
        assert os.path.isfile(LAKEFILE), f"lakefile.toml missing: {LAKEFILE}"

    def test_lean_toolchain_exists(self):
        assert os.path.isfile(LEAN_TOOLCHAIN), (
            f"lean-toolchain missing: {LEAN_TOOLCHAIN}"
        )

    def test_lake_manifest_exists(self):
        assert os.path.isfile(LAKE_MANIFEST), (
            f"lake-manifest.json missing: {LAKE_MANIFEST}\n"
            "Run 'lake update' in formal/lean/ to generate it."
        )

    def test_main_lean_exists(self):
        assert os.path.isfile(MAIN_LEAN), (
            f"Main.lean missing: {MAIN_LEAN}\n"
            "lakefile.toml declares [[lean_exe]] name='Main' but Main.lean does not exist."
        )

    def test_erdos_atlas_basic_exists(self):
        assert os.path.isfile(ERDOS_ATLAS_LEAN), (
            f"ErdosAtlas/Basic.lean missing: {ERDOS_ATLAS_LEAN}"
        )

    def test_n10_lean_exists(self):
        assert os.path.isfile(N10_LEAN), (
            f"ErdosAtlas/CirclePacking/N10.lean missing: {N10_LEAN}"
        )

    def test_geometry_lean_exists(self):
        assert os.path.isfile(GEOMETRY_LEAN), (
            f"ErdosAtlas/Geometry/Basic.lean missing: {GEOMETRY_LEAN}"
        )


class TestLakefileContent:
    """Verify lakefile.toml has required content."""

    def _read_lakefile(self):
        if not os.path.isfile(LAKEFILE):
            pytest.skip("lakefile.toml not found")
        with open(LAKEFILE) as f:
            return f.read()

    def test_lakefile_has_mathlib_require(self):
        content = self._read_lakefile()
        assert "mathlib" in content, (
            "lakefile.toml missing mathlib dependency.\n"
            "Add: [[require]]\nname = \"mathlib\"\ngit = \"...\"\nrev = \"...\""
        )

    def test_lakefile_has_require_block(self):
        content = self._read_lakefile()
        assert "[[require]]" in content or "[require]" in content, (
            "lakefile.toml has no [[require]] block"
        )

    def test_lakefile_has_lean_lib(self):
        content = self._read_lakefile()
        assert "[[lean_lib]]" in content or "[lean_lib]" in content

    def test_lakefile_has_erdos_atlas_lib(self):
        content = self._read_lakefile()
        assert "ErdosAtlas" in content

    def test_lakefile_no_bare_true_suppression(self):
        """lakefile.toml must not suppress errors with || true patterns."""
        content = self._read_lakefile()
        assert "|| true" not in content


class TestLeanTheoremNaming:
    """Verify canonical theorem name consistency across all files."""

    def _file_contains(self, filepath, text):
        if not os.path.isfile(filepath):
            return False
        with open(filepath) as f:
            return text in f.read()

    def test_n10_lean_has_canonical_theorem(self):
        if not os.path.isfile(N10_LEAN):
            pytest.skip("N10.lean not found")
        assert self._file_contains(N10_LEAN, CANONICAL_THEOREM_NAME), (
            f"N10.lean does not contain canonical theorem name: {CANONICAL_THEOREM_NAME}"
        )

    def test_n10_lean_no_trivial_True_conclusion(self):
        """The N10 theorem must not have '→ True' as its conclusion."""
        if not os.path.isfile(N10_LEAN):
            pytest.skip("N10.lean not found")
        with open(N10_LEAN) as f:
            content = f.read()
        assert "→ True" not in content and "-> True" not in content, (
            "N10.lean contains '→ True' — this is a placeholder, not a real theorem"
        )

    def test_n10_lean_no_float_type(self):
        """The N10 theorem must not use Float for the core mathematical statement."""
        if not os.path.isfile(N10_LEAN):
            pytest.skip("N10.lean not found")
        with open(N10_LEAN) as f:
            content = f.read()
        # Float should not appear in theorem statements (only in comments is OK)
        theorem_lines = [
            line for line in content.split("\n")
            if "theorem" in line or "def " in line
        ]
        for line in theorem_lines:
            assert "Float" not in line, (
                f"Float found in theorem/def line: {line}\n"
                "Use ℝ (Real) instead of Float for formal mathematics."
            )


class TestSorryPolicy:
    """Verify no-sorry policy for L5-claimed theorems."""

    def _find_sorry_in_lean_files(self, directory):
        """Find all .lean files containing 'sorry' (not in comments)."""
        sorry_files = []
        if not os.path.isdir(directory):
            return sorry_files
        for root, _, files in os.walk(directory):
            for fname in files:
                if not fname.endswith(".lean"):
                    continue
                fpath = os.path.join(root, fname)
                with open(fpath) as f:
                    lines = f.readlines()
                for lineno, line in enumerate(lines, 1):
                    # Skip pure comment lines
                    stripped = line.strip()
                    if stripped.startswith("--"):
                        continue
                    if "sorry" in line:
                        sorry_files.append((fpath, lineno, line.rstrip()))
        return sorry_files

    def test_no_sorry_in_lean_files(self):
        """
        No .lean file should contain 'sorry' outside of comments.
        If sorry is present, the formal level must be < L5.
        """
        if not os.path.isdir(LEAN_DIR):
            pytest.skip("Lean directory not found")
        sorry_occurrences = self._find_sorry_in_lean_files(LEAN_DIR)
        if sorry_occurrences:
            details = "\n".join(
                f"  {f}:{ln}: {line}"
                for f, ln, line in sorry_occurrences
            )
            pytest.fail(
                f"Found 'sorry' in {len(sorry_occurrences)} location(s).\n"
                f"A theorem with sorry cannot be at L5 (KERNEL_CHECKED).\n"
                f"Either remove sorry or downgrade formal level to L1-L4.\n"
                f"Locations:\n{details}"
            )


class TestLeanAvailability:
    """
    Verify Lean/lake availability.
    make lean MUST fail if Lean is not installed.
    """

    def test_lean_available_or_skip(self):
        """
        If Lean is not available, this test is skipped (for local dev).
        In CI, Lean must be available — CI should fail if not.
        """
        if shutil.which("lake") is None:
            pytest.skip(
                "lake not installed. "
                "In CI, this must be a FAILURE. "
                "For local dev, install Lean 4 + mathlib."
            )

    def test_lake_build_succeeds(self):
        """lake build must succeed in formal/lean/."""
        if shutil.which("lake") is None:
            pytest.skip("lake not installed")
        if not os.path.isdir(LEAN_DIR):
            pytest.skip("Lean directory not found")

        result = subprocess.run(
            ["lake", "build"],
            cwd=LEAN_DIR,
            capture_output=True,
            text=True,
            timeout=300,
        )
        assert result.returncode == 0, (
            f"lake build FAILED.\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

