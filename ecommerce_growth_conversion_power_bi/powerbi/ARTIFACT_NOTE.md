# Power BI Artifact

Main project file:

```text
Ecommerce_Growth_Conversion_Analytics.pbip
```

This is a portable Power BI Project (PBIP).

The project contains:
- a TMDL semantic model
- three fact tables
- five shared dimensions
- one disconnected funnel-stage helper table
- a dedicated measures table
- 13 relationships
- 31 DAX measures
- five report pages

The eight bundled analytical tables are stored in the semantic-model definition, so the report does not require a machine-specific CSV path when opened.

## Runtime verification

The project was opened in Power BI Desktop, refreshed successfully, and tested with slicer interactions.

Verified headline totals:
- Sessions: 75,237
- Users: 32,000
- Transactions: 4,737
- Revenue: $217,478.50

## Local Power BI workspace files

Power BI Desktop may recreate `.pbi/` folders containing local settings and cache files.

These files are intentionally excluded from version control:

```text
**/.pbi/
```

They are not required to reproduce the report and should not be distributed as part of the public portfolio.

The `screenshots/` folder contains Power BI Desktop captures of the report pages and model view.
