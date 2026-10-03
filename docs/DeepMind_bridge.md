# DeepMind Formal Conjectures Bridge

## What this is

A compatibility layer for the Google DeepMind
[formal-conjectures](https://github.com/google-deepmind/formal-conjectures) ecosystem.

## What this is NOT

- A fork of google-deepmind/formal-conjectures
- A claim to reproduce DeepMind's work

## Usage

```bash
python scripts/export_deepmind.py
```

## Output format

```yaml
problem_id: erdos_circle_packing_n10
category: geometry
ams: [52]
lean_theorem: circlePacking10MinDistBound
lean_file: ErdosAtlas/CirclePacking/N10.lean
formal_status: STATEMENT_FORMALIZED
computational_status: SYMBOLICALLY_CERTIFIED
```

## Future

If a theorem is formally proved (L5), the bridge will record:
- exact Lean file
- git commit
- lake build verification
