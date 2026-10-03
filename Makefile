
# Makefile for erdos-proof-atlas
#
# REPAIR V5:
#   - Fixed non-existent script references:
#     scripts/search.py    → scripts/run_problem.py
#     scripts/verify.py   → scripts/verify_result.py
#     scripts/exact.py    → scripts/build_certificate.py (exact symbolic cert)
#     scripts/generate_manifest.py → scripts/build_manifest.py
#   - All test targets use tests/ (canonical)
#   - make lean FAILS if Lean unavailable
#   - make all fails if any mandatory stage fails
#
# Usage:
#   make install        Install Python dependencies
#   make test           Run all pytest tests
#   make search         Run numerical search (N=10 packing)
#   make verify         Run independent verification
#   make exact          Run exact symbolic computation / certificate
#   make certify        Build algebraic certificate
#   make lean           Run Lean 4 formal verification (FAILS if Lean unavailable)
#   make status         Report formal level (does NOT fail if Lean unavailable)
#   make audit          Run atlas audit (repository + evidence)
#   make formal-audit   Run formal audit (Lean formalization)
#   make full-audit     Run complete audit (atlas + formal)
#   make report         Generate reproducibility report
#   make deepmind-export Export DeepMind metadata
#   make manifest       Generate reproducibility manifest
#   make check-paths    Run path consistency check
#   make all            Run complete pipeline (fails on any error)
#   make clean          Remove generated files

PYTHON := python3
PYTEST := python3 -m pytest
SCRIPTS := scripts

.PHONY: install test unit-test integration-test adversarial-test regression-test \
        search verify exact certify lean status audit formal-audit full-audit \
        report deepmind-export manifest check-paths all clean

# ---------------------------------------------------------------------------
# Installation
# ---------------------------------------------------------------------------
install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e ".[symbolic,dev]"
	@echo "[PASS] Dependencies installed"

# ---------------------------------------------------------------------------
# Tests (canonical: tests/ directory)
# ---------------------------------------------------------------------------
test:
	$(PYTEST) tests/ -q --tb=short
	@echo "[PASS] All tests passed"

unit-test:
	$(PYTEST) tests/unit/ -v --tb=short
	@echo "[PASS] Unit tests passed"

integration-test:
	$(PYTEST) tests/integration/ -v --tb=short
	@echo "[PASS] Integration tests passed"

adversarial-test:
	$(PYTEST) tests/adversarial/ -v --tb=short
	@echo "[PASS] Adversarial tests passed"

regression-test:
	$(PYTEST) tests/regression/ -v --tb=short
	@echo "[PASS] Regression tests passed"

formal-test:
	$(PYTEST) tests/formal/ -v --tb=short
	@echo "[PASS] Formal tests passed"

compile-check:
	$(PYTHON) -m compileall src scripts
	@echo "[PASS] Python compilation check passed"

# ---------------------------------------------------------------------------
# Computational pipeline
# REPAIR V5: Fixed script names to match actual files in repo
# ---------------------------------------------------------------------------
search:
	$(PYTHON) $(SCRIPTS)/run_problem.py circle-packing-square-n10
	@echo "[PASS] Numerical search complete"

verify:
	$(PYTHON) $(SCRIPTS)/verify_result.py results/latest
	@echo "[PASS] Verification complete"

exact:
	$(PYTHON) $(SCRIPTS)/build_certificate.py
	@echo "[PASS] Exact symbolic computation / certificate built"

certify:
	$(PYTHON) $(SCRIPTS)/build_certificate.py
	@echo "[PASS] Certificate built"

# ---------------------------------------------------------------------------
# Lean formal verification
# make lean FAILS if Lean is unavailable (no silent success)
# ---------------------------------------------------------------------------
lean:
	@echo "Running Lean 4 formal verification (strict mode)..."
	$(PYTHON) $(SCRIPTS)/lean_check.py
	@echo "[PASS] Lean formal verification passed"

# Status-only mode: reports formal level without failing when Lean unavailable
status:
	$(PYTHON) $(SCRIPTS)/lean_check.py --status

# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------
check-paths:
	$(PYTHON) $(SCRIPTS)/check_paths.py
	@echo "[PASS] Path consistency check passed"

audit:
	$(PYTHON) $(SCRIPTS)/atlas_audit.py
	@echo "[PASS] Atlas audit passed"

formal-audit:
	$(PYTHON) $(SCRIPTS)/formal_audit.py
	@echo "[PASS] Formal audit passed"

full-audit:
	$(PYTHON) $(SCRIPTS)/full_audit.py
	@echo "[PASS] Full audit passed"

# ---------------------------------------------------------------------------
# Reporting and export
# REPAIR V5: Fixed generate_manifest.py → build_manifest.py
# ---------------------------------------------------------------------------
report:
	$(PYTHON) $(SCRIPTS)/generate_report.py
	@echo "[PASS] Report generated"

deepmind-export:
	$(PYTHON) $(SCRIPTS)/export_deepmind.py
	$(PYTHON) $(SCRIPTS)/validate_deepmind_mapping.py
	@echo "[PASS] DeepMind export and validation complete"

manifest:
	$(PYTHON) $(SCRIPTS)/build_manifest.py
	@echo "[PASS] Reproducibility manifest generated"

# ---------------------------------------------------------------------------
# Complete pipeline
# make all fails if ANY mandatory stage fails
# ---------------------------------------------------------------------------
all: compile-check test check-paths certify lean audit deepmind-export manifest
	@echo ""
	@echo "============================================================"
	@echo "  BUILD COMPLETE — All mandatory checks passed"
	@echo "============================================================"

# ---------------------------------------------------------------------------
# Clean
# ---------------------------------------------------------------------------
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -f bridges/deepmind/export.json
	@echo "[PASS] Clean complete"
