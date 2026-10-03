"""
Erdős Proof Atlas
=================
Computational Discovery, Exact Certification, and Lean-Checked Mathematics.

Evidence Model (two independent axes):

Computational Evidence (E-axis):
  E0 IDEA
  E1 NUMERICAL
  E2 COMPUTATIONAL
  E3 INDEPENDENTLY_VERIFIED
  E4 EXACTIFIED
  E5 SYMBOLICALLY_CERTIFIED

Formal Evidence (L-axis):
  L0 NOT_FORMALIZED
  L1 STATEMENT_FORMALIZED
  L2 DEFINITIONS_FORMALIZED
  L3 KEY_LEMMAS_FORMALIZED
  L4 THEOREM_PROVED
  L5 LEAN_BUILD_VERIFIED

FORBIDDEN auto-upgrades:
  NUMERICAL -> THEOREM
  COMPUTATIONAL -> THEOREM
  CERTIFICATE -> FORMAL_PROOF
  AI_GENERATED -> VERIFIED
  GitHub Actions success -> epistemic status change
"""

__version__ = "0.1.0"
__author__ = "Scott Sun"
__project__ = "Erdős Proof Atlas"
