#!/usr/bin/env python3
"""Run numerical search pipeline."""
import sys, json, argparse, numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from atlas.search.multistart import run_multistart_search
from atlas.geometry.circle_packing import PackingConfiguration, evaluate_configuration
from atlas.provenance.tracker import ProvenanceRecord

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("problem_id")
    parser.add_argument("--n", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--restarts", type=int, default=50)
    parser.add_argument("--output-dir", default="results/latest")
    args = parser.parse_args()
    out = Path(args.output_dir); out.mkdir(parents=True, exist_ok=True)
    prov = ProvenanceRecord.create(args.problem_id, args.seed)
    print(f"[run] Run ID: {prov.run_id}, N={args.n}, seed={args.seed}")
    result = run_multistart_search(args.problem_id, args.n, n_restarts=args.restarts, seed=args.seed)
    print(f"[run] [NUMERICAL] Objective: {result.objective:.10f}")
    coords = np.array(result.coordinates)
    config = PackingConfiguration(n_points=args.n, coordinates=coords)
    vr = evaluate_configuration(config)
    print(f"[run] [E3] Verification passed: {vr.passed}, min_d: {vr.min_distance:.10f}")
    (out/"search_result.json").write_text(json.dumps(result.to_dict(), indent=2))
    (out/"verification_result.json").write_text(json.dumps(vr.to_dict(), indent=2))
    prov.save(out/"provenance.json")
    print(f"[run] Saved to {out}/")
    return 0 if vr.passed else 1

if __name__ == "__main__": sys.exit(main())
