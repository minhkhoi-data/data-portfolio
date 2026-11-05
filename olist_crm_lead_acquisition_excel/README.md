# Olist CRM | Lead Acquisition by Source

An Excel project that answers a CRM reporting question: which sources brought in the most sampled marketing-qualified leads, and how many leads had a recorded win?

## Open the workbook

Open `Olist_CRM_Lead_Acquisition.xlsx` in Microsoft 365 or Excel 2021 or later for `XLOOKUP`. The data and calculations are embedded. The two original CSVs are included in `data/` for comparison.

| Sheet | What to look at |
|---|---|
| **Report** | KPIs, source summary, one chart, a PivotTable and reconciliation checks. |
| **Leads** | One row per sampled lead. Columns A:C hold source fields. Columns D:G show the lookup, closing days, source label and win flag. |
| **Won_Deals** | One row per recorded win. The lead ID connects this sheet to **Leads**. |

## Recreate the report

1. Check that lead IDs are unique on both input sheets before using an exact `XLOOKUP` to bring the won timestamp into **Leads**.
2. Use `IF` to create a win flag and separate missing origins. Keep the literal source label `unknown` as its own group.
3. Use `COUNTIFS` for lead counts and `SUMIFS` for the win flags. Divide wins by leads within each source.
4. Create a PivotTable from `Leads!F6:G8006`. Use **Source** as Rows, **Count of Source** and **Sum of Won flag** as Values. Compare totals with the formula summary. In Excel, refresh the PivotTable after editing the source rows.

The workbook covers the supplied snapshot. If you append rows, expand the formula ranges and PivotTable source to include them.

## What the data shows

- **8,000** sampled leads and **842** recorded wins. The overall recorded won share is **10.5%** rounded to one decimal place.
- Organic search contributed the most leads (**2,296**) and recorded wins (**271**). Paid search recorded **195 wins** across **1,586 leads**.
- Median closing time is **14 calendar days** across **841 valid wins**. One won timestamp precedes first contact, so that lead counts as a recorded win but is excluded from closing-time calculations.

A lead without a matched win has an unobserved outcome. The recorded won share uses the supplied lead snapshot and is descriptive. It cannot establish a final conversion rate or the causal effect of a source. The first-contact dates span 14 June 2017 to 31 May 2018.

## Data source

Olist and collaborators published the anonymized lead and closed-deal files in [Marketing Funnel by Olist](https://www.kaggle.com/datasets/olistbr/marketing-funnel-olist). The supplied source documentation identifies the data licence as [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
