 
-- ErdosAtlas/Geometry/UnitSquare.lean
-- Definition of the unit square [0,1]² and membership predicate.
 
import ErdosAtlas.Geometry.Point
import Mathlib.Data.Real.Basic
 
namespace ErdosAtlas.Geometry
 
/-- A point lies inside the closed unit square [0,1]². -/
def InUnitSquare (p : Point) : Prop :=
  0 ≤ p.x ∧ p.x ≤ 1 ∧ 0 ≤ p.y ∧ p.y ≤ 1
 
/-- All n points lie inside the unit square. -/
def AllInUnitSquare {n : ℕ} (pts : Fin n → Point) : Prop :=
  ∀ i : Fin n, InUnitSquare (pts i)
 
theorem inUnitSquare_x_nonneg {p : Point} (h : InUnitSquare p) : 0 ≤ p.x :=
  h.1
 
theorem inUnitSquare_x_le_one {p : Point} (h : InUnitSquare p) : p.x ≤ 1 :=
  h.2.1
 
theorem inUnitSquare_y_nonneg {p : Point} (h : InUnitSquare p) : 0 ≤ p.y :=
  h.2.2.1
 
theorem inUnitSquare_y_le_one {p : Point} (h : InUnitSquare p) : p.y ≤ 1 :=
  h.2.2.2
 
end ErdosAtlas.Geometry
 
