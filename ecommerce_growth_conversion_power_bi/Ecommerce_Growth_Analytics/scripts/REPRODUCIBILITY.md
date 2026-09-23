# Reproducibility Notes

## Bundled demo data

The data files are deterministic and were generated using seed `20260916`.

Reference totals:
- sessions: 75,237
- users: 32,000
- orders: 4,737
- revenue: $217,478.50

Use `validate_dataset.py` to verify the files after cloning or moving the repository.

## Why bundle demo data?

A GitHub portfolio should be runnable without requiring:
- a Google Cloud billing account
- BigQuery permissions
- an API key
- a private export

The `sql/` folder provides the separate official-public-data route.
