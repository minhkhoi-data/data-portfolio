# Dataset attribution and local provenance

**Official source:** Chen, D. (2012). *Online Retail II* [Dataset]. UCI Machine Learning Repository. DOI: [10.24432/C5CG6D](https://doi.org/10.24432/C5CG6D). [Dataset page](https://archive.ics.uci.edu/dataset/502/online+retail+ii). UCI lists the data under **CC BY 4.0**; retain attribution and identify adaptations when sharing.

UCI describes transactions for one UK registered non-store retailer, mainly selling giftware, with many wholesale customers. Coverage: 1 December 2009 to 9 December 2011; 1,067,371 rows; unit prices in sterling (GBP). These facts describe the source, not current business conditions. The original workbook contains two yearly sheets.

The uploaded project contained `data/online_retail_II.csv.gz`; its original download/conversion date was not recorded. The old notebook cited a Kaggle mirror. During this remaster, the official UCI workbook was downloaded and compared with this local CSV, in row order, across all eight fields. Seven fields matched after identifier/timestamp normalization and a numeric tolerance of 1e-10. Four Description cells were numeric in Excel and the same digits as text in CSV; after treating descriptions as text there is no substantive difference. This supports the local dataset attribution; no claim is made about who originally converted/downloaded it.

[audit/source_verification.json](audit/source_verification.json) records the original workbook SHA-256, sheet names, comparison procedure and the four type differences. `outputs/run_summary.json` records the bundled gzip SHA-256. No source rows were overwritten. Prepared purchase/credit files, deduplication and metrics are this project's adaptations.

Description can be missing or contain numeric labels; it is retained but not used to infer customer behaviour. Public source IDs and countries are retained without names/contact data. No email addresses, permission records or private company data are included. The UCI workbook was used for verification and is not duplicated inside this deliverable.

On 2026-10-07 the official UCI package was downloaded again and all 1,067,371 bundled rows, in original order across all eight fields, compared with its workbook. The original workbook SHA-256 matched the earlier record. Zero mismatches remain after the documented numeric/text normalization; the four numeric Description cells are text-equivalent. [Current source recheck](audit/source_reverification.json) records acquisition time, URL, hashes, sheets, tolerance and exact coverage. The date of the original CSV conversion remains unknown.

## Standalone takeover source check — 2026-10-15

The official UCI ZIP was downloaded again for this audit. The new workbook SHA-256 is `bcbe73b35f5b7babf197fb0cb983a11f5d9ff929078d4aa53d171b1f2df2e980`, matching the earlier workbook. A new streaming comparison checked all 1,067,371 rows in source order and all eight fields against the bundled CSV: zero mismatches after the documented blank/text/timestamp normalization and numeric absolute tolerance of 1e-10. Four numeric Description cells are text-equivalent; row indices and exact hashes are in `audit/takeover_source_verification.json`. This is a new full comparison, not a relabelled historical result.

To repeat this optional source check, download and extract the official UCI workbook separately, install `requirements-verification.txt`, then run:

```bash
python analysis/verify_official_source.py --workbook /path/to/online_retail_II.xlsx
```

The source-check script does not download data or alter the bundled input. The official workbook is omitted from the ZIP to avoid duplicating the already bundled CSV. Historical conversion ownership/date remain unknown.
