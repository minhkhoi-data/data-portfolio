# GA4 Acquisition & Conversion | Power BI

Where does the ecommerce journey lose observed sessions, and how does purchase conversion vary by device and the channel that first acquired the user?

This one-page report uses the Google Merchandise Store GA4 public sample for 1 November 2020 to 31 January 2021. Start with the traffic and purchase KPIs, check the ordered funnel, then use the month slicer to compare patterns by device and first-user channel.

## Open and refresh

1. Extract the entire ZIP and keep the project and `data/` folder together.
2. In Windows, close any open copy of this report and double-click `Open_Report.cmd`. It points Power Query at the included `data/` folder. If the file does not open automatically, use **File → Open** in a current version of Power BI Desktop and select `GA4AcquisitionAndConversion.pbip`.
3. In Power BI Desktop, select **Home → Refresh**. Clear the **Month** slicer for the full-window checks below. Run the opener again after moving the folder.

If Windows blocks the launcher, open the PBIP and use **Transform data → Manage Parameters** to set `DataFolder` to the absolute path to `data/`, then **Close & Apply**. If the PBIP cannot open before setting the path, open `GA4AcquisitionAndConversion.SemanticModel/definition/expressions.tmdl` in a text editor and replace the quoted placeholder path on the first line. Save it before opening the PBIP. Use a normal local folder such as `C:\Portfolio\ga4_acquisition_and_conversion_power_bi\data`.

## Data and model

| Table | What one row means |
| --- | --- |
| `FactSessions` | One observed session. `purchase` marks any observed purchase. The four `ordered_` columns indicate how far the session progressed through the observed event sequence. |
| `FactPurchases` | One recorded purchase event with the source event's date and USD value. |
| `DimDate`, `DimChannel`, `DimDevice` | One date, first-user channel, or device category. Each dimension filters both facts through one-to-many, single-direction relationships. |
| `FunnelStage` | One label and sort order for the chart. A DAX measure picks the corresponding session flag for each label. |

The month slicer filters sessions by session date and revenue by purchase-event date. The `data/` folder contains the CSV inputs to refresh the report. The fact files keep selected columns from the original portfolio's prepared GA4 tables. Event sequencing was done upstream. In Power Query the report loads the six CSVs, promotes headers and sets types.

Source: [Kaggle GA4 mirror](https://www.kaggle.com/datasets/hashiromer/ga4-merchandise-store-flattened-bigquery) of the [Google Analytics BigQuery ecommerce sample](https://developers.google.com/analytics/bigquery/web-ecommerce-demo-dataset). This public, obfuscated historical sample is for descriptive analysis.

## Results and checks

| Scope | Sessions | Sessions with a purchase | Session conversion | Recorded purchase-event revenue |
| --- | ---: | ---: | ---: | ---: |
| Full sample | 360,129 | 4,848 | 1.35% | $362,165 |
| December 2020 only | 133,351 | 2,115 | 1.59% | $160,555 |

- **Ordered journey.** 77,020 sessions viewed a product, 14,380 reached cart in order, 5,187 reached checkout in order and 2,778 reached purchase in order. View-to-cart was 18.67%, the lowest step-to-step rate among the four commerce stages. Investigate usability and tracking coverage before calling missing events abandonment.
- **Overall purchase activity.** The 4,848 purchase sessions include 2,070 sessions without the complete recorded sequence. The funnel and the overall KPI answer different questions.
- **Segment comparisons.** Mobile conversion was 1.39% versus 1.32% on desktop. Referral was 2.03% from 28,849 sessions, and 119,526 sessions had an unknown or masked first-user channel. Use the charts to identify where to investigate. First-user channel describes initial acquisition and gives no campaign-spend or causal evidence.
- **Revenue.** $362,165 is the sum of recorded purchase-event values. The sample does not establish verified order counts, net sales or experiment outcomes.

## Rebuild it yourself

1. Import the CSVs in Power Query. Keep session identifiers as text, dates as dates, flags as whole numbers and revenue as fixed decimal. Check that session IDs are unique and the ordered flags are 0 or 1.
2. In Model view, connect the date, channel and device lookups to the two fact tables. Check the direction runs from the lookup to the fact. Leave `FunnelStage` disconnected.
3. Write the session measures first. `COUNTROWS` works because one row is one session. `CALCULATE` filters to sessions with `purchase = 1`. `DIVIDE` computes the conversion rate within the current slicer context. Add `SUM` for revenue. For the funnel, use `SELECTEDVALUE` and `SWITCH` to sum the relevant 0/1 flag for each stage.
4. Build the KPI cards, the funnel, channel and device comparisons, a daily sessions trend and the month slicer. Check the full sample, filter to December and compare the figures above, then clear the slicer.

The supplied CSV totals, keys and filter-slice benchmarks were checked outside Desktop. Native opening, refresh and report rendering still need the Windows Desktop check above.
