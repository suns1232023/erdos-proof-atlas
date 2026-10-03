# Evidence Model

## Two Independent Axes

### E-Axis: Computational Evidence

| Level | Name | Description |
|-------|------|-------------|
| E0 | IDEA | Conjecture or idea |
| E1 | NUMERICAL | Numerical result (not a proof) |
| E2 | COMPUTATIONAL | Computational result |
| E3 | INDEPENDENTLY_VERIFIED | Verified by separate implementation |
| E4 | EXACTIFIED | Exact algebraic form |
| E5 | SYMBOLICALLY_CERTIFIED | Algebraic certificate |

### L-Axis: Formal Evidence

| Level | Name | Description |
|-------|------|-------------|
| L0 | NOT_FORMALIZED | No Lean formalization |
| L1 | STATEMENT_FORMALIZED | Statement in Lean |
| L2 | DEFINITIONS_FORMALIZED | Definitions in Lean |
| L3 | KEY_LEMMAS_FORMALIZED | Key lemmas in Lean |
| L4 | THEOREM_PROVED | Proved (may use sorry) |
| L5 | LEAN_BUILD_VERIFIED | No sorry, no axiom |

## Forbidden Auto-Upgrades

- NUMERICAL → THEOREM ❌
- COMPUTATIONAL → THEOREM ❌
- AI_GENERATED → VERIFIED ❌
- CERTIFICATE → FORMAL_PROOF ❌
- GitHub Actions success → epistemic status change ❌
