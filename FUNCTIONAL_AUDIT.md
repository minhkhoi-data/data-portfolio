# Functional Audit

**Portfolio status:** 8/8 projects functionally verified  
**Verification date:** 23 September 2026

This document records the final runtime verification status of the portfolio. It is intended as a technical audit trail, not as a replacement for each project's README.

---

## Summary

| Project | Primary Tool | Functional Status | Verification |
|---|---|---:|---|
| E-commerce Customer Segmentation & Retention | Python | PASS | Notebook executed end-to-end |
| Marketing Campaign Funnel & Channel Performance | Python | PASS | Notebook executed end-to-end |
| Commercial & CRM Operations Analysis | Excel | PASS | Workbook opened, formulas recalculated, dashboard verified |
| E-commerce Growth & Conversion Analytics | Power BI | PASS | PBIP opened, refreshed, visuals and slicers verified |
| Supervised Learning — Regression & Classification | R | PASS | R Markdown knitted successfully to PDF |
| Insurance Risk Segmentation | PostgreSQL | PASS | Schema setup, CSV import, analytical pipeline and outputs verified |
| Product Affinity & Co-Purchase Network Analysis | Python | PASS | Notebook executed end-to-end |
| Australian Airline Performance Visual Analytics | R + Tableau | PASS | Four R Markdown stages knitted; Tableau datasource and worksheets verified |

---

## 1. E-commerce Customer Segmentation & Retention Analysis

**Status: PASS**

Verification completed by executing the notebook from top to bottom.

Runtime checks:
- 22/22 code cells executed successfully.
- No execution errors.
- Source data loaded through project-relative paths.
- Reproduced approximately **$17.37M revenue**.
- Reproduced **5,878 customers**.
- Reproduced **36,969 orders**.
- Reproduced **4,631 products**.
- RFM segmentation outputs rendered successfully.

The source dataset is stored as a compressed `.csv.gz` file so the project remains suitable for GitHub while remaining directly readable by pandas.

---

## 2. Marketing Campaign Funnel & Channel Performance

**Status: PASS**

Verification completed by executing the notebook from top to bottom.

Runtime checks:
- 28/28 code cells executed successfully.
- No execution errors.
- Source CSV loaded through project-relative paths.
- Dataset contains **10,000 campaign records**.
- Overall CTR reproduced at approximately **5.48%**.
- Funnel, channel and campaign KPI outputs rendered successfully.

---

## 3. Commercial & CRM Operations Analysis

**Status: PASS**

The workbook was opened and tested in Microsoft Excel.

Verified:
- Workbook opens without corruption or repair prompts.
- CRM source data load correctly.
- Formula-driven derived fields calculate correctly.
- Channel normalisation and product mapping work after recalculation.
- Rep Region and Team lookups return valid values.
- No visible `#REF!`, `#DIV/0!`, `#VALUE!`, `#NAME?` or `#N/A` errors remain.
- Dashboard KPIs calculate correctly.
- All four management charts display correctly:
  - Sales Funnel by Stage
  - Won Revenue by Channel
  - Monthly Won Revenue Trend
  - Won Revenue vs Target by Sales Rep

Verified headline outputs include:
- Won Revenue: **$9,775,630**
- Open Pipeline: **$13,011,200**
- Weighted Pipeline: **$7,830,015**
- Win Rate: **26.0%**
- Average Won Deal: **$27,079**
- Stale Open Leads: **358**

Compatibility-related lookup formulas were standardised using `VLOOKUP` where required.

---

## 4. E-commerce Growth & Conversion Analytics

**Status: PASS**

The PBIP project was opened and tested in Power BI Desktop.

Verified:
- PBIP project opens successfully.
- Data model and relationships load correctly.
- Refresh completes successfully.
- Report pages render without broken visuals.
- Slicers and filter interactions work.
- No missing datasource or missing-field errors were observed.

Verified model totals:
- Sessions: **75,237**
- Users: **32,000**
- Transactions: **4,737**
- Revenue: **$217,478.50**
- Session conversion rate: approximately **6.30%**
- AOV: approximately **$45.91**

Local `.pbi` workspace/cache files are not required for distribution and should remain excluded from version control.

---

## 5. Supervised Learning — Regression & Classification

**Status: PASS**

The R Markdown analysis was knitted successfully to PDF after installing the required LaTeX environment.

Verified:
- Required datasets resolve through relative paths.
- Regression workflow executes.
- Model diagnostics execute.
- Cross-validation executes.
- Logistic-regression classification workflow executes.
- ROC/AUC evaluation executes.
- Threshold comparison executes.
- Final PDF renders successfully from beginning to end.

Verified classification outputs include:
- Test accuracy at threshold 0.5: approximately **0.736**
- AUC: approximately **0.813**

A fixed seed of **599** is used for reproducibility where random procedures are required.

---

## 6. Insurance Risk Segmentation

**Status: PASS**

The project was tested with PostgreSQL 18 using pgAdmin 4.

Verified workflow:
1. Created the project database.
2. Ran `setup_schema.sql`.
3. Imported `data/insurance.csv` into `raw.insurance`.
4. Ran `insurance_charges_analysis.sql`.
5. Verified final analytical outputs.

Verified row counts:
- Raw: **1,338**
- Clean: **1,338**
- Final analytical dataset: **1,337**

The reduction from 1,338 to 1,337 is caused by removal of one exact duplicate.

Final risk-segmentation queries returned populated ranked tables including:
- risk rank
- age bucket
- BMI bucket
- smoker group
- customer count
- average charges
- median charges
- 90th-percentile charges

---

## 7. Product Affinity & Co-Purchase Network Analysis

**Status: PASS**

Verification completed by executing the notebook from top to bottom.

Runtime checks:
- 38/38 code cells executed successfully.
- No execution errors.
- Source data loaded through project-relative paths.
- Large intermediate files can be regenerated locally.
- Gephi-compatible network exports were produced successfully.

Verified network outputs:
- Focused threshold: **581 nodes / 1,948 edges**
- Broader threshold: **1,653 nodes / 20,065 edges**

---

## 8. Australian Airline Performance Visual Analytics

**Status: PASS**

Both the R pipeline and Tableau workbook were tested.

### R pipeline

All four R Markdown stages knitted successfully:

1. `01_data_audit`
2. `02_data_cleaning`
3. `03_feature_engineering`
4. `04_analysis_findings`

Verified pipeline:
- Raw workbook read successfully.
- Multi-sheet data combined.
- Clean dataset exported successfully.
- Analysis dataset exported successfully.
- Analytical findings executed successfully.

Verified data outputs:
- Rows before cleaning: **80,977**
- Rows after cleaning: **80,972**
- Analysis dataset: **80,972 rows**
- Analysis period: **2010-01 to 2024-02**
- Analysis levels:
  - Airline: **1,174**
  - Airline Route: **59,472**
  - Network: **170**
  - Route: **20,156**
- Duplicate analytical keys found: **0**

### Tableau

Verified:
- Workbook opens successfully.
- Datasource resolves using the project-relative path:
  `../data/processed/airline_performance_analysis.csv`
- Tableau does not require manual datasource relocation.
- Worksheets render successfully.
- Calculated fields and filters work.
- Network trend, cancellation trend, geographic map, heatmaps, route scatter and airline comparison views load correctly.

---

## Repository-Level Functional Checks

Verified across the repository:
- Eight project folders are present at the repository root.
- Project READMEs are directly accessible from the root README.
- Python notebooks use portable project-relative paths.
- R analyses use project-relative paths.
- Tableau uses a relative datasource path.
- PostgreSQL setup and analysis scripts are separated clearly.
- Required reproducibility datasets are bundled where redistribution is appropriate.
- Large reproducible intermediate files are excluded where they can be regenerated.
- Repository archive integrity was checked successfully.

---

## Final Functional Verdict

**8/8 projects: FULL FUNCTIONAL PASS**

At this point, further work should focus on:
- documentation consistency
- privacy/metadata cleanup
- dataset attribution
- GitHub presentation
- visual polish

Core project logic should not be changed unless a new reproducible functional defect is discovered.
