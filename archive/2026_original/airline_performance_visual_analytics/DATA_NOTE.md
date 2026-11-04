# Data Note

## Source Context

This project analyses Australian domestic airline punctuality and reliability data associated with the **Bureau of Infrastructure and Transport Research Economics (BITRE)** airline on-time performance reporting program.

Reference:

- Bureau of Infrastructure and Transport Research Economics, *Airline on-time performance - Monthly reports and time series data*
- https://www.bitre.gov.au/resource/aviation/airline-time-performance-monthly-reports-and-time-series-data

The original coursework-provided Excel workbook is included in this repository because it is the direct input used by the R ingestion pipeline and supports end-to-end reproducibility. The repository does **not** claim ownership of the underlying aviation data.

## Bundled Files

```text
data/raw/Dataset Assignment 2.xlsx
data/raw/README.md
data/processed/airline_performance_clean.csv
data/processed/airline_performance_analysis.csv
```

`airline_performance_clean.csv` is produced by the cleaning stage.

`airline_performance_analysis.csv` is produced by the feature-engineering stage and is the datasource used by the Tableau workbook.

## Analytical Coverage

The final analytical layer covers:

- January 2010 to February 2024
- 170 monthly periods
- 80,972 observations
- 42 physical airports
- 155 route labels
- 12 standardised airline labels

## Transformation Notes

The reproducible R pipeline:

1. audits workbook sheets and duplicate coverage;
2. excludes duplicated source coverage where necessary;
3. removes non-data records;
4. standardises column names and airline labels;
5. converts dates and operational measures to consistent types;
6. creates reusable analytical levels and temporal fields;
7. calculates weighted KPIs from underlying flight counts;
8. validates calculated percentages against source values.

See the four R Markdown scripts under `scripts/` for the executable transformation logic.

## Redistribution and Attribution

The underlying aviation data are attributed to BITRE and remain subject to any applicable source terms. The code, documentation, transformation logic, and portfolio presentation in this repository are separate from ownership of the underlying data. The coursework-provided raw workbook and processed analytical CSVs are included to make the analytical workflow inspectable and reproducible.
