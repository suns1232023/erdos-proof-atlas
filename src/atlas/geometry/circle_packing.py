"""
Circle packing geometry — independent of the optimizer.

Historical note: The degree-18 minimal polynomial for N=10 was first
established by de Groot, Peikert & Würtz (1990). This module provides
independent reproduction, NOT a new discovery.
"""

from __future__ import annotations
import numpy as np
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PackingConfiguration:
    n_points: int
    coordinates: np.ndarray
    container: str = "unit_square"

    def __post_init__(self) -> None:
        if self.coordinates.shape != (self.n_points, 2):
            raise ValueError(f"Expected shape ({self.n_points}, 2), got {self.coordinates.shape}")


@dataclass
class ContactGraph:
    contacts: list[tuple[int, int]]
    near_contacts: list[tuple[int, int]]
    tolerance: float
    min_distance: float

    def to_dict(self) -> dict:
        return {
            "contacts": self.contacts,
            "near_contacts": self.near_contacts,
            "tolerance": self.tolerance,
            "min_distance": self.min_distance,
            "n_contacts": len(self.contacts),
        }


@dataclass
class VerificationResult:
    passed: bool
    min_distance: float
    boundary_feasible: bool
    constraint_violations: list[str]
    contact_graph: ContactGraph
    objective_value: float
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "min_distance": self.min_distance,
            "boundary_feasible": self.boundary_feasible,
            "constraint_violations": self.constraint_violations,
            "contact_graph": self.contact_graph.to_dict(),
            "objective_value": self.objective_value,
            "notes": self.notes,
        }


def compute_min_distance(coords: np.ndarray) -> float:
    n = len(coords)
    if n < 2:
        return float("inf")
    min_d = float("inf")
    for i in range(n):
        for j in range(i + 1, n):
            d = float(np.linalg.norm(coords[i] - coords[j]))
            if d < min_d:
                min_d = d
    return min_d


def check_boundary_constraints(coords: np.ndarray, container: str = "unit_square", tol: float = 1e-9) -> tuple[bool, list[str]]:
    violations = []
    if container == "unit_square":
        for i, (x, y) in enumerate(coords):
            if x < -tol or x > 1.0 + tol:
                violations.append(f"Point {i}: x={x:.6f} outside [0,1]")
            if y < -tol or y > 1.0 + tol:
                violations.append(f"Point {i}: y={y:.6f} outside [0,1]")
    return len(violations) == 0, violations


def build_contact_graph(coords: np.ndarray, min_distance: float, contact_tol: float = 1e-4, near_tol: float = 1e-3) -> ContactGraph:
    n = len(coords)
    contacts, near_contacts = [], []
    for i in range(n):
        for j in range(i + 1, n):
            d = float(np.linalg.norm(coords[i] - coords[j]))
            if abs(d - min_distance) <= contact_tol:
                contacts.append((i, j))
            elif abs(d - min_distance) <= near_tol:
                near_contacts.append((i, j))
    return ContactGraph(contacts=contacts, near_contacts=near_contacts, tolerance=contact_tol, min_distance=min_distance)


def evaluate_configuration(config: PackingConfiguration, contact_tol: float = 1e-4) -> VerificationResult:
    """Independent verification — separate code paths from optimizer."""
    coords = config.coordinates
    violations: list[str] = []
    n = len(coords)
    for i in range(n):
        for j in range(i + 1, n):
            if np.allclose(coords[i], coords[j], atol=1e-10):
                violations.append(f"Duplicate coordinates: points {i} and {j}")
    min_d = compute_min_distance(coords)
    boundary_ok, bv = check_boundary_constraints(coords, config.container)
    violations.extend(bv)
    cg = build_contact_graph(coords, min_d, contact_tol)
    nc_ok, ncv = _check_noncontact(coords, min_d, cg.contacts)
    violations.extend(ncv)
    passed = len(violations) == 0 and boundary_ok and nc_ok
    return VerificationResult(passed=passed, min_distance=min_d, boundary_feasible=boundary_ok,
                              constraint_violations=violations, contact_graph=cg, objective_value=min_d)


def _check_noncontact(coords: np.ndarray, min_distance: float, contact_pairs: list[tuple[int, int]], tol: float = 1e-6) -> tuple[bool, list[str]]:
    n = len(coords)
    contact_set = set(contact_pairs)
    violations = []
    for i in range(n):
        for j in range(i + 1, n):
            if (i, j) not in contact_set:
                d = float(np.linalg.norm(coords[i] - coords[j]))
                if d < min_distance - tol:
                    violations.append(f"Non-contact pair ({i},{j}): d={d:.8f} < d_min={min_distance:.8f}")
    return len(violations) == 0, violations
