
-- ErdosAtlas/Problems/SquarePacking.lean
-- General square packing problem definitions and open questions.
--
-- REPAIR V3 (conflict fix):
--   PROBLEM 1: Previously imported ErdosAtlas.Geometry.Basic which defined
--     `def Point : Type := Fin 2 → ℝ` (function type).
--     This conflicts with Point.lean's `structure Point where x y : ℝ`.
--   FIX: Now imports Point.lean directly for the canonical structure Point.
--
--   PROBLEM 2: Defined `optimalPackingDist` which duplicates `optimalDist`
--     from CirclePacking/Definitions.lean.
--   FIX: Removed duplicate. Uses `optimalDist` from Definitions.lean.
--
-- Formal level: L1 (STATEMENT_FORMALIZED)
 
import ErdosAtlas.Geometry.Point
import ErdosAtlas.Geometry.UnitSquare
import ErdosAtlas.Geometry.Distance
import ErdosAtlas.CirclePacking.Definitions
import Mathlib.Data.Real.Basic
 
namespace ErdosAtlas.Problems
 
open ErdosAtlas.Geometry
open ErdosAtlas.CirclePacking
 
-- ---------------------------------------------------------------------------
-- Reference to the canonical optimal distance (defined in Definitions.lean)
-- ---------------------------------------------------------------------------
 
-- optimalDist is defined in ErdosAtlas.CirclePacking.Definitions:
--   noncomputable def optimalDist (n : ℕ) : ℝ := sSup (achievableDistances n)
-- We use it directly here rather than redefining.
 
-- ---------------------------------------------------------------------------
-- Known algebraic degrees of d_n for small n
-- ---------------------------------------------------------------------------
 
/-- Known algebraic degrees of d_n for small n:
    n=4:  deg = 1  (rational: d4 = 1, trivial — 4 corners)
    n=9:  deg = 1  (rational: d9 = 1/2, 3×3 grid)
    n=10: deg = 18 (P18(d), Gal ≅ S18, not expressible by radicals)
    Open question: How does [Q(d_n):Q] grow with n? -/
 
/-- Statement: d9 = 1/2 (3×3 grid configuration). -/
theorem d9_eq_half : optimalDist 9 = 1 / 2 := by
  sorry  -- L1: statement correct, proof pending
 
/-- Open problem: Algebraic complexity of d_n.
    Conjecture: For n with C1 symmetry (no geometric symmetry),
    Gal(min_poly(d_n)/Q) ≅ S_k for some large k.
    Verified for n=10: k=18 (this work, V1.4). -/
def AlgebraicComplexityConjecture : Prop :=
  ∀ n : ℕ, n ≥ 10 →
  ∃ k : ℕ, k ≥ 18 ∧
  -- The minimal polynomial of d_n has degree k
  -- and its Galois group is S_k (not expressible by radicals)
  True  -- placeholder until formal polynomial connection is established
 
end ErdosAtlas.Problems
 
