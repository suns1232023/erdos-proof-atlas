#!/usr/bin/env python3
"""Independent verification of a saved result."""
import sys, json, argparse, numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from atlas.geometry.circle_packing import PackingConfiguration, evaluate_configuration

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("result_dir")
    parser.add_argument("--contact-tol", type=float, default=1e-4)
    args = parser.parse_args()
    p = Path(args.result_dir) / "search_result.json"
    if not p.exists():
        print(f"ERROR: {p} not found", file=sys.stderr); return 1
    data = json.loads(p.read_text())
    coords = np.array(data["coordinates"])
    config = PackingConfiguration(n_points=len(coords), coordinates=coords)
    vr = evaluate_configuration(config, contact_tol=args.contact_tol)
    print(f"[verify] Passed: {vr.passed}")
    print(f"[verify] Min distance: {vr.min_distance:.12f}")
    print(f"[verify] Violations: {vr.constraint_violations}")
    (Path(args.result_dir)/"verification_result.json").write_text(json.dumps(vr.to_dict(), indent=2))
    return 0 if vr.passed else 1

if __name__ == "__main__": sys.exit(main())
