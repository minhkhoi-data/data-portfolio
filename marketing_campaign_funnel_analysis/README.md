# Campaign & Growth Performance

**Flagship 2 of 3 · Customer & Growth Analytics**  
**Tools:** Python, pandas, NumPy, matplotlib  
**Data:** 10,000 deterministic synthetic campaigns across Search, Email, Social, Display, and Influencer

## Business decision

Where does marketing performance weaken across the funnel, which campaigns deserve scale or optimisation review, and what can the available data support without overclaiming incrementality?

![Campaign decision dashboard](figures/campaign_decision_dashboard.png)

## Decision summary

Across the complete dataset, campaigns generated **4.20% weighted CTR**, **$22.52 observed CAC**, and **3.35x observed ROAS**.

- **Email** has the strongest weighted observed ROAS at **4.31x**.
- **Display** has the weakest observed ROAS at **1.49x** and the highest CAC at **$44.68**.
- Campaigns with high CTR but weak downstream conversion enter a landing-page or offer-optimisation queue rather than being labelled an acquisition failure.
- High-ROAS, low-CAC campaigns enter a scale review; they are not automatically scaled because capacity, marginal returns, attribution, and incrementality are not present in the dataset.

## Metric logic

| Metric | Formula | Decision use |
|---|---|---|
| CTR | Clicks ÷ impressions | Creative and audience response |
| Click-to-lead | Leads ÷ clicks | Landing-page and form effectiveness |
| Lead-to-conversion | Conversions ÷ leads | Lead quality and sales/offer effectiveness |
| CAC | Spend ÷ conversions | Acquisition efficiency |
| ROAS | Revenue ÷ spend | Observed return; not causal incrementality |

Channel rates are calculated from **summed numerators and denominators**. The analysis does not average campaign-level rates, which would give small and large campaigns equal weight.

## Reproduce

The dataset is generated inside the repository, removing dependence on an ambiguous third-party license.

```bash
python marketing_campaign_funnel_analysis/src/generate_synthetic_campaigns.py
python marketing_campaign_funnel_analysis/analysis/run_analysis.py
```

Expected result:

```text
PASS — generated 10,000 synthetic campaign records
PASS — campaign analysis completed
Campaigns: 10,000
CTR: 4.20%
CAC: $22.52
ROAS: 3.35x
```

The analysis validates schema, dates, funnel ordering, missingness, duplicate campaign IDs, and non-negative measures before producing decision outputs.

## Start here

- [Decision memo](memo/business_memo.md)
- [Decision dashboard](figures/campaign_decision_dashboard.png)
- [Canonical analysis](analysis/run_analysis.py)
- [Synthetic-data generator](src/generate_synthetic_campaigns.py)
- [Channel performance](outputs/channel_performance.csv)
- [Campaign decision table](outputs/campaign_decision_table.csv)

## Decision-rule limits

The priority queue uses transparent median-based rules to triage human review. It is not an optimisation algorithm and should not execute budget changes automatically. The synthetic data contain observed spend and revenue but no contribution margin, customer lifetime value, attribution model, or holdout design. A real budget decision should be validated with a geo/audience holdout and margin/customer-quality guardrails.

## Data disclosure

All campaign records are deterministic synthetic portfolio data generated with seed `2026`. They do not represent a real employer, client, advertising account, or claimed commercial outcome.
