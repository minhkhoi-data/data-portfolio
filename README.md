# Data Analytics Portfolio — Customer, Growth & Business Analytics

A curated portfolio of analytics projects focused on turning business data into decisions. The work spans customer segmentation, marketing performance, predictive modelling, SQL analysis, product affinity, and visual analytics.

**Current toolkit:** Python • R • SQL (PostgreSQL) • Tableau • statistical modelling • business analytics

> Portfolio principle: fewer, stronger projects. Each project is kept only when it demonstrates a distinct analytical skill or business use case.

## Featured Projects

### 1. E-commerce Customer Segmentation & Retention Opportunity Analysis
**Tools:** Python, pandas, matplotlib  
**Business question:** Which customer groups should be prioritised for retention, reactivation, and revenue growth?

- Built customer-level RFM metrics from transaction data.
- Found that **Champions represented 21.93% of customers but 68.03% of revenue**.
- Identified **At Risk** customers as a meaningful win-back opportunity and translated segments into CRM actions and KPIs.

[Open project](./ecommerce_customer_segmentation_rfm)

### 2. Marketing Campaign Funnel & Channel Performance Analysis
**Tools:** Python, pandas, NumPy, matplotlib  
**Business question:** Where does the funnel lose efficiency, and which campaigns deserve scale, optimisation, investigation, or budget review?

- Analysed **10,000 campaign-level records**.
- Built CTR, lead rate, conversion rate, CPC, cost per lead, CAC, and ROAS metrics.
- Identified impression-to-click as the largest observed funnel drop-off, with **5.48% of impressions converting to clicks**.
- Created a rule-based campaign prioritisation framework for business action.

[Open project](./marketing_campaign_funnel_analysis)

### 3. Supervised Learning — Regression & Classification
**Tools:** R, R Markdown, `boot`, `pROC`  
**Business question:** How should predictive models be selected and evaluated when the outcome is continuous versus binary?

- Compared linear, polynomial, multiple, and interaction regression models using diagnostics and 10-fold cross-validation.
- Built a learner-completion logistic model with **AUC 0.813**.
- Evaluated threshold trade-offs between sensitivity and specificity and connected model thresholds to operational decision costs.

[Open project](./supervised_learning_regression_classification_r)

## Supporting Projects

| Project | Primary skill demonstrated | Key signal |
|---|---|---|
| [Insurance Risk Segmentation — SQL](./insurance_risk_segmentation_sql) | SQL analytics | CTEs, robust percentiles, segmentation, ranking, lift |
| [Product Affinity & Co-Purchase Network](./product_affinity_network_analysis) | Relational/network analytics | 1M+ transaction rows, weighted product network, hubs and communities |
| [Australian Airline Performance Visual Analytics](./airline_performance_visual_analytics) | R + Tableau | data integration, weighted KPIs, multidimensional visual analysis |

## Skills Demonstrated

**Customer & growth analytics**  
RFM segmentation • retention/reactivation logic • campaign funnel analysis • CAC/ROAS-style KPI interpretation • customer prioritisation

**Data analysis & programming**  
Python • pandas • NumPy • R • SQL/PostgreSQL • data cleaning • EDA • reproducible notebooks/R Markdown

**Statistics & modelling**  
Regression • logistic classification • cross-validation • ROC/AUC • threshold analysis • hypothesis testing • robust summary statistics

**Visual analytics**  
matplotlib • Tableau • KPI design • geographic/time-series/route visualisation • analytical storytelling

## Repository Structure

```text
data-portfolio/
├── ecommerce_customer_segmentation_rfm/
├── marketing_campaign_funnel_analysis/
├── supervised_learning_regression_classification_r/
├── insurance_risk_segmentation_sql/
├── product_affinity_network_analysis/
├── airline_performance_visual_analytics/
├── README.md
└── LICENSE
```

## Next Portfolio Builds

The next additions will close two practical tooling gaps rather than add more generic projects:

- **Excel business analysis project** — structured operational/commercial analysis using formulas, PivotTables, data cleaning, and management-ready outputs.
- **Power BI project** — an end-to-end dashboard project focused on e-commerce/customer/growth decision-making.

These will be added only when complete; unfinished placeholder projects are intentionally excluded from the public portfolio.
