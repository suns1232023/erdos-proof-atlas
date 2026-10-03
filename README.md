# Erdős Proof Atlas — DRAFT README

> **DRAFT**: Working draft. Final public README will be rewritten separately.

## Project Purpose

**Erdős Proof Atlas** is an open research infrastructure for connecting Erdős and extremal-mathematics problems with reproducible computation, exact certificates, and machine-checked Lean proofs.

**First vertical slice**: N=10 Square Packing — complete end-to-end evidence chain.

### Core Principle

```
SOLVER ≠ VERIFIER ≠ CERTIFICATE ≠ FORMAL PROOF
```

A numerical result is never automatically promoted to a theorem.
A GitHub Actions success never changes the epistemic status of a mathematical claim.

## Evidence Model (Dual-Axis)

| Axis | Level | Meaning |
|------|-------|---------|
| **E** (Computational) | E0 | Idea |
| | E1 | Numerical result |
| | E2 | Computational result |
| | E3 | Independently verified |
| | E4 | Exactified |
| | E5 | Symbolically certified |
| **L** (Formal) | L0 | Not formalized |
| | L1 | Statement formalized |
| | L2 | Definitions formalized |
| | L3 | Key lemmas formalized |
| | L4 | Theorem proved (may use sorry) |
| | L5 | Lean build verified (no sorry) |

A result is represented as `E5/L0`, `E3/L1`, `E5/L5`, etc.

## Installation

```bash
git clone https://github.com/suns1232023/erdos-proof-atlas
cd erdos-proof-atlas
pip install -e ".[symbolic,dev]"
```

## Usage

```bash
make search          # Numerical search (E1)
make verify          # Independent verification (E3)
make exact           # Build algebraic certificate (E5)
make lean            # Check Lean build (L0-L5)
make audit           # Full audit
make report          # Generate report
make deepmind-export # DeepMind-compatible metadata
make all             # Complete pipeline
```

## Historical Note (N=10)

The degree-18 minimal polynomial for N=10 was first established by
**de Groot, Peikert & Würtz (1990)** and is recorded in OEIS A281065.
This repository provides:
1. Independent computational reproduction
2. Symbolic certification (Galois group evidence)
3. Lean formalization infrastructure

It does NOT claim to have discovered the polynomial.

## Current Status

| Component | Status |
|-----------|--------|
| Circle packing geometry | ✅ E3 |
| Multistart SLSQP search | ✅ E1 |
| Independent verifier | ✅ E3 |
| Adversarial test suite | ✅ |
| Polynomial certificate | ✅ E5 |
| Galois certificate | ✅ E5 |
| Lean formalization | ⚠️ L1 (statement only) |
| DeepMind bridge | ✅ metadata |
| Regression tests (N=2,4,9,10) | ✅ |

## DeepMind Compatibility

See [docs/DEEPMIND_BRIDGE.md](docs/DEEPMIND_BRIDGE.md).
