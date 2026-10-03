 
-- ErdosAtlas/Geometry/Distance.lean
-- Squared and Euclidean distance between two points.
-- Uses squared distance to avoid noncomputable sqrt where possible.
 
import ErdosAtlas.Geometry.Point
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Data.Real.Sqrt
 
namespace ErdosAtlas.Geometry
 
/-- Squared Euclidean distance between two points (avoids sqrt). -/
def squaredDist (p q : Point) : ℝ :=
  (p.x - q.x) ^ 2 + (p.y - q.y) ^ 2
 
/-- Euclidean distance between two points. -/
noncomputable def dist2D (p q : Point) : ℝ :=
  Real.sqrt (squaredDist p q)
 
-- Basic properties
theorem squaredDist_nonneg (p q : Point) : 0 ≤ squaredDist p q := by
  unfold squaredDist
  positivity
 
theorem squaredDist_self (p : Point) : squaredDist p p = 0 := by
  simp [squaredDist]
 
theorem squaredDist_comm (p q : Point) : squaredDist p q = squaredDist q p := by
  simp [squaredDist]; ring
 
theorem dist2D_nonneg (p q : Point) : 0 ≤ dist2D p q :=
  Real.sqrt_nonneg _
 
theorem dist2D_self (p : Point) : dist2D p p = 0 := by
  simp [dist2D, squaredDist_self]
 
theorem dist2D_comm (p q : Point) : dist2D p q = dist2D q p := by
  simp [dist2D, squaredDist_comm]
 
/-- Pairwise separation: all pairs of n points are at least d apart (using squared distance). -/
def PairwiseSeparated {n : ℕ} (pts : Fin n → Point) (d : ℝ) : Prop :=
  ∀ i j : Fin n, i ≠ j → d ^ 2 ≤ squaredDist (pts i) (pts j)
 
end ErdosAtlas.Geometry
 

