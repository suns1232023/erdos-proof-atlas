"""Independent verifier. Separate code paths from optimizer."""

from __future__ import annotations
import json, numpy as np
from pathlib import Path
from atlas.geometry.circle_packing import PackingConfiguration, evaluate_configuration, VerificationResult


def verify_from_file(result_path: Path, contact_tol: float = 1e-4) -> VerificationResult:
    with open(result_path) as f:
        data = json.load(f)
    coords = np.array(data["coordinates"])
    config = PackingConfiguration(n_points=len(coords), coordinates=coords)
    return evaluate_configuration(config, contact_tol=contact_tol)


def verify_adversarial_cases() -> dict[str, bool]:
    """All adversarial cases must be REJECTED."""
    results = {}
    # Overlapping
    cfg = PackingConfiguration(3, np.array([[0.1,0.1],[0.1,0.1],[0.9,0.9]]))
    results["overlapping_circles"] = not evaluate_configuration(cfg).passed
    # Boundary violation
    cfg = PackingConfiguration(2, np.array([[1.5,0.5],[0.5,0.5]]))
    results["boundary_violation"] = not evaluate_configuration(cfg).passed
    # Duplicate coordinates
    cfg = PackingConfiguration(3, np.array([[0.3,0.3],[0.3,0.3],[0.7,0.7]]))
    results["duplicate_coordinates"] = not evaluate_configuration(cfg).passed
    return results
