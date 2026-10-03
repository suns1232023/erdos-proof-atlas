#!/usr/bin/env python3
"""Build SHA256 manifest."""
import sys, json, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from atlas.provenance.tracker import build_sha256sums

def main() -> int:
    result_dir = Path("results/latest")
    if not result_dir.exists():
        print("ERROR: results/latest not found", file=sys.stderr); return 1
    sums = build_sha256sums(result_dir)
    manifest = {"generated": time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()), "files": sums}
    (result_dir/"manifest.json").write_text(json.dumps(manifest, indent=2))
    (result_dir/"SHA256SUMS").write_text("\n".join(f"{v}  {k}" for k,v in sums.items()))
    print(f"[manifest] {len(sums)} files hashed")
    return 0

if __name__ == "__main__": sys.exit(main())
