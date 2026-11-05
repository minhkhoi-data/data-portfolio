# GA4 Weekly Traffic & Purchase Reporting

**SQL / SQLite · Public GA4 sample · Weekly reporting**

How did website traffic and the share of sessions with a recorded purchase change week by week? The [weekly KPI report](results/weekly_kpis.csv) covers 360,129 observed sessions, including 4,848 sessions with at least one recorded purchase (1.35% overall).

## What the report shows

- The week starting 7 December 2020 recorded the most sessions (38,729) and the highest session purchase rate (1.99%) among the complete weeks in this snapshot.
- The week starting 4 January 2021 recorded 29,029 sessions and a 0.56% session purchase rate, the lowest among complete weeks. These figures describe the observed sample. They do not identify the cause of the change.

## Metrics

| Metric | Definition |
| --- | --- |
| Week start | Monday of the week containing the session date. The session date is the source property's calendar date of its first observed event. |
| Total sessions | Count of session rows in that week. Each session ID occurs once. |
| Sessions with a purchase | Sessions with at least one recorded purchase event. Multiple purchase events in one session count once. |
| Session purchase rate | Sessions with a purchase divided by total sessions, expressed as a percentage. |

The observed period is 1 November 2020 to 31 January 2021. The first row is labelled 26 October because that is the Monday of the first week. It contains only 1 November and should be excluded from full-week comparisons. The data describes tracked sessions in an obfuscated sample. Purchase events do not establish a count of unique orders.

## How it works

[weekly_report.sql](sql/weekly_report.sql) joins sessions to the calendar by date, then groups by week and computes the three metrics. [checks.sql](sql/checks.sql) groups purchase events by session before joining them back to the session table. It checks that every session date maps to the calendar, all purchase events map to sessions, and the purchase flags agree with the event data. The runner also checks that the weekly totals reconcile to the inputs.

## Run locally

Requires Python 3.10 or later with its standard SQLite module. No pip packages are needed. From this project folder, point the runner to the original cohort project's extracted `data/audited` folder. It needs these three prepared files:

- `fact_sessions.csv` — one row per session
- `dim_date.csv` — one row per calendar date
- `fact_purchases.csv` — one row per recorded purchase event

```powershell
python run.py "..\ecommerce_customer_cohort_sql\data\audited"
```

Use the actual input path if your folder layout differs. The runner loads the inputs into a temporary in-memory SQLite database, runs the checks and writes `results/weekly_kpis.csv`. The prepared input CSVs are kept separately. The aggregate report is included for browsing.

## Source and contribution

The prepared inputs come from the same snapshot as the accompanying GA4 cohort and Power BI projects. They originate from the [Google GA4 public ecommerce sample](https://developers.google.com/analytics/bigquery/web-ecommerce-demo-dataset) via the [Kaggle flattened mirror](https://www.kaggle.com/datasets/hashiromer/ga4-merchandise-store-flattened-bigquery). This project starts at the prepared session, calendar and purchase tables.

AI drafted and checked the SQL, runner and documentation.
