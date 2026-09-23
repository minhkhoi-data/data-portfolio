# Data Dictionary

The workbook contains 1,800 synthetic CRM lead records. Each row in `CRM_Data` represents one lead or opportunity.

This document separates source fields from calculated analytical fields so the workbook logic can be audited without opening every formula individually.

## Raw CRM Fields

| Field | Type | Business meaning |
|---|---|---|
| `Lead_ID` | Text | Unique CRM lead identifier |
| `Created_Date` | Date | Date the lead was created |
| `Owner` | Text | Sales representative responsible for the lead |
| `Region` | Text | Sales region |
| `Raw_Source` | Text | Original, unstandardised acquisition-source label |
| `Product_Code` | Text | Product identifier used for lookup enrichment |
| `Industry` | Text | Customer industry |
| `Company_Size` | Text | Customer segment: SMB, Mid-Market, or Enterprise |
| `Deal_Stage` | Text | Current or final sales stage |
| `Last_Stage_Date` | Date | Date of the most recent stage update |
| `Close_Date` | Date | Close date for won or lost deals |
| `Expected_Value_USD` | Currency | Expected opportunity value before outcome adjustment |
| `Discount_Pct` | Percentage | Discount applied to the opportunity |
| `Stage_Probability` | Percentage | Probability associated with the current sales stage |
| `Lost_Reason` | Text | Reason recorded for a closed-lost opportunity |
| `Funnel_Level` | Whole number | Furthest funnel stage reached by the lead |

## Calculated Excel Fields

| Field | Type | Main logic | Business meaning |
|---|---|---|---|
| `Source_Clean` | Text | `VLOOKUP` + `IFERROR` | Standardised acquisition channel derived from `Raw_Source` |
| `Product_Name` | Text | `VLOOKUP` + `IFERROR` | Product name mapped from `Product_Code` |
| `Product_Category` | Text | `VLOOKUP` + `IFERROR` | Product category mapped from `Product_Code` |
| `Deal_Segment` | Text | `IF` | Deal-size segment derived from expected opportunity value |
| `Outcome` | Text | `IF` | Simplified outcome classification: Won, Lost, or Open |
| `Actual_Revenue_USD` | Currency | `IF` | Realised revenue for closed-won deals after discount |
| `Weighted_Pipeline_USD` | Currency | `IF` | Open expected value multiplied by stage probability |
| `Sales_Cycle_Days` | Whole number | `IF` + `IFERROR` | Days between lead creation and close for completed deals |
| `Age_Days` | Whole number | `IF` | Age of an open opportunity as of the workbook snapshot date |
| `SLA_Flag` | Text | `IF` + `AND` | Flags open opportunities older than 30 days as stale |
| `Created_Month` | Text | `TEXT` | Year-month reporting key based on `Created_Date` |
| `Close_Month` | Text | `TEXT` | Year-month reporting key based on `Close_Date` |
| `Created_Quarter` | Text | `YEAR` + `MONTH` + `ROUNDUP` | Calendar-quarter reporting key |
| `Lead_Score` | Whole number | Nested `IF` + `MIN` | Rule-based lead-prioritisation score |
| `Forecast_Category` | Text | Nested `IF` | Pipeline classification such as Pipeline, Best Case, Commit, or Closed |

## Supporting Lookup Fields

The `Lookups` sheet contains the control tables used by the workbook, including:

- raw-source to clean-channel mappings
- product-code to product-name/category mappings
- sales-rep region and team mappings
- rep revenue targets
- clean channel list
- workbook snapshot/control values

`VLOOKUP` is used for compatibility with Excel installations where `XLOOKUP` is unavailable.

## Notes

- The dataset is synthetic and does not represent real customers, an employer, or confidential business records.
- Formula-driven fields are kept visible in the workbook so KPI logic can be traced from row-level records to summary sheets.
- Repository-wide provenance notes are documented in [`../../DATA_SOURCES.md`](../../DATA_SOURCES.md).
