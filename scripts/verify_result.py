#!/usr/bin/env python3
"""Independent verification of a saved result.

The verifier is INDEPENDENT from the optimizer.
It loads saved coordinates and validates them from scratch.

Clearly distinguishes:
  "feasible packing verified" != "globally optimal packing proved"
"""
import sys
import json
import argparse
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from atlas.geometry.circle_packing import PackingConfiguration, evaluate_configuration


def verify_coordinates(coords: np.ndarray, contact_tol: float = 1e-4) -> dict:
    """
    Independently verify a set of coordinates.
    Returns a dict with all check results and a top-level 'passed' flag.
    """
    n = len(coords)
    violations = []
    checks = {}

    # 1. Shape check
    if coords.ndim != 2 or coords.shape[1] != 2:
        violations.append(f"wrong shape: {coords.shape}, expected (n, 2)")
        checks["shape"] = False
    else:
        checks["shape"] = True

    # 2. Finite values check (NaN / inf)
    if not np.all(np.isfinite(coords)):
        nan_count = np.sum(np.isnan(coords))
        inf_count = np.sum(np.isinf(coords))
        violations.append(f"non-finite values: {nan_count} NaN, {inf_count} inf")
        checks["finite"] = False
    else:
        checks["finite"] = True

    # 3. Boundary constraints: all coordinates in [0, 1]
    if checks.get("finite", False) and checks.get("shape", False):
        out_of_bounds = np.sum((coords < 0) | (coords > 1))
        if out_of_bounds > 0:
            violations.append(
                f"boundary violation: {out_of_bounds} coordinates outside [0,1]"
            )
            checks["boundary"] = False
        else:
            checks["boundary"] = True
    else:
        checks["boundary"] = False

    # 4. Duplicate coordinates check
    if checks.get("shape", False) and checks.get("finite", False):
        from scipy.spatial.distance import pdist
        dists = pdist(coords)
        n_duplicates = int(np.sum(dists < 1e-10))
        if n_duplicates > 0:
            violations.append(f"duplicate coordinates: {n_duplicates} pairs within 1e-10")
            checks["no_duplicates"] = False
        else:
            checks["no_duplicates"] = True
    else:
        checks["no_duplicates"] = False

    # 5. Minimum pairwise distance (independently computed)
    min_dist = None
    if checks.get("shape", False) and checks.get("finite", False):
        from scipy.spatial.distance import pdist
        dists = pdist(coords)
        min_dist = float(dists.min()) if len(dists) > 0 else 0.0
        checks["min_distance"] = min_dist

    # 6. Contact graph
    contact_pairs = []
    if min_dist is not None:
        from scipy.spatial.distance import pdist, squareform
        dist_matrix = squareform(pdist(coords))
        for i in range(n):
            for j in range(i + 1, n):
                if dist_matrix[i, j] <= min_dist + contact_tol:
                    contact_pairs.append([i, j])

    passed = len(violations) == 0

    return {
        "passed": passed,
        # Clearly distinguish feasibility from global optimality
        "feasible_packing_verified": passed,
        "globally_optimal_proved": False,  # Never claim this without a formal certificate
        "n_points": n,
        "min_distance": min_dist,
        "checks": checks,
        "constraint_violations": violations,
        "contact_graph": {"contacts": contact_pairs, "n_contacts": len(contact_pairs)},
        "boundary_feasible": checks.get("boundary", False),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Independent verification of a saved packing result."
    )
    parser.add_argument("result_dir", help="Directory containing search_result.json")
    parser.add_argument("--contact-tol", type=float, default=1e-4)
    args = parser.parse_args()

    result_dir = Path(args.result_dir)
    search_file = result_dir / "search_result.json"

    if not search_file.exists():
        print(f"ERROR: {search_file} not found", file=sys.stderr)
        return 1

    try:
        data = json.loads(search_file.read_text())
    except json.JSONDecodeError as e:
        print(f"ERROR: invalid JSON in {search_file}: {e}", file=sys.stderr)
        return 1

    if "coordinates" not in data:
        print("ERROR: search_result.json missing 'coordinates' field", file=sys.stderr)
        return 1

    raw_coords = data["coordinates"]
    if not raw_coords:
        print("ERROR: coordinates list is empty", file=sys.stderr)
        return 1

    try:
        coords = np.array(raw_coords, dtype=float)
    except (ValueError, TypeError) as e:
        print(f"ERROR: cannot convert coordinates to numpy array: {e}", file=sys.stderr)
        return 1

    result = verify_coordinates(coords, contact_tol=args.contact_tol)

    print(f"[verify] Passed: {result['passed']}")
    print(f"[verify] Feasible packing verified: {result['feasible_packing_verified']}")
    print(f"[verify] Globally optimal proved: {result['globally_optimal_proved']}")
    print(f"[verify] Min distance: {result['min_distance']}")
    print(f"[verify] N contacts: {result['contact_graph']['n_contacts']}")

    if result["constraint_violations"]:
        print("[verify] VIOLATIONS:")
        for v in result["constraint_violations"]:
            print(f"  - {v}")

    output_file = result_dir / "verification_result.json"
    output_file.write_text(json.dumps(result, indent=2))
    print(f"[verify] Written: {output_file}")

    # Return nonzero if verification failed
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
