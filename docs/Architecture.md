# Architecture

## Two Independent Tracks

```
ERDŐS PROBLEM
    │
    ├── Computational Track          Formal Track
    │   │                            │
    │   Search/Solver                Lean / Mathlib
    │   │                            │
    │   Candidate                    Formal Lemmas
    │   │                            │
    │   Independent Verification     Proof Obligations
    │   │                            │
    │   Exactification               │
    │   │                            │
    │   Symbolic Certificate         │
    │   │                            │
    └───┴────── EVIDENCE BRIDGE ─────┘
                    │
                LEAN CERTIFICATE
                    │
               lake build
                    │
            FORMALLY CHECKED
```

## Module Responsibilities

| Module | Responsibility | Must NOT import |
|--------|---------------|-----------------|
| `schema/` | Evidence types | nothing |
| `geometry/` | Packing evaluation | search/ |
| `search/` | Numerical optimization | verification/ |
| `verification/` | Independent checker | search/ |
| `exact/` | Exactification | search/ |
| `certification/` | Algebraic certs | search/ |
| `formalization/` | Lean interface | search/, verification/ |
| `provenance/` | Reproducibility | stdlib only |
| `reporting/` | Report generation | all above |
