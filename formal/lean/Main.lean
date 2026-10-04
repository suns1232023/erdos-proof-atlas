-- Main.lean -- ErdosAtlas executable entry point
-- Required by [[lean_exe]] name = "Main" root = "Main" in lakefile.toml
-- This file must be named Main.lean (uppercase M) on Linux.
import ErdosAtlas.Basic

def main : IO Unit := do
  IO.println "Erdos Proof Atlas -- Lean 4 build OK"
  IO.println "Formal level: L1 (Statement Formalized)"
  IO.println "Canonical theorem: circlePacking10MinDistBound"
