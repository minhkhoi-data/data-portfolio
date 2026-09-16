# Campaign Funnel & Channel Performance Analysis

## Project Overview

This project analyzes marketing campaign performance across multiple channels to identify funnel drop-offs, compare channel efficiency, and prioritize campaigns for optimization.

The goal is not only to report campaign metrics, but also to translate marketing data into practical business recommendations for budget allocation and campaign improvement.

## Business Context

A marketing team runs campaigns across several channels such as Search, Display, Email, Influencer, and Social. Each campaign generates impressions, clicks, leads, conversions, cost, revenue, and ROI.

However, high traffic does not always mean strong business performance. A campaign may generate many impressions and clicks, but still fail to create enough leads, conversions, or revenue.

Because of this, campaign performance should be evaluated using both funnel efficiency and cost efficiency.

## Business Questions

This project answers the following questions:

1. Where does the campaign funnel lose the most efficiency?
2. Which marketing channels perform better in terms of conversion and revenue efficiency?
3. Which campaigns generate strong ROAS and low CAC?
4. Which campaigns spend more but generate weaker return?
5. How can campaigns be grouped into practical action categories?

## Dataset

The dataset used in this project is the **Marketing Campaign Performance Dataset** from Kaggle.

Dataset source: https://www.kaggle.com/datasets/mirzayasirabdullah07/marketing-campaign-performance-dataset

The dataset contains 10,000 campaign-level records with the following fields:

- Campaign ID
- Start date
- End date
- Channel
- Impressions
- Clicks
- Leads
- Conversions
- Cost
- Revenue
- ROI

The dataset is not presented as data from one specific real company. It is used here as a portfolio dataset to simulate a practical marketing analytics task.

## Tools Used

- Python
- pandas
- numpy
- matplotlib
- Jupyter Notebook

## Analysis Workflow

The project follows a simple business analytics workflow:

1. Load and inspect the dataset
2. Check data quality
3. Prepare date columns and campaign duration
4. Create marketing KPIs
5. Analyze the overall campaign funnel
6. Compare performance by marketing channel
7. Analyze individual campaign performance
8. Prioritize campaigns using rule-based logic
9. Provide business recommendations

## Key Metrics

The main KPIs used in this project include:

| Metric | Formula | Purpose |
|---|---|---|
| CTR | Clicks / Impressions | Measures click-through performance |
| Lead Rate | Leads / Clicks | Measures click-to-lead efficiency |
| Conversion Rate | Conversions / Clicks | Measures click-to-conversion efficiency |
| Lead-to-Conversion Rate | Conversions / Leads | Measures lead quality and conversion efficiency |
| CPC | Cost / Clicks | Measures cost per click |
| Cost per Lead | Cost / Leads | Measures lead acquisition cost |
| CAC | Cost / Conversions | Measures cost per conversion |
| ROAS | Revenue / Cost | Measures revenue efficiency |

## Key Findings

### 1. The biggest funnel drop-off happens from impressions to clicks

Only **5.48%** of impressions become clicks. This means the impression-to-click stage is the biggest funnel bottleneck and CTR is the first major efficiency point to monitor.

### 2. Channel-level performance is relatively close

Search, Display, Email, Influencer, and Social show relatively close performance across CTR, conversion rate, CAC, and ROAS.

Because the differences are small, channel-level results alone are not enough to make strong budget decisions.

### 3. Campaign-level analysis gives clearer insight

Individual campaigns show stronger differences than channel averages. Some campaigns have strong ROAS and low CAC, while others spend more but generate weaker return.

This means campaign-level analysis is more useful for budget and optimization decisions.

### 4. Rule-based prioritization supports decision-making

Campaigns were grouped into four action categories:

- Scale Review
- Optimize
- Investigate
- Reduce / Pause Review

This helps translate campaign metrics into practical business actions.

## Campaign Prioritization Logic

Campaigns were assigned into priority groups using simple median-based rules.

| Priority Group | Meaning | Suggested Action |
|---|---|---|
| Scale Review | Strong ROAS, lower CAC, and solid conversion volume | Review for controlled budget increase |
| Optimize | Good CTR but weaker conversion rate | Improve landing page, offer, targeting, or post-click experience |
| Investigate | Mixed performance that needs more context | Check campaign objective, audience, creative, and tracking |
| Reduce / Pause Review | Weak ROAS and higher CAC | Reduce budget, pause, or redesign before spending more |

## Business Recommendations

| Priority | Recommendation | Expected Business Impact |
|---|---|---|
| 1 | Review Scale Review campaigns for controlled budget increase | Increase revenue while keeping conversion cost controlled |
| 2 | Review Reduce / Pause Review campaigns before giving more budget | Reduce wasted spend and improve budget efficiency |
| 3 | Optimize campaigns with strong CTR but weak conversion rate | Improve post-click conversion and reduce inefficient traffic |
| 4 | Investigate mixed-performance campaigns before making budget decisions | Avoid premature decisions and identify hidden opportunities |
| 5 | Continue using campaign-level analysis instead of relying only on channel averages | Make more precise campaign optimization decisions |

## Limitations

This analysis has some limitations:

- The dataset is campaign-level and does not include user-level behavior.
- The dataset does not include creative type, landing page, audience segment, device, or campaign objective.
- The prioritization framework is rule-based and should support decision-making, not replace business judgment.
- The analysis identifies performance patterns, but it does not prove the exact cause of campaign performance.
- More data would be needed to understand why specific campaigns perform better or worse.

## Project Structure

```text
05_marketing_campaign_funnel_analysis/
│
├── data/
│   └── marketing_campaign_performance_10000.csv
│
├── README.md
└── marketing_campaign_funnel_analysis.ipynb
```

## How to Run

1. Clone or download this project folder.

2. Make sure the dataset is stored in:

```text
data/marketing_campaign_performance_10000.csv
```

3. Open the notebook:

```text
marketing_campaign_funnel_analysis.ipynb
```

4. Run the notebook cells from top to bottom.

## Final Conclusion

This project shows how marketing campaign data can be used not only to report performance, but also to support business decisions around budget allocation, campaign optimization, and performance improvement.

The strongest value of this analysis is the move from basic campaign reporting to practical campaign prioritization.