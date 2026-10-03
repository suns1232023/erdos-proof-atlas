"""Multistart SLSQP search. Status is always NUMERICAL."""

from __future__ import annotations
import time, uuid, platform, sys
import numpy as np
from dataclasses import dataclass, field
from scipy.optimize import minimize
from scipy.spatial.distance import pdist, cdist


@dataclass
class SearchResult:
    problem_id: str
    run_id: str
    objective: float
    coordinates: list[list[float]]
    seed: int
    algorithm: str
    runtime_seconds: float
    software_versions: dict
    status: str = "NUMERICAL"
    # Failure tracking (per spec)
    successful_restarts: int = 0
    failed_restarts: int = 0
    failure_reasons: list = field(default_factory=list)
    feasible_found: bool = False

    def __post_init__(self) -> None:
        if self.status != "NUMERICAL":
            raise ValueError("SearchResult.status must be NUMERICAL. Never auto-upgrade.")

    def to_dict(self) -> dict:
        return {
            "problem_id": self.problem_id, "run_id": self.run_id,
            "objective": self.objective, "coordinates": self.coordinates,
            "seed": self.seed, "algorithm": self.algorithm,
            "runtime_seconds": self.runtime_seconds,
            "software_versions": self.software_versions,
            "status": self.status,
            "successful_restarts": self.successful_restarts,
            "failed_restarts": self.failed_restarts,
            "failure_reasons": self.failure_reasons,
            "feasible_found": self.feasible_found,
        }


def run_multistart_search(
    problem_id: str,
    n_points: int,
    n_restarts: int = 50,
    seed: int = 42,
    timeout_seconds: float = 300.0,
) -> SearchResult:
    rng = np.random.default_rng(seed)
    run_id = str(uuid.uuid4())[:8]
    t_start = time.time()
    best_obj, best_coords = -1.0, None
    bounds = [(0., 1.)] * (2 * n_points) + [(0., np.sqrt(2.))]
    ii, jj = np.triu_indices(n_points, 1)

    # Failure tracking
    successful_restarts = 0
    failed_restarts = 0
    failure_reasons: list[str] = []

    def constraints_fn(z: np.ndarray) -> np.ndarray:
        pts = z[:-1].reshape(n_points, 2)
        t = z[-1]
        v = pts[ii] - pts[jj]
        return np.sum(v * v, axis=1) - t * t

    def init() -> np.ndarray:
        corners = np.array([[0., 0.], [0., 1.], [1., 0.], [1., 1.]])
        pts = [corners[rng.integers(4)].copy()]
        while len(pts) < n_points:
            cands = np.vstack([rng.random((2000, 2)), corners])
            d = cdist(cands, np.array(pts)).min(axis=1)
            pts.append(cands[np.argmax(d)])
        return np.array(pts)

    for restart_idx in range(n_restarts):
        if time.time() - t_start > timeout_seconds:
            failure_reasons.append(f"timeout after {restart_idx} restarts")
            break

        p0 = init()
        t0 = float(pdist(p0).min()) * 0.98
        z0 = np.r_[p0.ravel(), t0]

        try:
            res = minimize(
                lambda z: -z[-1], z0, method="SLSQP", bounds=bounds,
                constraints={"type": "ineq", "fun": constraints_fn},
                options={"maxiter": 2000, "ftol": 1e-11, "disp": False},
            )

            # Explicit validation of optimizer result (per spec)
            pts = res.x[:-1].reshape(n_points, 2)

            # Check for NaN/inf
            if not np.all(np.isfinite(res.x)):
                failed_restarts += 1
                failure_reasons.append(f"restart {restart_idx}: non-finite coordinates")
                continue

            # Check optimizer status
            if not res.success and res.status not in (0, 9):
                # status 9 = iteration limit, may still be feasible
                failed_restarts += 1
                failure_reasons.append(
                    f"restart {restart_idx}: optimizer failed "
                    f"(status={res.status}, msg={res.message})"
                )
                continue

            # Check constraint feasibility
            constraint_residual = constraints_fn(res.x).min()
            if constraint_residual < -1e-7:
                failed_restarts += 1
                failure_reasons.append(
                    f"restart {restart_idx}: infeasible "
                    f"(constraint_residual={constraint_residual:.2e})"
                )
                continue

            # Check coordinate bounds
            if pts.min() < -1e-9 or pts.max() > 1 + 1e-9:
                failed_restarts += 1
                failure_reasons.append(f"restart {restart_idx}: coordinates out of bounds")
                continue

            # Independently compute objective (separate from optimizer)
            obj = float(pdist(pts).min())

            if obj > best_obj:
                best_obj = obj
                best_coords = pts.copy()

            successful_restarts += 1

        except Exception as exc:
            # Record failure reason, do NOT silently pass
            failed_restarts += 1
            failure_reasons.append(f"restart {restart_idx}: exception {type(exc).__name__}: {exc}")

    # If all restarts failed, raise immediately with diagnostic
    if best_coords is None:
        summary = "; ".join(failure_reasons[:5])
        raise RuntimeError(
            f"No feasible numerical result was produced after {n_restarts} restarts "
            f"for problem '{problem_id}'. "
            f"Failures: {summary}"
        )

    return SearchResult(
        problem_id=problem_id,
        run_id=run_id,
        objective=best_obj,
        coordinates=best_coords.tolist(),
        seed=seed,
        algorithm="multistart_slsqp_slack",
        runtime_seconds=time.time() - t_start,
        software_versions={"python": sys.version, "numpy": np.__version__},
        status="NUMERICAL",
        successful_restarts=successful_restarts,
        failed_restarts=failed_restarts,
        failure_reasons=failure_reasons,
        feasible_found=True,
    )
