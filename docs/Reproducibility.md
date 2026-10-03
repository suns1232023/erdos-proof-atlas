# Reproducibility

## Every experiment records

- Git commit hash
- Timestamp UTC
- Python version + dependencies
- Random seed
- Configuration hash

## Reproducibility Guardrails

1. Numerical result cannot overwrite exact result
2. Failed verification cannot generate PASS
3. Missing certificate cannot generate CERTIFIED
4. GitHub Actions success ≠ epistemic status change

## Commands

```bash
make search verify exact certify lean audit report manifest
```
