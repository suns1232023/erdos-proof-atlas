#!/usr/bin/env python3
"""Export DeepMind-compatible formalization metadata."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def main() -> int:
    out_dir = Path("bridges/deepmind/examples"); out_dir.mkdir(parents=True, exist_ok=True)
    metadata = {
        "problem_id": "erdos_circle_packing_n10",
        "source": {"type": "erdos_extremal_geometry", "identifier": "circle_packing_square_n10"},
        "category": "geometry",
        "ams": [52],
        "lean_theorem": "circlePacking10MinDist",
        "lean_file": "ErdosAtlas/CirclePacking/N10.lean",
        "formal_status": "STATEMENT_FORMALIZED",
        "computational_status": "SYMBOLICALLY_CERTIFIED",
        "certificate": "certificates/circle_packing_n10/polynomial_certificate.json",
        "provenance": {"repository": "suns1232023/erdos-proof-atlas"},
        "historical_note": "Polynomial first established by de Groot, Peikert & Würtz (1990).",
        "deepmind_compatible": True,
        "note": "This is a compatibility layer. Do NOT fork google-deepmind/formal-conjectures.",
    }
    (out_dir/"circle_packing_n10.json").write_text(json.dumps(metadata, indent=2))
    print(f"[deepmind] Exported to {out_dir}/circle_packing_n10.json")
    return 0

if __name__ == "__main__": sys.exit(main())
