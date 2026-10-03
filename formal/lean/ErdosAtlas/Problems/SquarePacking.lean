-- ErdosAtlas/Problems/SquarePacking.lean
-- Formal level: L1

import ErdosAtlas.Geometry.Point
import ErdosAtlas.Geometry.UnitSquare
import ErdosAtlas.Geometry.Distance
import ErdosAtlas.CirclePacking.Definitions
import Mathlib.Data.Real.Basic

namespace ErdosAtlas.Problems

open ErdosAtlas.Geometry
open ErdosAtlas.CirclePacking

/-- d9 = 1/2 (3x3 grid). Proof pending. -/
theorem d9_eq_half : optimalDist 9 = 1 / 2 := by
  sorry

/-- Open question: How does [Q(d_n):Q] grow with n?
    Known: deg(d_4)=1, deg(d_9)=1, deg(d_10)=18.
    Note: n=16 (4x4 grid) has d=1/3, degree=1 — NOT all n>=10 have high degree. -/
def AlgebraicDegreeQuestion : Prop :=
  forall n : Nat, exists k : Nat, k >= 1

end ErdosAtlas.Problems
