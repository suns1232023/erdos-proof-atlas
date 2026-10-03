# Erdős Proof Atlas — Research Report
Problem: `circle-packing-square`  |  Generated: `2026-10-03T03:50:44Z`

## Evidence Status Legend
- `[E5/L5]` — Symbolically certified + Lean-checked (strongest)
- `[E5/L0]` — Symbolically certified, not yet formalized
- `[E3/L1]` — Independently verified, statement formalized
- `[NUMERICAL]` — Numerical result only (E1). NOT a proof.
- `[OPEN]` — No evidence available.

---

## 1. Problem Definition
Problem ID: `circle-packing-square`

## 2. Numerical Search [E1]
**[NUMERICAL]** Objective: `0.4212795439838933`
Algorithm: `multistart_slsqp_slack`
> ⚠️ NUMERICAL result. NOT a proof.

## 3. Independent Verification [E3]
[E3/COMP_VERIF] Passed: `True`
Min distance: `0.4212795439838933`

## 4. Exact Certificate [E4/E5]
**[E5]** Degree: `18`
Irreducibility: `CHECKED`
Historical note: Polynomial first established by de Groot, Peikert & Würtz (1990). Independent reproduction.

## 5. Galois Certificate [E5]
[OPEN] No Galois certificate.

## 6. Lean Formalization
[L0/OPEN] Lean formalization not yet available.

## 7. Provenance
Run ID: `fbf36c4b-8c2`
Git commit: `UNKNOWN`
Timestamp: `2026-10-03T03:50:35Z`

## 8. Known Limitations
- Galois group: Steps 3-4 (primitivity, Jordan) are computational evidence, not rigorous proof.
- Lean formalization: IMPLEMENTATION_PENDING for full theorem.
- Global optimality: relies on historical literature (Szabó et al. 2007, Specht 2022).

## 9. Open Tasks
- [ ] Rigorous primitivity proof (GAP/Magma)
- [ ] Lean theorem without sorry
- [ ] DeepMind-compatible export
- [ ] N=11..20 polynomial database
