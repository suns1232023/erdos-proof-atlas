-- ErdosAtlas/Geometry/Point.lean
-- Definition of a 2D point using exact real numbers.
--
-- REPAIR V2 (per reviewer):
--   Use `structure Point` with fields x y : ℝ
--   NOT Fin 2 → Float (which was the placeholder)
--
-- REPAIR V3 (compiler fix):
--   Removed `deriving Repr`.
--   ℝ (Real) is noncomputable. Real.instRepr is marked `unsafe` in Lean 4.
--   Deriving Repr for a structure containing ℝ causes LCNF compiler panic:
--     (kernel) invalid declaration, it uses unsafe declaration 'Real.instRepr'
--     PANIC at Lean.Compiler.LCNF.ExplicitBoxing
--   Point is used only for formal reasoning, not runtime printing.

import Mathlib.Data.Real.Basic

namespace ErdosAtlas.Geometry

/-- A point in the 2D Euclidean plane with exact real coordinates. -/
structure Point where
  x : ℝ
  y : ℝ

end ErdosAtlas.Geometry
