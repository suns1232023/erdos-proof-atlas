"""Regression tests for known reference cases."""
import pytest, numpy as np, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from atlas.geometry.circle_packing import PackingConfiguration, evaluate_configuration

N10_COORDS = np.array([
    [0.18802934,0.00000000],[0.98852225,1.00000000],[0.00000000,1.00000000],
    [1.00000000,0.15759730],[0.28362135,0.68849497],[0.00000000,0.37698995],
    [0.60930889,0.00000000],[1.00000000,0.57887684],[0.56724271,1.00000000],
    [0.60930889,0.42127954],
])
N10_D = 0.42127954398390343
N10_TOL = 1e-5

@pytest.mark.parametrize("n,coords,expected_d,tol", [
    (2, np.array([[0.,0.],[1.,1.]]), float(np.sqrt(2)), 1e-6),
    (4, np.array([[0.,0.],[1.,0.],[0.,1.],[1.,1.]]), 1.0, 1e-6),
    (9, np.array([[i/2,j/2] for i in range(3) for j in range(3)]), 0.5, 1e-6),
])
def test_small_cases(n, coords, expected_d, tol):
    config = PackingConfiguration(n, coords)
    vr = evaluate_configuration(config)
    assert vr.passed
    assert abs(vr.min_distance - expected_d) < tol

def test_n10_historical_benchmark():
    """HISTORICAL BENCHMARK — not a new discovery. de Groot et al. (1990)."""
    config = PackingConfiguration(10, N10_COORDS)
    vr = evaluate_configuration(config)
    assert vr.passed
    assert abs(vr.min_distance - N10_D) < N10_TOL
    assert len(vr.contact_graph.contacts) == 12
