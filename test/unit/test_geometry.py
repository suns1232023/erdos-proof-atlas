"""Unit tests for circle packing geometry."""
import pytest, numpy as np, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from atlas.geometry.circle_packing import (PackingConfiguration, compute_min_distance,
    check_boundary_constraints, build_contact_graph, evaluate_configuration)

def test_min_distance_two_points():
    assert abs(compute_min_distance(np.array([[0.,0.],[1.,0.]])) - 1.0) < 1e-12

def test_boundary_valid():
    ok, v = check_boundary_constraints(np.array([[0.1,0.1],[0.9,0.9]]))
    assert ok and len(v) == 0

def test_boundary_violation():
    ok, v = check_boundary_constraints(np.array([[1.5,0.5],[0.5,0.5]]))
    assert not ok and len(v) > 0

def test_contact_graph_reports_tolerance():
    coords = np.array([[0.,0.],[0.5,0.]])
    cg = build_contact_graph(coords, 0.5, contact_tol=1e-4)
    assert "tolerance" in cg.to_dict()
    assert cg.tolerance == 1e-4

def test_evaluate_valid():
    config = PackingConfiguration(2, np.array([[0.1,0.1],[0.9,0.9]]))
    vr = evaluate_configuration(config)
    assert vr.passed

def test_evaluate_overlapping_rejected():
    config = PackingConfiguration(3, np.array([[0.1,0.1],[0.1,0.1],[0.9,0.9]]))
    assert not evaluate_configuration(config).passed

def test_evaluate_boundary_rejected():
    config = PackingConfiguration(2, np.array([[1.5,0.5],[0.5,0.5]]))
    assert not evaluate_configuration(config).passed

def test_shape_check():
    with pytest.raises(ValueError):
        PackingConfiguration(3, np.array([[0.1,0.1],[0.9,0.9]]))
