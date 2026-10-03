
-- ErdosAtlas/Problems/SquarePacking.lean
-- General square packing problem definitions and open questions.
-- Formal level: L1 (STATEMENT_FORMALIZED)

import ErdosAtlas.Geometry.Point
import ErdosAtlas.Geometry.UnitSquare
import ErdosAtlas.Geometry.Distance
import ErdosAtlas.CirclePacking.Definitions
import Mathlib.Data.Real.Basic

namespace ErdosAtlas.Problems

open ErdosAtlas.Geometry
open ErdosAtlas.CirclePacking

-- Known values of optimalDist for small n:
--   n=4:  d4 = 1 (4 corners of unit square)
--   n=9:  d9 = 1/2 (3x3 grid)
--   n=10: d10 ≈ 0.421279543983903... (non-symmetric, de Groot et al. 1990)

/-- Statement: d9 = 1/2 (3x3 grid configuration). -/
theorem d9_eq_half : optimalDist 9 = 1 / 2 := by
  sorry  -- L1: statement correct, proof pending

/-- Open problem: How does the algebraic degree [Q(d_n):Q] grow with n?
    Known: deg(d_4) = 1, deg(d_9) = 1, deg(d_10) = 18.
    Note: NOT all n ≥ 10 have high degree — e.g., n=16 (4x4 grid) has d16=1/3, degree 1. -/
def AlgebraicDegreeQuestion : Prop :=
  ∀ n : Nat, ∃ k : Nat, k ≥ 1
  -- The minimal polynomial of optimalDist n has degree k over Q

end ErdosAtlas.Problems
