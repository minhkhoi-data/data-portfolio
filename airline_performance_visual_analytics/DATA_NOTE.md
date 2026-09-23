# Data Note

## Source Context

This project analyses Australian domestic airline punctuality and reliability data associated with the **Bureau of Infrastructure and Transport Research Economics (BITRE)** airline on-time performance reporting program.

Reference:

- Bureau of Infrastructure and Transport Research Economics, *Airline on-time performance - Monthly reports and time series data*
- https://www.bitre.gov.au/resource/aviation/airline-time-performance-monthly-reports-and-time-series-data

The original Excel workbook was the project input used for this analysis. It is not redistributed in the public portfolio because the coursework wrapper did not provide explicit redistribution permission. The repository does **not** claim ownership of the underlying source data.

## Bundled Files

```text
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

Source-data ownership and redistribution rights remain with BITRE and any applicable source terms. The code, documentation, transformation logic, and portfolio presentation in this repository are separate from ownership of the underlying aviation data. Processed analytical CSVs are retained for inspection; the coursework-packaged raw workbook is deliberately excluded.
