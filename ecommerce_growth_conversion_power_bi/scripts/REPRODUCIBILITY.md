# Reproducibility Notes

## Bundled synthetic dataset

The repository includes the final deterministic CSV tables used by the Power BI model.

Reference totals:

- sessions: 75,237
- users: 32,000
- transactions: 4,737
- revenue: $217,478.50

Run:

```bash
python validate_dataset.py
```

from the `scripts/` directory, or provide the script with the project path as required by your local environment.

The validator checks the distributed data and reconciliation rules.

## Why bundle the data?

The project should be reviewable without requiring:

- a Google Cloud billing account
- BigQuery permissions
- an API key
- a private analytics export

The `sql/` folder documents a separate pathway using Google's public GA4 Merchandise Store sample dataset.

## Power BI reproducibility

Open:

```text
../powerbi/Ecommerce_Growth_Conversion_Analytics.pbip
```

in Power BI Desktop and select **Refresh**.

The final runtime verification confirmed that the PBIP opens, refreshes, renders all five pages, and responds to slicer interactions.

Local `.pbi/` folders are Power BI Desktop workspace/cache artifacts and are intentionally excluded from version control.
