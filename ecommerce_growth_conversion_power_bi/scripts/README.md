# Validation Scripts

The bundled Power BI data are deterministic synthetic portfolio data.

Reference totals:

- Sessions: 75,237
- Users: 32,000
- Transactions: 4,737
- Revenue: $217,478.50

Use:

```text
validate_dataset.py
```

to verify the bundled CSV files after cloning, moving, or repackaging the repository.

The repository does **not** include the original data-generation program. The included validator checks the distributed dataset and key reconciliation rules; it does not regenerate the dataset.

For the alternative public-data pathway using Google's GA4 Merchandise Store sample, see the SQL templates under `../sql/`.
