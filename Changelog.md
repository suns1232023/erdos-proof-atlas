# Changelog

## [0.1.0] - 2026-08-14

### Added
- Dual-axis evidence model (E0-E5 computational, L0-L5 formal)
- Circle packing geometry module (independent of optimizer)
- Multistart SLSQP search (always NUMERICAL status)
- Independent verifier (separate code paths)
- Adversarial test suite
- Polynomial + Galois certificate system
- Lean 4 project (formal/lean/) — L1 statement formalized
- DeepMind compatibility bridge
- 6 GitHub Actions workflows (including lean-check.yml)
- atlas_audit.py with formal evidence reporting

### Historical Note
The degree-18 polynomial for N=10 was first established by
de Groot, Peikert & Würtz (1990). This repository provides
independent reproduction and formalization infrastructure.
