"""Report generator. Labels: [E5/L5] [ALGEBRAIC] [COMP_VERIF] [NUMERICAL] [OPEN]"""

from __future__ import annotations
import json, time
from pathlib import Path
from typing import Optional


def generate_atlas_report(problem_id: str, search_result: Optional[dict], verification_result: Optional[dict],
                          polynomial_cert: Optional[dict], galois_cert: Optional[dict],
                          lean_status: Optional[dict], provenance: Optional[dict], output_path: Path) -> str:
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    lines = [
        f"# Erdős Proof Atlas — Research Report",
        f"Problem: `{problem_id}`  |  Generated: `{ts}`",
        "",
        "## Evidence Status Legend",
        "- `[E5/L5]` — Symbolically certified + Lean-checked (strongest)",
        "- `[E5/L0]` — Symbolically certified, not yet formalized",
        "- `[E3/L1]` — Independently verified, statement formalized",
        "- `[NUMERICAL]` — Numerical result only (E1). NOT a proof.",
        "- `[OPEN]` — No evidence available.",
        "",
        "---",
        "",
        "## 1. Problem Definition",
        f"Problem ID: `{problem_id}`",
        "",
        "## 2. Numerical Search [E1]",
    ]
    if search_result:
        lines += [f"**[NUMERICAL]** Objective: `{search_result.get('objective','N/A')}`",
                  f"Algorithm: `{search_result.get('algorithm','N/A')}`",
                  "> ⚠️ NUMERICAL result. NOT a proof."]
    else:
        lines.append("[OPEN] No search result.")

    lines += ["", "## 3. Independent Verification [E3]"]
    if verification_result:
        passed = verification_result.get("passed", False)
        label = "[E3/COMP_VERIF]" if passed else "[NUMERICAL/FAIL]"
        lines += [f"{label} Passed: `{passed}`",
                  f"Min distance: `{verification_result.get('min_distance','N/A')}`"]
    else:
        lines.append("[OPEN] No verification result.")

    lines += ["", "## 4. Exact Certificate [E4/E5]"]
    if polynomial_cert:
        lines += [f"**[E5]** Degree: `{polynomial_cert.get('degree','N/A')}`",
                  f"Irreducibility: `{polynomial_cert.get('irreducible',{}).get('status','N/A')}`",
                  f"Historical note: {polynomial_cert.get('historical_note','')}"]
    else:
        lines.append("[OPEN] No polynomial certificate.")

    lines += ["", "## 5. Galois Certificate [E5]"]
    if galois_cert:
        lines += [f"**[E5]** Group claim: `{galois_cert.get('group_claim','N/A')}`",
                  f"Method: `{galois_cert.get('method','N/A')}`",
                  f"Notes: {galois_cert.get('notes','')}",
                  "> ⚠️ ALGEBRAIC_CERTIFIED, not THEOREM. Lean proof required for L5."]
    else:
        lines.append("[OPEN] No Galois certificate.")

    lines += ["", "## 6. Lean Formalization"]
    if lean_status:
        l_level = lean_status.get("level", "L0")
        lines += [f"**[{l_level}]** Status: `{lean_status.get('status','N/A')}`",
                  f"Lean file: `{lean_status.get('lean_file','N/A')}`",
                  f"lake build: `{lean_status.get('lake_build','N/A')}`"]
    else:
        lines.append("[L0/OPEN] Lean formalization not yet available.")

    lines += ["", "## 7. Provenance"]
    if provenance:
        lines += [f"Run ID: `{provenance.get('run_id','N/A')}`",
                  f"Git commit: `{provenance.get('git_commit','N/A')}`",
                  f"Timestamp: `{provenance.get('timestamp_utc','N/A')}`"]
    else:
        lines.append("[OPEN] No provenance record.")

    lines += ["", "## 8. Known Limitations",
              "- Galois group: Steps 3-4 (primitivity, Jordan) are computational evidence, not rigorous proof.",
              "- Lean formalization: IMPLEMENTATION_PENDING for full theorem.",
              "- Global optimality: relies on historical literature (Szabó et al. 2007, Specht 2022).",
              "", "## 9. Open Tasks",
              "- [ ] Rigorous primitivity proof (GAP/Magma)",
              "- [ ] Lean theorem without sorry",
              "- [ ] DeepMind-compatible export",
              "- [ ] N=11..20 polynomial database"]

    report = "\n".join(lines)
    output_path.write_text(report)
    return report


def generate_audit_report(results: dict) -> str:
    lines = [
        "=" * 60,
        "ERDŐS PROOF ATLAS — FORMAL AUDIT",
        "=" * 60,
    ]
    for problem, status in results.items():
        lines.append(f"\nProblem: {problem}")
        for category, items in status.items():
            lines.append(f"\n{category}:")
            for key, val in items.items():
                lines.append(f"  {key:<30} {val}")
    lines.append("\n" + "=" * 60)
    return "\n".join(lines)
