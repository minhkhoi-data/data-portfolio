# Customer Lifecycle & Value Review — generated decision memo

## Decision and evidence

Use lifecycle to select the journey, RFM/value history to differentiate treatment, and mature repeat/cohort activity to set descriptive test references. All audiences are historical hypotheses; no messages have been sent and no causal uplift measured.

- 5,878 identified purchase customers; 36,969 distinct purchase invoices. All-history repeat: **72.4%**. Repeat on a different calendar day: **71.3%**. A second invoice is not proof of a second visit or a retained sale.
- **2,486/5,281 = 47.1%** placed a second order within exactly 90 elapsed days, among customers with the entire window observed. Different-day repeat in that same window: **44.3%**.
- Median time to second order among observed repeaters: **56.0 elapsed days**. This excludes non-repeaters, varies with follow-up and does not identify an optimal campaign day. Use repeat_90_curve.csv (same mature denominator at every point) to frame timing hypotheses.
- Month-1 cohort activity: **23.4%**; month-3: **24.9%**. The mature audiences differ; changes between horizons are not a common-population survival curve. Activity in month n need not be continuous activity in earlier months.
- Historical gross purchases: **£17,374,804**; recorded credits: **£1,023,763**; net recorded value: **£16,351,041**. These include invoice charges and are neither profit nor future CLV.
- **73** customers require credit/value review before outreach. Credit-only customers are excluded from purchase segmentation but reconciled separately.
- Alternative analyst-defined rules changed up to **1,163** action labels. Thresholds are transparent hypotheses, not validated optima; inspect rule_sensitivity.csv before operational adoption.

## Historical review/test audiences

| Proposed audience | Customers | Net recorded history |
|---|---:|---:|
| Protect frequent higher-value | 1,266 | £11,352,522 |
| Develop higher-value repeat | 409 | £1,249,039 |
| Review dormant higher-value | 404 | £1,211,460 |
| Lower-cost dormant test | 1,947 | £792,631 |
| Win-back frequent higher-value test | 189 | £709,902 |
| Develop repeat relationship | 836 | £574,632 |
| Review credits before outreach | 73 | £17,481 |
| Lower-cost win-back test | 332 | £178,338 |
| Second-order journey test | 358 | £134,639 |
| Win-back higher-value test | 64 | £130,399 |

## Conditional next tests

1. CRM analyst first resolves nonpositive net value/high credit burden, checks contact permission, current customer status, product mix and attribution of credits. No automatic discount is supported.
2. For eligible recent single-order customers, propose post-purchase timing tests (for example day 14 versus day 30 versus a no-message holdout); these timings are hypotheses. Define eligibility at assignment, follow all arms for 90 days from first order, and compare second-order rate and net contribution per assigned customer. Do not use current RFM labels to estimate historical acquisition-stage response probabilities.
3. For repeat or win-back audiences, test one permitted treatment against customer-level holdout; stratify using pre-assignment lifecycle/value/frequency and season/cohort. Primary business outcome requires margin and treatment cost not present here; also monitor credits, unsubscribes and complaints. CRM lead owns approval; analyst owns measurement. Define power/sample, stopping rule, reporting windows and acceptable harms before launch. If this cannot be done, collect the missing inputs rather than claim a successful strategy.
4. Month/cohort variation motivates investigation of seasonality, tenure, wholesale mix and acquisition source, not a causal channel ranking. Revenue concentration alone does not prove which treatment has incremental ROI.

## Limits next to the decision

Observation 2009-12-01 07:45:00–2011-12-09 12:50:00; snapshot 2011-12-10; last complete month 2011-11. The business is one historical UK retailer with wholesale customers; this is not current Vietnam market evidence. First observed purchase is not verified acquisition. Missing IDs and credit-only customers change coverage. Lifetime F/M depend on observation tenure; tenure_context.csv and the 365-day context fields help reveal that exposure difference but do not estimate future value. A credit is not linked back to a specific purchase invoice, so frequency describes positive purchase invoices, not non-returned orders. Exact-row deduplication is an assumption with a retained-duplicates sensitivity check. Source-local timestamps lack timezone metadata. All figures and the memo are static until the pipeline is rerun; the notebook invokes the same implementation.
