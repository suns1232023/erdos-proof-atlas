# DeepMind Formal Conjectures Bridge

This directory provides compatibility with the Google DeepMind
[formal-conjectures](https://github.com/google-deepmind/formal-conjectures) ecosystem.

## What this is NOT
- A fork of google-deepmind/formal-conjectures
- A claim to reproduce DeepMind's work

## What this IS
- A compatibility layer that can generate DeepMind-compatible metadata
- A bridge for future submission of formally proved theorems

## Usage
```bash
python scripts/export_deepmind.py
```

## Format
Follows DeepMind's conventions:
- Lean 4 + mathlib
- AMS classification
- category metadata
- formal_proof provenance
