
-- ErdosAtlas/Basic.lean — Root module for ErdosAtlas library
--
-- REPAIR V3 (conflict fix):
--   PROBLEM: Previously imported both ErdosAtlas.Geometry.Point (structure)
--     AND ErdosAtlas.Geometry.Basic (which had def Point := Fin 2 → ℝ).
--     This caused Point type conflicts throughout the library.
--   FIX: Geometry.Basic now re-exports Point/UnitSquare/Distance,
--     so we only need to import Geometry.Basic here.
--     No direct import of Geometry.Point/Distance/UnitSquare needed.
--
--   Import order matters for Lean 4:
--     Geometry.Basic → re-exports Point, UnitSquare, Distance
--     CirclePacking.Definitions → uses Geometry types
--     CirclePacking.N10 → uses Definitions
--     CirclePacking.Certificate → uses Definitions
--     Problems.SquarePacking → uses Definitions
--     Audit.Axioms → uses N10 (imported last to avoid cycles)
 
import ErdosAtlas.Geometry.Basic
import ErdosAtlas.CirclePacking.Definitions
import ErdosAtlas.CirclePacking.N10
import ErdosAtlas.CirclePacking.Certificate
import ErdosAtlas.Problems.SquarePacking
import ErdosAtlas.Audit.Axioms
 
