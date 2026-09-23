# Publishing Checklist

## Automated gates

Run from the repository root:

```bash
python scripts/audit_portfolio.py
```

Publication is blocked unless the command ends with:

```text
PASS — portfolio publication audit completed
```

The audit checks project scope, duplicate/cache paths, GitHub file-size limits, local links, machine-specific paths, Python syntax, notebook error outputs, all flagship runtime pipelines, metric reconciliation, experiment SRM/balance/inference/guardrails, and the root recruiter path.

## Native application spot checks

Automated checks cannot replace application rendering. Before publishing a new native-file revision:

1. Open the Power BI `.pbip`, refresh, and compare headline totals with `docs/QA_CHECKS.md`.
2. Open the Excel workbook and confirm that no cells display formula errors.
3. Open the Tableau workbook and confirm that its relative processed-CSV connection resolves.

The current native files were not modified during the retention/experimentation remaster. Their previously verified screenshots and analytical outputs remain bundled.

## Public-data rule

- Do not restore local Power BI cache folders or nested `FINAL` copies.
- Do not add coursework-packaged raw data without explicit redistribution permission.
- Label every synthetic result as synthetic.
- Re-run the audit after changing code, data, paths, metrics, or documentation.
