"""Formal tests — check Lean availability and build."""
import pytest, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from atlas.formalization.lean_interface import check_lean_available, run_lean_build

def test_lean_check_runs():
    """Lean check should run without crashing (even if Lean not installed)."""
    available = check_lean_available()
    assert isinstance(available, bool)

@pytest.mark.skipif(not check_lean_available(), reason="Lean not installed")
def test_lean_build():
    result = run_lean_build(Path("formal/lean"))
    assert isinstance(result.success, bool)
    assert result.formal_level() in ("L0","L1","L2","L3","L4","L5")
