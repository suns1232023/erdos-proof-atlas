
-- ErdosAtlas/CirclePacking/Definitions.lean
-- Core packing definitions for N points in the unit square.
--
-- REPAIR V2 (per reviewer):
--   Defines IsPacking using real-valued geometry (not Float).
--   Separates definitions from theorem statements.
 
import ErdosAtlas.Geometry.Point
import ErdosAtlas.Geometry.UnitSquare
import ErdosAtlas.Geometry.Distance
import Mathlib.Data.Real.Basic
 
namespace ErdosAtlas.CirclePacking
 
open ErdosAtlas.Geometry
 
/-- A valid packing: n points in the unit square with pairwise squared distance ≥ d². -/
def IsPacking {n : ℕ} (pts : Fin n → Point) (d : ℝ) : Prop :=
  AllInUnitSquare pts ∧ PairwiseSeparated pts d
 
/-- The set of achievable separation distances for n points in the unit square. -/
def achievableDistances (n : ℕ) : Set ℝ :=
  { d : ℝ | ∃ pts : Fin n → Point, IsPacking pts d }
 
/-- The optimal packing distance: supremum of all achievable separation distances. -/
noncomputable def optimalDist (n : ℕ) : ℝ :=
  sSup (achievableDistances n)
 
-- Basic lemma: d=0 is always achievable (trivially)
theorem zero_achievable (n : ℕ) (hn : 0 < n) : (0 : ℝ) ∈ achievableDistances n := by
  simp [achievableDistances, IsPacking, AllInUnitSquare, PairwiseSeparated,
        InUnitSquare, squaredDist]
  -- Use constant configuration: all points at origin
  exact ⟨fun _ => ⟨0, 0⟩, fun i => by simp [InUnitSquare], fun i j _ => by simp [squaredDist]⟩
 
end ErdosAtlas.CirclePacking
 

