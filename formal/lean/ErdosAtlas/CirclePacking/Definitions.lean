
-- ErdosAtlas/CirclePacking/Definitions.lean
-- Core packing definitions for N points in the unit square.

import ErdosAtlas.Geometry.Point
import ErdosAtlas.Geometry.UnitSquare
import ErdosAtlas.Geometry.Distance
import Mathlib.Data.Real.Basic
import Mathlib.Topology.Algebra.Order.LiminfLimsup

namespace ErdosAtlas.CirclePacking

open ErdosAtlas.Geometry

/-- A valid packing: n points in the unit square with pairwise squared distance ≥ d². -/
def IsPacking {n : Nat} (pts : Fin n → Point) (d : Real) : Prop :=
  AllInUnitSquare pts ∧ PairwiseSeparated pts d

/-- The set of achievable separation distances for n points in the unit square. -/
def achievableDistances (n : Nat) : Set Real :=
  { d : Real | ∃ pts : Fin n → Point, IsPacking pts d }

/-- The optimal packing distance: supremum of all achievable separation distances. -/
noncomputable def optimalDist (n : Nat) : Real :=
  sSup (achievableDistances n)

-- d=0 is always achievable (all points at origin satisfies d=0 trivially)
theorem zero_achievable (n : Nat) : (0 : Real) ∈ achievableDistances n := by
  simp only [achievableDistances, Set.mem_setOf_eq]
  refine ⟨fun _ => ⟨0, 0⟩, ?_, ?_⟩
  · intro i
    simp [AllInUnitSquare, InUnitSquare, Point.x, Point.y]
  · intro i j _
    simp [PairwiseSeparated, squaredDist, Point.x, Point.y]

end ErdosAtlas.CirclePacking
