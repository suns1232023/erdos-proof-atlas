
-- ErdosAtlas/Audit/Axioms.lean
-- Axiom audit module: tracks which axioms are used in ErdosAtlas theorems.
--
-- REPAIR V3 (circular import fix):
--   PROBLEM: Previously imported both ErdosAtlas.CirclePacking.N10 and
--     ErdosAtlas.CirclePacking.Certificate. Since Basic.lean already imports
--     N10, importing N10 here again is redundant and risks circular imports
--     if the import chain is not carefully managed.
--   FIX: Import only what is strictly needed for axiom audit.
--     The #print axioms commands are run via `lake env lean` externally,
--     not compiled as part of the library build.
--
-- Usage:
--   After lake build, run: lake env lean ErdosAtlas/Audit/Axioms.lean
--   This prints the axioms used by each theorem.
--
-- Formal level: L1 → L5 gate
--   L5 requires: no sorry + only authorized axioms (Classical, propext, etc.)

import ErdosAtlas.CirclePacking.N10

namespace ErdosAtlas.Audit

-- ---------------------------------------------------------------------------
-- Authorized axioms (standard Lean 4 / mathlib axioms)
-- These are acceptable and do NOT prevent L5 certification.
-- ---------------------------------------------------------------------------
-- Classical.choice      — classical logic
-- propext               — propositional extensionality
-- Quot.sound            — quotient soundness
-- funext                — function extensionality (from mathlib)

-- ---------------------------------------------------------------------------
-- #print axioms — declaration-level axiom inspection
-- Run after lake build to inspect axiom usage:
-- ---------------------------------------------------------------------------

-- #print axioms ErdosAtlas.CirclePacking.circlePacking10MinDistBound
-- Expected output (L1 with sorry):
--   'ErdosAtlas.CirclePacking.circlePacking10MinDistBound' depends on axioms:
--   [sorryAx, Classical.choice, propext, Quot.sound]
--
-- Expected output (L5 target — no sorry):
--   'ErdosAtlas.CirclePacking.circlePacking10MinDistBound' depends on axioms:
--   [Classical.choice, propext, Quot.sound]

-- ---------------------------------------------------------------------------
-- Audit record structure
-- ---------------------------------------------------------------------------

/-- Audit record for a formal theorem. -/
structure AuditRecord where
  theoremName    : String
  formalLevel    : String
  sorryPresent   : Bool
  authorizedOnly : Bool
  notes          : String

/-- Current audit record for the N=10 packing theorem. -/
def n10AuditRecord : AuditRecord := {
  theoremName    := "circlePacking10MinDistBound"
  formalLevel    := "L1"
  sorryPresent   := true   -- sorry present at L1; target L5 = false
  authorizedOnly := true   -- only Classical.choice, propext, Quot.sound expected
  notes          := "Proof pending L3/L4. Use #print axioms to verify at L5."
}

end ErdosAtlas.Audit
