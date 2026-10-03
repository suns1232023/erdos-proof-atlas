
-- ErdosAtlas/Geometry/Point.lean
-- Definition of a 2D point using exact real numbers.
--
-- REPAIR V2 (per reviewer):
--   Use `structure Point` with fields x y : ℝ
--   NOT Fin 2 → Float (which was the placeholder)
 
import Mathlib.Data.Real.Basic
 
namespace ErdosAtlas.Geometry
 
/-- A point in the 2D Euclidean plane with exact real coordinates. -/
structure Point where
  x : ℝ
  y : ℝ
  deriving Repr
 
end ErdosAtlas.Geometry
 
