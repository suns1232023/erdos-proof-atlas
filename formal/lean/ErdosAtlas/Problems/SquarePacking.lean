
-- ErdosAtlas/Problems/SquarePacking.lean
-- General square packing problem definitions and open questions.
--
-- Formal level: L1 (STATEMENT_FORMALIZED)
 
import ErdosAtlas.Geometry.Basic
import Mathlib.Data.Real.Basic
 
namespace ErdosAtlas.Problems
 
open ErdosAtlas.Geometry
 
/-- The optimal packing distance for n points in the unit square.
    d_n = max over all configurations of (min pairwise distance).
    This is a noncomputable real number for each n. -/
noncomputable def optimalPackingDist (n : ℕ) : ℝ :=
  sSup { d : ℝ | ∃ pts : Fin n → Point,
    AllInUnitSquare pts ∧ PairwiseSeparated pts d }
 
/-- Known algebraic degrees of d_n for small n:
    n=4:  deg = 1  (rational: d4 = √2/2... actually d4 = 1, trivial)
    n=9:  deg = 1  (rational: d9 = 1/2, 3×3 grid)
    n=10: deg = 18 (P18(d), Gal ≅ S18, not expressible by radicals)
    Open question: How does [Q(d_n):Q] grow with n? -/
 
/-- Statement: d9 = 1/2 (3×3 grid configuration). -/
theorem d9_eq_half : optimalPackingDist 9 = 1 / 2 := by
  sorry  -- L1: statement correct, proof pending
 
/-- Open problem: Algebraic complexity of d_n.
    Conjecture: For n with C1 symmetry (no geometric symmetry),
    Gal(min_poly(d_n)/Q) ≅ S_k for some large k.
    Verified for n=10: k=18. -/
def AlgebraicComplexityConjecture : Prop :=
  ∀ n : ℕ, n ≥ 10 →
  ∃ k : ℕ, k ≥ 18 ∧
  -- The minimal polynomial of d_n has degree k
  -- and its Galois group is S_k (not expressible by radicals)
  True  -- placeholder until formal polynomial connection is established
 
end ErdosAtlas.Problems
 

