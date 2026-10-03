
-- Main.lean — ErdosAtlas executable entry point
--
-- REPAIR V5 (case sensitivity fix):
--   PROBLEM: GitHub shows 'main.lean' (lowercase m) but lakefile.toml declares
--     root = "Main" which expects 'Main.lean' (uppercase M).
--     On Linux (case-sensitive filesystem), lake build fails to find Main.lean.
--   FIX: This file must be committed as 'Main.lean' (uppercase M).
--     Run: git mv formal/lean/main.lean formal/lean/Main.lean
--     Then commit and push.
--
-- Note: If both main.lean and Main.lean exist, delete main.lean.
 
import ErdosAtlas.Basic
 
def main : IO Unit := do
  IO.println "Erdős Proof Atlas — Lean 4 build OK"
  IO.println "Formal level: L1 (Statement Formalized)"
  IO.println "Canonical theorem: circlePacking10MinDistBound"
  IO.println "Evidence level: E5 (Symbolically Certified)"
 
