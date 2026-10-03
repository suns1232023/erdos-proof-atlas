# Makefile for erdos-proof-atlas
#
# Pipeline (per README):
#   SEARCH -> VERIFY -> CERTIFY -> FORMALIZE -> AUDIT -> REPORT
#
# Targets:
#   make install        Install Python dependencies
#   make compile-check  Check Python syntax
#   make test           Run all pytest tests
#   make check-paths    Run path consistency check
#   make search         Run numerical search (N=10 packing)
#   make verify         Run independent verification
#   make certify        Build algebraic certificate (E5)
#   make lean           Run Lean formal verification (requires Lean 4)
#   make status         Report formal level (does NOT fail without Lean)
#   make audit          Run atlas audit
#   make formal-audit   Run formal audit
#   make full-audit     Run complete audit
#   make deepmind-export Export DeepMind metadata
#   make manifest       Generate reproducibility manifest
#   make report         Generate research report
#   make all            Complete computational pipeline (no Lean required)
#   make all-formal     Complete pipeline including Lean verification
#   make clean          Remove generated files

PYTHON := python3
PYTEST := python3 -m pytest
SCRIPTS := scripts

.PHONY: install compile-check test unit-test integration-test adversarial-test \
        regression-test formal-test search verify certify lean status \
        check-paths audit formal-audit full-audit deepmind-export manifest \
        report all all-formal clean

# ---------------------------------------------------------------------------
# Installation
# ---------------------------------------------------------------------------
install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e ".[symbolic,dev]"
	@echo "[PASS] Dependencies installed"

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
compile-check:
	$(PYTHON) -m compileall src scripts
	@echo "[PASS] Python compilation check passed"

test:
	$(PYTEST) tests/ -q --tb=short
	@echo "[PASS] All tests passed"

unit-test:
	$(PYTEST) tests/unit/ -v --tb=short

integration-test:
	$(PYTEST) tests/integration/ -v --tb=short

adversarial-test:
	$(PYTEST) tests/adversarial/ -v --tb=short

regression-test:
	$(PYTEST) tests/regression/ -v --tb=short

formal-test:
	$(PYTEST) tests/formal/ -v --tb=short

# ---------------------------------------------------------------------------
# Computational pipeline: SEARCH -> VERIFY -> CERTIFY
# ---------------------------------------------------------------------------
search:
	$(PYTHON) $(SCRIPTS)/run_problem.py circle-packing-square-n10
	@echo "[PASS] Numerical search complete"

verify:
	$(PYTHON) $(SCRIPTS)/verify_result.py results/latest
	@echo "[PASS] Verification complete"

certify:
	$(PYTHON) $(SCRIPTS)/build_certificate.py
	@echo "[PASS] Certificate built"

# ---------------------------------------------------------------------------
# Lean formal verification
# make lean: FAILS if Lean unavailable (strict mode)
# make status: reports level without failing (status mode)
# ---------------------------------------------------------------------------
lean:
	@echo "Running Lean 4 formal verification (strict mode)..."
	$(PYTHON) $(SCRIPTS)/lean_check.py
	@echo "[PASS] Lean formal verification passed"

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
# ---------------------------------------------------------------------------
deepmind-export:
	$(PYTHON) $(SCRIPTS)/export_deepmind.py
	$(PYTHON) $(SCRIPTS)/validate_deepmind_mapping.py
	@echo "[PASS] DeepMind export and validation complete"

manifest:
	$(PYTHON) $(SCRIPTS)/build_manifest.py
	@echo "[PASS] Reproducibility manifest generated"

report:
	$(PYTHON) $(SCRIPTS)/generate_report.py
	@echo "[PASS] Report generated"

# ---------------------------------------------------------------------------
# Complete pipelines
#
# make all: computational/reproducibility pipeline (no Lean required)
#   README pipeline: SEARCH -> VERIFY -> CERTIFY -> AUDIT -> REPORT
#
# make all-formal: adds Lean verification gate
# ---------------------------------------------------------------------------
all: compile-check test check-paths search verify certify audit deepmind-export manifest report
	@echo ""
	@echo "============================================================"
	@echo "  BUILD COMPLETE (computational pipeline)"
	@echo "  Lean verification: run 'make lean' or 'make all-formal'"
	@echo "============================================================"

all-formal: compile-check test check-paths search verify certify lean audit deepmind-export manifest report
	@echo ""
	@echo "============================================================"
	@echo "  BUILD COMPLETE (full pipeline including Lean)"
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
