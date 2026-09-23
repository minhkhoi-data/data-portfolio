# Excel Skills Evidence

This file maps the workbook's main Excel techniques to the sheets and business logic where they are used.

| Skill | Evidence in the workbook |
|---|---|
| `VLOOKUP` | `CRM_Data` source normalisation and product enrichment; `Rep_Performance` region, team and revenue-target lookups |
| `IFERROR` | Lookup fallbacks, ratio protection, sales-cycle calculations and KPI protection |
| `IF` / nested `IF` | Outcome classification, deal segmentation, SLA flag, lead score and forecast category |
| `SUMIFS` | Won revenue, open pipeline, weighted pipeline and monthly revenue |
| `COUNTIFS` | Won/lost deals, rep and channel counts, and monthly win counts |
| `COUNTIF` | Funnel-stage reach, stale opportunities and clean-channel lead volume |
| `TEXT` | Monthly reporting keys |
| `MONTH` / `YEAR` / `ROUNDUP` | Quarter generation |
| Excel Tables | CRM source table and management summary tables |
| Data Validation | Controlled inputs for owner, region, product and company size |
| Conditional Formatting | Stale leads, lead score, weighted pipeline, win rate and target attainment |
| Charts | Sales Funnel by Stage; Won Revenue by Channel; Monthly Won Revenue Trend; Won Revenue vs Target by Sales Rep |
| Dashboard | Six headline KPIs plus four validated management charts |

## Workbook Evidence

The final workbook was opened and recalculated in Microsoft Excel during functional verification.

Validated outputs include:

- Won Revenue: **$9,775,630**
- Open Pipeline: **$13,011,200**
- Weighted Pipeline: **$7,830,015**
- Win Rate: **26.0%**
- Average Won Deal: **$27,079**
- Stale Open Leads: **358**

The workbook uses formula-driven supporting sheets so headline dashboard values can be traced back to row-level CRM records rather than relying on hard-coded summary values.
