# Australian Airline Punctuality & Reliability Visual Analytics

**Tools:** R, R Markdown, Tableau  
**Data:** Australian domestic airline on-time performance, January 2010–February 2024  
**Focus:** weighted KPI design, time-series analysis, airport/route/airline comparison, visual analytics

## Business Question

How do Australian domestic airlines, airports, and routes differ in punctuality, cancellation reliability, and operational scale, and what patterns become visible when those measures are analysed together?

## Workflow

R is used for:

1. workbook and worksheet auditing;
2. duplicate and missing-value validation;
3. multi-sheet integration and airline-name standardisation;
4. analytical-layer creation;
5. weighted KPI calculation and validation;
6. reproducible findings analysis.

Tableau is used for geographic, temporal, route, airport, and airline visual exploration.

## Selected Findings

### Network performance

- Weighted Departure OTP: **81.0%**
- Weighted Arrival OTP: **79.9%**
- Overall Cancellation Rate: **2.62%**

Large cancellation spikes occurred in **April 2020 (33.6%)** and **July 2021 (31.8%)**.

The weakest monthly network punctuality in the analysis was **July 2022**:

- Departure OTP: **54.0%**
- Arrival OTP: **55.0%**

### Airport concentration

Sydney, Melbourne, and Brisbane together accounted for **56.6% of departure flight activity**.

### Recovery pattern

- From 2021 to 2022, all **36 comparable airports** had lower Arrival OTP.
- From 2022 to 2023, **29 of 36** comparable airports improved.

### 2023 route example

The highest-volume route was **Melbourne–Sydney**:

- Sectors flown: **24,222**
- Departure OTP: **72.5%**
- Arrival OTP: **67.6%**
- Cancellation rate: **8.95%**

The analysis shows why punctuality should be interpreted together with cancellation reliability and traffic volume rather than using a single ranking metric.

## Visual Outputs

- Geographic airport performance
- Network OTP trend
- Network cancellation trend
- Airport-year heatmap
- Airport-month heatmap
- Route-performance scatterplot
- Airline performance comparison

See the [`figures`](./figures) directory for exported views and [`tableau`](./tableau) for the workbook.

## Repository Structure

```text
airline_performance_visual_analytics/
├── scripts/
│   ├── 01_data_audit/
│   ├── 02_data_cleaning/
│   ├── 03_feature_engineering/
│   └── 04_analysis_findings/
├── tableau/
├── figures/
├── report/
│   └── analysis_and_insights.pdf
└── README.md
```

## Limitations

- Operational punctuality data do not explain causal reasons for delays or cancellations.
- One-year monthly comparisons should not be treated as proof of recurring seasonality.
- Weighted KPIs are sensitive to route/airport traffic composition, so volume should remain visible alongside percentages.
