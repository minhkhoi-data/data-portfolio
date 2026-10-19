# Ecommerce growth and conversion — GA4 remaster

An existing five-page Power BI project remastered against a public Google Merchandise Store GA4 sample mirrored on Kaggle. The bundled source is a public obfuscated Google sample, not AI-generated outcomes; it is not an unaltered production export. Derived tables, DAX, report metadata and documentation were prepared with AI assistance. No claim is made that the author independently wrote every component.

## Open the report

Extract the complete ZIP into a fresh folder and double-click `MO_PROJECT.cmd`. The opener validates eight CSV files, sets the local DataFolder parameter and requests Windows to open `powerbi/MO_GA4_CSV_13_10.pbip`. Click Home → Refresh in Power BI Desktop. All CSVs are included in `data/`; no Kaggle/BigQuery account, Python installation or manual path editing is required to open this snapshot. Keep the complete folder together. Run the opener again after moving the folder, with the project closed in Desktop.

This release uses file-backed CSV partitions instead of compressed data embedded in M expressions. The two support tables are also CSV imports; no calculated partition needs initialization. If the PBIP file association is missing, the opener configures the path first and tells you to use Desktop → File → Open. Desktop opening, M execution, DAX execution and visual rendering of this rebuild remain **NOT VERIFIED** here. The user's one-row Enter Data test succeeded; both prior embedded loaders failed native model creation with the same closed-Stream error. The exact internal engine cause is unestablished.

## Source and scope

- Source: https://www.kaggle.com/datasets/hashiromer/ga4-merchandise-store-flattened-bigquery
- Upstream sample: https://developers.google.com/analytics/bigquery/web-ecommerce-demo-dataset
- Property dates: 2020-11-01 through 2021-01-31.
- Original CSV: 4,295,584 events, 88 columns. Included `data/source/ga4_events.csv.gz`: exact 25-column projection of **all** rows; all source IDs, values and blanks in those columns preserved.
- Original ZIP is not duplicated in this folder. Download URL, original ZIP/CSV SHA-256 and projection SHA-256 are in `data/source/provenance.json`.
- Google describes the source as obfuscated and limits its internal consistency. It is suitable for a scoped public-data analytics portfolio, not audited commerce accounting.
- The uploader labels the mirror MIT; this does not establish additional rights over upstream Google data. Consult upstream terms for redistribution or other uses.

Product SKU rankings, margins, verified order/AOV accounting and observed checkout A/B outcomes are unsupported. The report includes a coverage page, and a future experiment design is clearly separated from results.

## Contents

| Path | Purpose |
| --- | --- |
| powerbi/ | Portable PBIP, semantic model and five report pages |
| data/source/ | All-row source projection, hashes and user-supplied BigQuery controls |
| data/ | Six rebuilt analytical CSV tables |
| scripts/ | Import, deterministic transforms, CSV model generation, opener, documentation and verification |
| outputs/ | CSV results and explicitly labeled Python preview |
| docs/ | Business questions, metric definitions and descriptive findings |
| audit/ | Executed checks and native validation status |
| experiment_design/ | Future test protocol, no observed results |
| sql/ | Independent BigQuery source-profile query |

## Reproduce

Python 3.12 was used with pinned libraries in requirements.txt. From this project folder:

```bash
python -m pip install -r requirements.txt
python scripts/run_all.py
```

Allow roughly 8 GB RAM and several minutes for the full 4.3-million-event rebuild. `run_all.py` validates source hash and controls, writes analytical and support CSV tables, rebuilds the model, updates report bindings, regenerates documentation/preview and runtime manifest, and runs checks. Failure exits nonzero and marks build outputs invalid. Optional external validator arguments are shown by `python scripts/run_all.py --help`; omitted parsers are marked NOT RUN rather than retaining evidence from a prior model. Current parser status is recorded in audit/evidence/build_status.json; historical parser evidence is reused only for identical tested inputs. After a rebuild, run MO_PROJECT.cmd to set the machine-local DataFolder before opening Desktop.

To rebuild the included source projection from the downloaded original archive:

```bash
python scripts/import_source.py --zip /path/to/ga4-merchandise-store-flattened-bigquery.zip
python scripts/run_all.py
```

Use the same published source snapshot and compare the recorded hashes. The existing independent controls intentionally reject a changed source; a genuinely new dataset requires reviewed definitions, controls and mappings rather than blind substitution.

## Verification boundary

Source counts/revenue match the independent BigQuery profile by month. Analytical totals, keys, foreign keys, ordered-event edge cases, CSV schemas/manifest hashes, M types, references and layout bounds are checked programmatically. The model uses short CSV import expressions with one local DataFolder parameter; identifiers remain text and nullable numeric fields remain null. The current opener evidence records configuration tests for paths with spaces and Unicode, relocation, missing/altered CSVs, and repeated configuration; Windows launch remains unverified. Official metadata and grammar checks do not execute Windows M or DAX. See audit/CHECKS.csv and audit/NATIVE_STATUS.md. No old synthetic-data audit result or experiment outcome is carried into this version.

## Standalone audit and independent source-to-fact checks

Read `AUDIT_SUMMARY_VI.md` and `audit/AUDIT_REPORT.md` for the dated takeover result. Full Desktop/DAX and redistribution gates remain separate from analytical correctness. The source projection is unchanged; the takeover corrects `(data deleted)` acquisition values into Unknown / masked.

Optional independent SQL verification uses a temporary disk database, one thread and a 1 GB DuckDB cap:

```bash
python -m pip install -r requirements-verification.txt
python scripts/verify_source_sql.py
```

This scans every bundled event and compares every session and purchase with the delivered facts. It does not execute DAX or authenticate the mirror against a new external download. Source provenance and supplied BigQuery control totals are retained; no fresh BigQuery query is claimed.
