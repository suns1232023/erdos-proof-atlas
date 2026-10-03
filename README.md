# Erdős Proof Atlas

### Reproducible Discovery · Independent Verification · Exact Certification · Formalization

> An open research infrastructure for computational and formal study of Erdős and extremal-mathematics problems.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)
[![Lean](https://img.shields.io/badge/Lean-4-purple.svg)](formal/lean/lean-toolchain)
[![Status](https://img.shields.io/badge/status-research--infrastructure-orange.svg)](docs/)

---

## 1. What is Erdős Proof Atlas?

Many difficult mathematical problems now pass through several different stages:

```text
mathematical question
        ↓
computational exploration
        ↓
candidate discovery
        ↓
independent verification
        ↓
exact / symbolic certification
        ↓
formal mathematical statement
        ↓
machine-checked proof
```

These stages are often mixed together.

A numerical optimizer may find a highly convincing candidate.

A large computation may verify millions or billions of cases.

A symbolic calculation may identify an exact algebraic object.

A Lean development may formalize part of the argument.

But **none of these stages automatically implies the next one**.

Erdős Proof Atlas is designed to keep these epistemic layers separate while providing reproducible connections between them.

> **Solver ≠ Verifier ≠ Certificate ≠ Formal Proof**

The project therefore treats computational discovery and mathematical proof as related but distinct objects.

---

# 2. Research Question

The initial case study is the classical extremal geometry problem of packing points in a unit square.

For \(N\) points

\[
P_1,\ldots,P_N\in[0,1]^2,
\]

one seeks to maximize the minimum pairwise distance

\[
d_N
=
\max_{P_1,\ldots,P_N}
\min_{i\ne j}\|P_i-P_j\|.
\]

Equivalently, this can be viewed as a circle-packing / dispersion problem in a bounded domain.

The first vertical slice of this repository focuses on the historically studied **\(N=10\)** case.

The repository is not intended to replace the mathematical literature. Instead, it provides an auditable computational and formalization framework around a concrete extremal problem.

---

# 3. Why This Repository Exists

The project addresses a practical reproducibility problem.

For a computationally difficult extremal problem, a result may depend on:

- numerical optimization;
- initialization;
- search strategy;
- floating-point precision;
- independent implementations;
- symbolic elimination;
- polynomial arithmetic;
- algebraic-number certification;
- proof-assistant formalization.

These are different sources of evidence.

The Atlas records them separately and attempts to preserve the chain:

```text
Problem
  │
  ├── Search
  │
  ├── Independent Verification
  │
  ├── Exact Certificate
  │
  ├── Formal Statement
  │
  └── Machine-Checked Proof
```

A successful computational run therefore does not silently become a theorem.

---

# 4. First Case Study: N = 10 Square Packing

The current repository uses the \(N=10\) square-packing problem as its first complete research case study.

The historical degree-18 algebraic description of the optimal distance is not claimed as a new discovery by this repository. The project instead reconstructs and audits the computational and algebraic pipeline around the known problem.

The current research artifacts include:

- numerical search;
- independent verification;
- regression and adversarial testing;
- exact polynomial data;
- symbolic certification infrastructure;
- Galois-group certification infrastructure;
- Lean 4 formalization infrastructure;
- provenance and audit records.

The repository therefore should be read as a **reproducibility and certification project**, not as a claim of priority for the underlying mathematical result.

---

# 5. Evidence Model

A central design principle is that computational and formal evidence are tracked independently.

## Computational Evidence

| Level | Meaning |
|---|---|
| **E0** | Research idea / problem definition |
| **E1** | Numerical observation |
| **E2** | Computational result |
| **E3** | Independently verified computation |
| **E4** | Exactified result |
| **E5** | Symbolically certified result |

## Formal Evidence

| Level | Meaning |
|---|---|
| **L0** | Not formalized |
| **L1** | Mathematical statement formalized |
| **L2** | Core definitions formalized |
| **L3** | Key supporting lemmas formalized |
| **L4** | Proof source substantially completed |
| **L5** | Lean build / kernel verification completed under the project's verification rules |

A result can therefore be described as:

```text
E3 / L1
E5 / L2
E5 / L5
```

rather than being assigned a single undifferentiated “verified” label.

### Important

A GitHub Actions success does not automatically upgrade a mathematical claim.

A numerical result does not automatically become a theorem.

A symbolic polynomial does not automatically become a proof of the geometric optimization problem.

A Lean file does not automatically constitute a complete formal proof merely because it compiles.

---

# 6. Current Research Status

The current project should be understood as a **research infrastructure under active formalization**, rather than a finished formal-proof library.

| Component | Current status |
|---|---|
| Square-packing computational framework | **E1–E3** |
| Independent verification architecture | **E3** |
| Adversarial / regression testing | **Active** |
| Exact polynomial infrastructure | **E4–E5** |
| Galois-group certification infrastructure | **E5 infrastructure** |
| Lean 4 geometry / N=10 formalization | **L1 / under development** |
| DeepMind metadata bridge | **Under development** |
| End-to-end Lean certification | **Open / pending** |

The distinction between **infrastructure completed** and **mathematical theorem formally proved** is intentional.

---

# 7. The N = 10 Algebraic Layer

One of the important objects associated with the \(N=10\) case is a degree-18 polynomial describing the relevant algebraic distance.

This repository reconstructs the associated symbolic pipeline rather than presenting the polynomial as a newly discovered result.

The symbolic layer is intended to make the following chain auditable:

```text
geometric configuration
        ↓
contact / rigidity structure
        ↓
algebraic equations
        ↓
symbolic elimination
        ↓
integer polynomial
        ↓
irreducibility / algebraic certification
        ↓
Galois-group analysis
```

This separation is important because:

> finding a polynomial is not the same as proving that it describes the global optimum.

The repository therefore keeps geometric optimization, symbolic elimination, and formal proof as separate layers.

---

# 8. Numerical Search Is Not the Proof

The numerical search layer is designed for discovery and candidate generation.

It may use:

- multistart optimization;
- nonlinear constrained optimization;
- numerical distance evaluation;
- contact-graph information;
- regression against known cases.

Numerical output is therefore classified as computational evidence.

For example:

```text
numerical optimizer
       ↓
candidate configuration
       ↓
independent verifier
       ↓
exactification
```

The optimizer is not treated as a theorem prover.

---

# 9. Independent Verification

A second implementation or an independent verification path has a different epistemic role from the original solver.

The project therefore attempts to maintain:

```text
SEARCHER
   ≠
VERIFIER
```

The verifier should not merely call the same function used by the searcher and repeat its assumptions.

Instead, verification should use an independent code path wherever practical.

This distinction is particularly important for computational mathematics, where the same implementation error can otherwise reproduce itself consistently.

---

# 10. Exact Certification

The exact-certification layer attempts to move from numerical observations to exact mathematical objects.

Typical artifacts include:

```text
exact polynomial
integer coefficients
primitive polynomial
finite-field reductions
irreducibility evidence
root isolation
certificate metadata
hash / provenance information
```

The goal is not merely to print a symbolic expression, but to preserve enough information for an independent reader to reconstruct how the certificate was obtained.

---

# 11. Formalization Strategy

The Lean component is deliberately separated from the numerical search.

The intended progression is:

```text
Geometry
   ↓
Exact Definitions
   ↓
Packing Predicate
   ↓
Distance / Separation Lemmas
   ↓
N=10 Statement
   ↓
Supporting Lemmas
   ↓
Formal Proof
```

The current N=10 Lean development should therefore be interpreted as a **formalization starting point**, not as a completed proof of the optimal-packing theorem.

The repository explicitly avoids treating placeholder statements, incomplete proofs, or computational certificates as equivalent to a kernel-checked mathematical theorem.

---

# 12. Connection to the Formal Mathematics Ecosystem

The project is designed to be interoperable with broader formal-mathematics ecosystems, including Lean-based Erdős problem formalization projects.

The intended bridge is:

```text
Atlas Problem
      ↓
Canonical Problem ID
      ↓
Mathematical Statement
      ↓
Lean Declaration
      ↓
Formal Verification
```

A future DeepMind / formal-conjectures bridge should therefore provide machine-readable metadata rather than merely claiming compatibility.

The bridge is considered complete only when the exported problem identifier, theorem name, Lean file, and formal status can be independently resolved.

---

# 13. Repository Architecture

The repository is organized around the research pipeline rather than around a single monolithic solver.

```text
erdos-proof-atlas/
│
├── problems/
│   └── erdos/
│       └── circle_packing_n10/
│
├── src/
│   └── atlas/
│       ├── schema/
│       ├── geometry/
│       ├── search/
│       ├── verification/
│       ├── symbolic/
│       ├── certification/
│       ├── provenance/
│       ├── reporting/
│       └── cli/
│
├── certificates/
│   └── circle_packing_n10/
│
├── results/
│   └── latest/
│
├── formal/
│   └── lean/
│
├── bridges/
│   └── deepmind/
│
├── scripts/
│
├── test/
│
├── docs/
│
├── .github/
│   └── workflows/
│
├── Makefile
├── pyproject.toml
├── CITATION.cff
├── LICENSE
└── README.md
```

The directory names are implementation details; the conceptual architecture is:

```text
PROBLEM
   ↓
SEARCH
   ↓
VERIFY
   ↓
CERTIFY
   ↓
FORMALIZE
   ↓
AUDIT
   ↓
REPORT
```

---

# 14. Reproducible Workflow

After installation, the intended workflow is:

```bash
# 1. Install
pip install -e ".[symbolic,dev]"

# 2. Numerical exploration
make search

# 3. Independent verification
make verify

# 4. Exact / symbolic certification
make exact

# 5. Lean formalization check
make lean

# 6. Repository and evidence audit
make audit

# 7. Generate research report
make report
```

For a complete local pipeline:

```bash
make all
```

Individual commands should be preferred during development because each stage has a different mathematical role.

---

# 15. Reproducibility

A reproducible result should answer five questions:

### 1. What was searched?

The exact problem definition and parameter range.

### 2. How was it searched?

The algorithm, numerical assumptions, initialization strategy, and configuration.

### 3. How was it independently verified?

A separate verification path and test suite.

### 4. How was it exactified?

The symbolic or algebraic certificate construction.

### 5. What has actually been formalized?

The precise Lean status, including any remaining proof gaps.

The repository therefore treats reproducibility as part of the mathematical record rather than as an optional software feature.

---

# 16. Tests and Adversarial Checks

The project includes testing at several levels:

```text
Unit
  ↓
Integration
  ↓
Regression
  ↓
Adversarial
  ↓
Formal verification
```

Adversarial tests are particularly important.

The system should reject invalid epistemic transitions such as:

```text
NUMERICAL → THEOREM
COMPUTATIONAL → THEOREM
AI_GENERATED → VERIFIED
PLACEHOLDER → FORMAL PROOF
```

The software should fail explicitly rather than silently upgrading a result.

---

# 17. What This Repository Does Not Claim

This repository does **not** claim that:

- numerical optimization alone proves a global optimum;
- a successful CI run is equivalent to a mathematical proof;
- an exact polynomial automatically proves the geometric theorem;
- the current Lean layer constitutes a complete formal proof of the N=10 problem;
- metadata export alone establishes formal compatibility with another proof ecosystem;
- computational evidence eliminates the need for mathematical interpretation.

These limitations are part of the project's design.

---

# 18. Open Research Tasks

The current research program includes several directions.

### Geometry

- Complete the exact formal definition of the packing problem.
- Formalize the relevant geometric lemmas.
- Connect the numerical configuration to an exact configuration.

### Algebra

- Complete the symbolic elimination chain.
- Independently validate polynomial certificates.
- Formalize the relationship between the polynomial and the geometric quantity.
- Complete the algebraic certification chain.

### Galois Theory

- Maintain an auditable finite-field certification record.
- Separate computational evidence from theorem-level conclusions.
- Formalize the relevant algebraic statements where practical.

### Lean

- Complete the N=10 definitions.
- Formalize the principal theorem statement.
- Add supporting lemmas.
- Establish a reproducible Lean build.
- Progress from L1 toward kernel-checked results.

### Interoperability

- Stabilize the canonical problem schema.
- Validate the DeepMind / formal-conjectures mapping.
- Make theorem identifiers machine-resolvable.
- Preserve provenance between computational and formal artifacts.

---

# 19. Research Philosophy

The project follows a simple rule:

> **Do not make the claim stronger than the evidence.**

A result may be computationally impressive and still remain mathematically open.

A proof assistant may formalize a statement while leaving an important theorem unfinished.

An exact algebraic certificate may be completely correct while answering only one part of the original geometric problem.

The Atlas therefore records not only positive results, but also:

- failed approaches;
- incomplete formalizations;
- reproducibility gaps;
- unresolved inconsistencies;
- historical corrections;
- boundaries between computation and proof.

This is intentional.

---

# 20. Relationship to Other Research Repositories

The repository is part of a broader research workflow rather than an isolated software package.

For example:

```text
Erdős Proof Atlas
        │
        ├── computational experiments
        │
        ├── exact certificates
        │
        ├── Lean formalization
        │
        └── external formal-mathematics ecosystems
```

The Atlas is intended to complement, rather than replace:

- the mathematical literature;
- OEIS;
- formal-conjecture databases;
- Lean mathematical libraries;
- independent computational implementations.

---

# 21. Historical Attribution

The N=10 algebraic problem has a history predating this repository.

The repository therefore distinguishes:

```text
historical mathematical result
        ≠
independent computational reproduction
        ≠
new mathematical discovery
```

The degree-18 polynomial associated with the N=10 problem is treated as a historical object to be reconstructed and certified, not as a discovery claimed by this repository.

Relevant bibliographic and provenance information should be maintained in the accompanying documentation and certificate records.

---

# 22. Citation

If you use the software, computational artifacts, or repository infrastructure in research, please cite the repository using [`CITATION.cff`](CITATION.cff).

For mathematical claims, please also cite the underlying primary literature rather than treating this repository as a replacement for the literature.

---

# 23. Project Status

**Research infrastructure: Active**

The project is currently best understood as:

```text
Computational infrastructure     █████████░
Independent verification         ████████░░
Exact certification              ████████░░
Lean formalization               ███░░░░░░░
Interoperability                 ███░░░░░░░
```

These bars are qualitative project indicators, not mathematical scores or proof probabilities.

The formalization and interoperability layers remain active development areas.

---

# 24. License

Code and repository infrastructure are released under the license specified in [`LICENSE`](LICENSE).

Documentation and research artifacts follow their respective stated licenses.

---

## Erdős Proof Atlas

**Computational Discovery → Independent Verification → Exact Certification → Formal Mathematics**

> **The purpose is not to make computation look like proof.  
> The purpose is to make the boundary between computation and proof explicit, reproducible, and progressively bridgeable.**
