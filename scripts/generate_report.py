#!/usr/bin/env python3
"""Generate research report."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from atlas.reporting.generator import generate_atlas_report

def main() -> int:
    result_dir = Path("results/latest")
    def load(name):
        p = result_dir / name
        return json.loads(p.read_text()) if p.exists() else None
    search = load("search_result.json")
    verify = load("verification_result.json")
    prov = load("provenance.json")
    cert_dir = Path("certificates/circle_packing_n10")
    poly_cert = json.loads((cert_dir/"polynomial_certificate.json").read_text()) if (cert_dir/"polynomial_certificate.json").exists() else None
    problem_id = search.get("problem_id","unknown") if search else "unknown"
    out = Path("results/latest/report.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    generate_atlas_report(problem_id, search, verify, poly_cert, None, None, prov, out)
    print(f"[report] Saved to {out}")
    return 0

if __name__ == "__main__": sys.exit(main())
