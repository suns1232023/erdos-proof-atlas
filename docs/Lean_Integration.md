# Lean Integration

## Certificate → Lean Pipeline

```
Python certificate (JSON)
    │
    ▼
Certificate parser / exporter
    │
    ▼
Lean constants / definitions
    │
    ▼
Formal lemmas
    │
    ▼
Theorem
    │
    ▼
lake build (no sorry, no axiom)
    │
    ▼
L5: LEAN_BUILD_VERIFIED
```

## Current Status

- `formal/lean/` is a valid Lean 4 + Lake project
- `lean-toolchain` pins the exact Lean version
- `ErdosAtlas/CirclePacking/N10.lean` contains the formal statement (L1)
- Full proof is IMPLEMENTATION_PENDING

## Running Lean

```bash
cd formal/lean
lake exe cache get
lake build
```

## Checking for sorry

```bash
grep -r "sorry" formal/lean/ErdosAtlas/ --include="*.lean"
```

If sorry is found: formal level is L4.
If no sorry and build succeeds: formal level is L5.
