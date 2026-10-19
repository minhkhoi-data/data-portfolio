# Methods, metrics and decision logic

## Question, units and lineage

The project supports a CRM analyst deciding which **historical audience hypotheses** to investigate or test. It describes the supplied transactions; it does not identify profitable treatment effects.

| Level | Meaning / key | Output |
|---|---|---|
| Raw row | Source invoice/product line; no unique line ID exists | Immutable `data/online_retail_II.csv.gz` |
| Purchase/credit line | Identifiable, valid priced positive purchase or negative C-prefixed credit | `outputs/purchase_lines.csv.gz`, `credit_lines.csv.gz` |
| Order | Customer ID + non-cancelled purchase invoice | `outputs/orders.csv` |
| Customer | One row per identified customer with at least one valid positive purchase | `outputs/customer_lifecycle_table.csv` |
| Cohort | Month of first **observed** purchase | `outputs/cohort_counts.csv`, `cohort_retention.csv` |
| Proposed audience | One mutually exclusive CRM review/test label per analysed customer | `outputs/crm_priority_summary.csv` |

Source columns: Invoice (string purchase/cancellation code); StockCode (string item or invoice charge); Description (optional text/label); Quantity (integer signed units); InvoiceDate (source-local ISO timestamp, timezone unspecified); Price (GBP per unit); Customer ID (nominal integer identifier); Country (source country label, not verified demographic segmentation).

## Preparation and reconciliation

The eight source fields are retained. Dates are parsed only as ISO dates/timestamps; ambiguous formats are rejected, counted and excluded rather than guessed. Numeric parse failures and invalid IDs are counted. Parsed IDs and integer quantities must fit the exactly representable integer range (2^53−1); larger IDs/absolute quantities are excluded before integer conversion, preventing overflow/rounding into plausible identifiers. The pipeline then applies, in order: missing ID, invalid ID, invalid required field/key/date or nonfinite number, zero/noninteger quantity, nonpositive price, inconsistent credit sign, exact duplicate raw row. Valid signed lines are split into positive purchases and negative C-prefixed credits. Blank Description is permitted because it is not a key or required metric input.

Each stage records remaining rows/value and **sequential** removals in `cleaning_reconciliation.csv`. `data_quality_summary.csv` records overlapping input flags; its counts cannot be summed as removed rows. Signed value is Quantity × Price; unknown/unpriced rows are separately counted, not claimed to have zero financial value. Invalid inputs can prevent publication. No arbitrary winsorisation or deletion of large valid orders is applied: wholesale purchases can be large, and corresponding credits may reverse them.

Exact duplicates are assumed repeated records, but a unique source line ID is unavailable. `duplicate_sensitivity.json` reports retained-duplicates totals and changed actions. If this assumption matters operationally, reconcile with invoice records before spending.

Orders use all positive lines of a customer/invoice; earliest timestamp defines the order. Multiple within-day timestamps are counted (64 in this source). An invoice spanning calendar dates or assigned to multiple customers fails validation because invoice identity would be ambiguous. Credits are retained in value calculations; they are **not** paired to a particular original invoice. Credit-only customers do not enter purchase segmentation, but `value_reconciliation.csv` bridges their signed value back to the identified signed ledger.

## Core metric dictionary

| Metric | Definition and interpretation |
|---|---|
| Orders / F | Count of distinct positive purchase invoices per customer. Two invoices at the same time count as two orders; visits and non-returned orders are unknown. |
| PurchaseDays | Distinct source calendar dates with purchases. Different-day repeat is a sensitivity definition, not a visit count. |
| GrossPurchaseValueGBP | Sum of valid positive line values, including invoice charges/manual entries; not merchandise-only sales or profit. |
| CreditValueGBP | Absolute sum of valid recorded negative C-prefixed values for the customer; can relate to purchases outside the observed interval. |
| NetRecordedValueGBP / M | Gross purchase value minus recorded credits. Can be negative. Descriptive recorded value, not audited financial net sales, margin or CLV. |
| CreditToGrossRatio | CreditValueGBP / GrossPurchaseValueGBP. It can exceed 1; credits may precede the observed purchases. |
| AverageGrossOrderValueGBP | Gross purchase value / purchase invoices; not net value divided by non-returned orders. |
| RecencyDays / R | Calendar days from last observed purchase date to snapshot date. Snapshot is one calendar day after the last source timestamp's date. |
| ObservedTenureDays | Exact elapsed days from first observed order to observation end; not verified customer age. |
| All-history repeat rate | Customers with ≥2 purchase invoices / all analysed purchase customers; follow-up differs between customers. |
| Eligible90 | First observed order timestamp + 90 full days ≤ last source timestamp. The added snapshot day is **not** extra observation. |
| SecondOrderWithin90 | A second observed invoice at elapsed time ≤90 days, within Eligible90; exact timestamp boundaries, not rounded day differences. |
| 90-day repeat rate | Eligible customers with SecondOrderWithin90 / Eligible90 customers; blank/not estimable if denominator is zero. |
| DaysToSecondOrder | Exact elapsed days between first and second observed invoice; missing for non-repeaters. Median is conditional on observed repeaters and is not an optimal treatment day. |
| AnotherPurchaseDayWithin90 | First purchase on a later calendar day within 90 elapsed days / the same mature Eligible90 population. |
| Monthly cohort activity | Customers purchasing in calendar month n after first observed month / cohort size. Not continuous survival and not verified acquisition retention. |
| Weighted cohort activity | Sum of active customers / sum of cohort sizes, using only cohorts whose baseline and target month are complete. Do not average cohort rates without weights. |
| GrossValueSharePct | Group gross purchase value / all analysed gross purchase value ×100; historical concentration only. |

Rates are saved as proportions (0–1); labelled chart percentages multiply by 100. Monetary computations preserve source precision, including fractional pennies; display rounded GBP. Reconciliations use GBP 0.01 absolute tolerance, not a claim of accounting accuracy.

## RFM: relative description with deterministic ties

Quintile cutoffs are the raw-value 20/40/60/80 percentiles. An ascending score is 1 + number of cutoffs **strictly below** the value. F/M use that score; R uses 6 minus it. Equal raw values always receive the same score, independent of input ordering. Equal-to-cutoff values stay in the lower ascending bin; repeated cutoffs can leave empty score bands. Bins are not forced to have equal populations.

The current numeric cutoffs are exported in `rfm_cutoffs.csv`. Lifetime F and M have more opportunity to accumulate for older observed histories; `tenure_context.csv` and customer 365-day fields expose this. Those fields are context checks, not an annualised forecast. A recent first-observed customer still has less than 365 days of history, and old customers can have credits without matched old purchases.

`RFM_Score` is the **sum** R+F+M (3–15). It is descriptive only; the action queue does not rank customers by that sum. `RFM_Profile` retains the three component scores. RFM labels are evaluated in this order:

| Label | Exact rule |
|---|---|
| Champions (relative) | R≥4 AND F≥4 AND M≥4 |
| Recent frequent | Otherwise R≥3 AND F≥4 |
| Recent mid-frequency | Otherwise R≥4 AND F in {2,3} |
| Recent low-frequency | Otherwise R≥4 AND F=1 |
| Lapsed frequent | Otherwise R≤2 AND F≥3 |
| Lapsed low-frequency | Otherwise R≤2 AND F≤2 |
| Intermediate | All remaining combinations |

“Recent/lapsed” here is **relative to this population**. “Frequent” does not prove loyalty. No score combination proves a customer is newly acquired. Relative labels and absolute lifecycle answer different questions; crosswalk counts make the relationship visible.

## Absolute lifecycle and CRM integration

| Lifecycle | Exact rule, using purchase-invoice frequency |
|---|---|
| Recent single-order | Orders=1 AND RecencyDays≤90 |
| Active repeat | Orders≥2 AND RecencyDays≤90 |
| At risk | 90<RecencyDays≤180, regardless of order count |
| Dormant | RecencyDays>180 |

These are analyst-defined operating cutoffs, not churn diagnoses. Config is in `analysis/config.json`; alternatives appear in `rule_sensitivity.csv`. “Higher recorded value” is M≥4, “middle” is M=3, “lower” is M≤2. These are relative historical tiers, not predicted worth.

Rules apply in order: **credit/value review overrides every outreach label** when net recorded value≤0 or credit/gross≥0.5. Recent single-order customers enter a second-order test hypothesis. For other states:

| Lifecycle | RFM/value context | Proposed audience |
|---|---|---|
| Active repeat | Champions plus higher-value M and frequent F | Protect frequent higher-value |
| Active repeat | Higher recorded value, remaining | Develop higher-value repeat |
| Active repeat | Remaining | Develop repeat relationship |
| At risk | Higher M and F≥4 | Win-back frequent higher-value test |
| At risk | Higher M, remaining | Win-back higher-value test |
| At risk | Remaining | Lower-cost win-back test |
| Dormant | Higher M | Review dormant higher-value |
| Dormant | Remaining | Lower-cost dormant test |

M therefore affects active, at-risk **and dormant** treatment. Lifecycle determines stage from raw recency and purchase count; relative RFM contributes value/frequency and Champion context within it. `rfm_lifecycle_crosswalk.csv` verifies coverage and reveals overlaps instead of pretending all labels describe the same dimension.

Repeat/cohort data enter the **test rationale and aggregate baseline**, not a per-customer risk score. `repeat_90_curve.csv` uses the same mature population at days 0/7/14/30/60/90. `repeat_90_by_cohort.csv` shows maturity and period differences. Do not compare past acquisition-stage repeat by **current** RFM group: later purchasing helps define those groups, making that comparison circular. The generated memo ties the references to proposed tests and states missing margin/contact inputs.

## Cohort censoring and uncertainty

The final source month is conservatively excluded as incomplete: December 2011 is partial, so November 2011 is last complete. A source starting after day 1 would also exclude its first partial month. Completeness is a coverage assumption, not inferred from a zero transaction count. A changed dataset requires a reviewed coverage policy.

Observed target months with no purchase are 0. Future/partial target months are NaN/blank and grey in the heatmap, including cohort month 0 when incomplete. `cohort_activity_observed.csv` retains unmasked **observed** counts for inspection; it is not the headline denominator. Different retention horizons have different mature audiences. A month-12 rate is not evidence that a particular month-1 customer survived continuously.

This is a descriptive census of included histories. No population p-values or causal intervals are claimed. Sensitivity covers ties, alternate lifecycle/value/credit rules, duplicate policy, another-day repeat and tenure. Precision, coverage and alternative explanations matter more than adding an unneeded statistical model. Product mix, seasonality, wholesalers and missing IDs remain limitations, so a successful treatment cannot be inferred here.

## Functionality and scope limits

The CLI validates before publishing staged outputs; failed required inputs exit nonzero and print no PASS. Old files are not labelled as a new successful run. CSVs, charts and the generated memo refresh on a successful run; no live monitoring or interactivity is claimed. QA checks semantic results independently with SQL and hand-computed fixtures. Python dependencies are pinned to tested versions. The notebook calls the canonical implementation and is executed with a fresh Jupyter kernel; the managed audit runtime uses a fresh in-process kernel when its local TCP/ZeroMQ socket is restricted (recorded in `audit/notebook_execution.json`). The notebook runner uses its own Python interpreter for a subprocess kernel; a different globally registered kernel cannot silently select a different dependency environment. Only an observed permission failure permits automatic in-process fallback; cell/dependency errors propagate. The managed runtime selects a fresh in-process kernel by default; other environments attempt a subprocess. Set RFM_KERNEL_MODE to override the mode, which is recorded in the evidence. A saved HTML preview is supplied for reading without running.
