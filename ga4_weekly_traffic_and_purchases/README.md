# GA4 Weekly Traffic & Purchase Reporting

**SQL / SQLite · Public GA4 sample · Weekly reporting**

How did website traffic and the share of sessions with a recorded purchase change week by week? The [weekly KPI report](results/weekly_kpis.csv) covers 360,129 observed sessions, including 4,848 sessions with at least one recorded purchase (1.35% overall).

## What the report shows

- The week starting 7 December 2020 recorded the most sessions (38,729) and the highest session purchase rate (1.99%) among the complete weeks in this snapshot.
- The week starting 4 January 2021 recorded 29,029 sessions and a 0.56% session purchase rate, the lowest among complete weeks. These figures describe the observed sample. They do not identify the cause of the change.
- Between the weeks starting 2 and 9 November 2020, the session purchase rate rose from 1.00% to 1.52%, a change of 0.52 percentage points. See the [week-over-week comparison](results/weekly_comparison.csv).

## Metrics

| Metric | Definition |
| --- | --- |
| Week start | Monday of the week containing the session date. The session date is the source property's calendar date of its first observed event. |
| Total sessions | Count of session rows in that week. Each session ID occurs once. |
| Sessions with a purchase | Sessions with at least one recorded purchase event. Multiple purchase events in one session count once. |
| Session purchase rate | Sessions with a purchase divided by total sessions, expressed as a percentage. |
| Week-over-week change | Current session purchase rate minus the previous week's rate, in percentage points. The difference uses unrounded rates. |

The observed period is 1 November 2020 to 31 January 2021. The first row is labelled 26 October because that is the Monday of the first week. It contains only 1 November and should be excluded from full-week comparisons. The data describes tracked sessions in an obfuscated sample. Purchase events do not establish a count of unique orders.

## How it works

[weekly_report.sql](sql/weekly_report.sql) joins sessions to the calendar by date, then groups by week and computes the three metrics. [checks.sql](sql/checks.sql) groups purchase events by session before joining them back to the session table. It checks that every session date maps to the calendar, all purchase events map to sessions, and the purchase flags agree with the event data. The runner also checks that the weekly totals reconcile to the inputs.

[weekly_comparison.sql](sql/weekly_comparison.sql) adds one follow-up question: did the rate rise or fall from the previous week? It starts from the calendar, keeps only weeks with seven covered dates using `HAVING`, and uses `LAG` to read the previous week's rate. A date check ensures the comparison uses consecutive weeks. The first complete week has no prior complete week, so its comparison fields are blank. A week with zero sessions has no purchase rate.

## Open in DBeaver

1. Extract the project ZIP. In DBeaver, create a SQLite connection and set **Path** to `data/ga4_weekly.sqlite` inside this folder.
2. Select **Test Connection**, then **Finish**. Download the SQLite driver if prompted.
3. Open [weekly_report.sql](sql/weekly_report.sql) in the SQL Editor on that connection and execute the statement. The output should match [weekly_kpis.csv](results/weekly_kpis.csv).
4. Run [weekly_comparison.sql](sql/weekly_comparison.sql) on the same connection to reproduce [weekly_comparison.csv](results/weekly_comparison.csv).

The SQLite file already contains `fact_sessions`, `dim_date` and `fact_purchases` with the columns used by the SQL. No CSV import or Python setup is needed for this route.

## Rebuild the CSV report

The prepared inputs are included in `data/audited/`:

- `fact_sessions.csv` — one row per session
- `dim_date.csv` — one row per calendar date
- `fact_purchases.csv` — one row per recorded purchase event

From this project folder, run:

```powershell
python run.py
```

The runner uses Python 3.10 or later and its standard SQLite module. It loads the bundled CSVs into a temporary database, runs the checks and writes `results/weekly_kpis.csv` and `results/weekly_comparison.csv`. The preloaded database is provided for use in DBeaver. The `data/` folder is ignored by Git for public repository use.

## Source and contribution

The prepared inputs come from the same snapshot as the accompanying GA4 cohort and Power BI projects. They originate from the [Google GA4 public ecommerce sample](https://developers.google.com/analytics/bigquery/web-ecommerce-demo-dataset) via the [Kaggle flattened mirror](https://www.kaggle.com/datasets/hashiromer/ga4-merchandise-store-flattened-bigquery). This project starts at the prepared session, calendar and purchase tables.

AI drafted and checked the SQL, runner and documentation.
