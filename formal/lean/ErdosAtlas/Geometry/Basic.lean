
-- ErdosAtlas/Geometry/Basic.lean
-- Core geometric definitions for the square packing formalization.
--
-- Formal level: L2 (DEFINITIONS_FORMALIZED)
--
-- REPAIR NOTE (P1 Fix):
--   Replaced Float-based placeholder with mathematically correct ℝ-based definitions.
--   These definitions form the foundation for the N=10 packing theorem.
 
import Mathlib.Analysis.InnerProductSpace.Basic
import Mathlib.Topology.MetricSpace.Basic
import Mathlib.Data.Real.Basic
 
namespace ErdosAtlas.Geometry
 
-- ---------------------------------------------------------------------------
-- Layer 1: Point in 2D Euclidean space
-- ---------------------------------------------------------------------------
 
/-- A point in the 2D plane, represented as a function Fin 2 → ℝ. -/
def Point : Type := Fin 2 → ℝ
 
/-- The x-coordinate of a point. -/
def Point.x (p : Point) : ℝ := p 0
 
/-- The y-coordinate of a point. -/
def Point.y (p : Point) : ℝ := p 1
 
-- ---------------------------------------------------------------------------
-- Layer 2: Unit square [0,1] × [0,1]
-- ---------------------------------------------------------------------------
 
/-- A point lies inside the closed unit square [0,1]². -/
def InUnitSquare (p : Point) : Prop :=
  0 ≤ p.x ∧ p.x ≤ 1 ∧ 0 ≤ p.y ∧ p.y ≤ 1
 
-- ---------------------------------------------------------------------------
-- Layer 3: Euclidean distance between two points
-- ---------------------------------------------------------------------------
 
/-- Squared Euclidean distance between two points. -/
def distSq (p q : Point) : ℝ :=
  (p.x - q.x) ^ 2 + (p.y - q.y) ^ 2
 
/-- Euclidean distance between two points. -/
noncomputable def dist2D (p q : Point) : ℝ :=
  Real.sqrt (distSq p q)
 
-- Basic properties of dist2D
theorem dist2D_nonneg (p q : Point) : 0 ≤ dist2D p q :=
  Real.sqrt_nonneg _
 
theorem dist2D_self (p : Point) : dist2D p p = 0 := by
  simp [dist2D, distSq, Point.x, Point.y]
 
theorem dist2D_comm (p q : Point) : dist2D p q = dist2D q p := by
  simp [dist2D, distSq, Point.x, Point.y]
  ring_nf
 
-- ---------------------------------------------------------------------------
-- Layer 4: Pairwise separation
-- ---------------------------------------------------------------------------
 
/-- All pairs of n points are separated by at least distance d. -/
def PairwiseSeparated {n : ℕ} (pts : Fin n → Point) (d : ℝ) : Prop :=
  ∀ i j : Fin n, i ≠ j → d ≤ dist2D (pts i) (pts j)
 
/-- All n points lie inside the unit square. -/
def AllInUnitSquare {n : ℕ} (pts : Fin n → Point) : Prop :=
  ∀ i : Fin n, InUnitSquare (pts i)
 
-- ---------------------------------------------------------------------------
-- Layer 5: Packing configuration
-- ---------------------------------------------------------------------------
 
/-- A valid packing configuration: n points in the unit square
    with pairwise distance at least d. -/
structure PackingConfig (n : ℕ) where
  pts : Fin n → Point
  inSquare : AllInUnitSquare pts
  separated : ∃ d : ℝ, 0 < d ∧ PairwiseSeparated pts d
 
/-- The minimum pairwise distance of a configuration (noncomputable). -/
noncomputable def minPairwiseDist {n : ℕ} (pts : Fin n → Point) : ℝ :=
  sInf { d : ℝ | ∃ i j : Fin n, i ≠ j ∧ d = dist2D (pts i) (pts j) }
 
end ErdosAtlas.Geometry
 

