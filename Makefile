.PHONY: install test search verify exact certify lean audit report deepmind-export manifest all clean

install:
	pip install -e ".[symbolic,dev]"

test:
	python -m pytest -q tests/

search:
	python scripts/run_problem.py circle-packing-square --n 10 --restarts 50

verify:
	python scripts/verify_result.py results/latest

exact:
	python scripts/build_certificate.py

certify: exact
	@echo "[certify] Certificate built."

lean:
	python scripts/lean_check.py

audit:
	python scripts/atlas_audit.py

report:
	python scripts/generate_report.py

deepmind-export:
	python scripts/export_deepmind.py

manifest:
	python scripts/build_manifest.py

all: search verify exact certify lean audit report deepmind-export manifest
	@echo "[all] Complete pipeline finished."

clean:
	rm -rf results/latest/*.json results/latest/*.md results/latest/SHA256SUMS
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
