# Data Analytics Portfolio

## Customer, Growth & Business Analytics

This portfolio contains eight end-to-end analytics projects focused on a common objective: turning operational, customer, marketing, and commercial data into decisions.

The projects cover customer segmentation, CRM and sales operations, marketing performance, e-commerce growth, predictive modelling, SQL-based risk analysis, product affinity networks, and airline performance analytics.

**Core toolkit:** Excel • Power BI • Python • R • PostgreSQL • Tableau

---

## Portfolio Projects

### 1. E-commerce Customer Segmentation & Retention Analysis
**Tools:** Python, pandas, matplotlib

**Business question:** Which customer groups should be prioritised for retention, reactivation, and revenue growth?

Key work:
- Built customer-level RFM metrics from transaction data.
- Segmented **5,878 customers** from **36,969 orders**.
- Identified that the Champions segment represented **21.93% of customers but 68.03% of revenue**.
- Translated segmentation results into CRM and retention actions.

[View project](./ecommerce_customer_segmentation_rfm)

---

### 2. Marketing Campaign Funnel & Channel Performance
**Tools:** Python, pandas, NumPy, matplotlib

**Business question:** Where does marketing performance weaken across the funnel, and which campaigns or channels need optimisation?

Key work:
- Analysed **10,000 campaign records**.
- Built CTR, lead rate, conversion rate, CPC, CPL, CAC, and ROAS metrics.
- Reproduced an overall CTR of approximately **5.48%**.
- Connected campaign metrics to practical scale, optimise, investigate, or reduce-spend decisions.

[View project](./marketing_campaign_funnel_analysis)

---

### 3. Commercial & CRM Operations Analysis
**Tools:** Excel

**Business question:** Which parts of the sales funnel, acquisition mix, sales team, and open pipeline deserve management attention?

Key work:
- Built a formula-driven CRM model from **1,800 synthetic leads**.
- Analysed funnel leakage, channel performance, sales-rep performance, stale opportunities, and weighted pipeline.
- Produced an executive dashboard with auditable supporting sheets.
- Final model tracks **$9.78M won revenue**, **$13.01M open pipeline**, and **358 stale open leads**.

[View project](./commercial_crm_excel_analytics)

---

### 4. E-commerce Growth & Conversion Analytics
**Tools:** Power BI, DAX, Power Query

**Business question:** How do traffic, funnel conversion, acquisition channels, customers, and products contribute to e-commerce growth?

Key work:
- Built a multi-page Power BI report and semantic model.
- Analysed **75,237 sessions**, **32,000 users**, and **4,737 transactions**.
- Validated total revenue of **$217,478.50**.
- Covered acquisition, conversion funnel, customer behaviour, geographic performance, and product performance.

[View project](./ecommerce_growth_conversion_power_bi)

---

### 5. Supervised Learning — Regression & Classification
**Tools:** R, R Markdown, `boot`, `pROC`

**Business question:** How should predictive models be selected, validated, and interpreted for continuous and binary outcomes?

Key work:
- Compared linear, polynomial, multiple-regression, and interaction models.
- Used model diagnostics and **10-fold cross-validation** for model selection.
- Built a logistic model for learner completion.
- Achieved **AUC = 0.813** and evaluated threshold trade-offs between sensitivity and specificity.

[View project](./supervised_learning_regression_classification_r)

---

### 6. Insurance Risk Segmentation
**Tools:** PostgreSQL, SQL

**Business question:** Which customer characteristics are associated with higher insurance charges, and which segments represent the highest observed cost risk?

Key work:
- Built a reproducible PostgreSQL workflow from raw data to analytical views.
- Used CTEs, bucketing, percentiles, ranking, aggregation, and segmentation.
- Verified **1,338 raw records** and **1,337 final records** after exact-duplicate removal.
- Ranked high-cost customer segments using average, median, and 90th-percentile charges.

[View project](./insurance_risk_segmentation_sql)

---

### 7. Product Affinity & Co-Purchase Network Analysis
**Tools:** Python, pandas, Jupyter, Gephi-compatible network data

**Business question:** Which products are repeatedly purchased together, and which products act as important nodes in the co-purchase network?

Key work:
- Converted transaction baskets into weighted product-product relationships.
- Built reusable edge and node datasets for network analysis.
- At the focused threshold, reproduced a network of **581 nodes and 1,948 edges**.
- Exported network files for further exploration in Gephi.

[View project](./product_affinity_network_analysis)

---

### 8. Australian Airline Performance Visual Analytics
**Tools:** R, R Markdown, Tableau

**Business question:** How do Australian airlines, airports, routes, and network conditions differ in punctuality, cancellation performance, and operating volume?

Key work:
- Built a reproducible pipeline from a multi-sheet workbook to clean and analysis-ready datasets.
- Processed **80,972 analytical records** covering **2010–2024**.
- Calculated weighted departure OTP, arrival OTP, cancellation rates, airport performance, route performance, and airline comparisons.
- Built Tableau views covering network trends, geographic performance, heatmaps, route analysis, and airline comparisons.

[View project](./airline_performance_visual_analytics)

---

## Repository Structure

```text
data-portfolio/
├── ecommerce_customer_segmentation_rfm/
├── marketing_campaign_funnel_analysis/
├── commercial_crm_excel_analytics/
├── ecommerce_growth_conversion_power_bi/
├── supervised_learning_regression_classification_r/
├── insurance_risk_segmentation_sql/
├── product_affinity_network_analysis/
├── airline_performance_visual_analytics/
├── DATA_SOURCES.md
├── FUNCTIONAL_AUDIT.md
├── README.md
└── LICENSE
```

Each project folder contains its own README with the business question, methodology, outputs, and reproduction instructions.

---

## Reproducibility

The portfolio is structured so that project files can be opened and reproduced without relying on machine-specific working directories.

- Python notebooks use project-relative paths.
- Excel includes its supporting dataset and formula-driven analysis workbook.
- Power BI is stored as a PBIP project with its semantic model and report definition.
- R projects use relative paths and include the required analysis data.
- PostgreSQL includes separate schema-setup and analysis scripts.
- Tableau connects to the processed airline dataset through a relative datasource path.
- Large reproducible intermediate files are excluded where they can be regenerated from the included source data.

`FUNCTIONAL_AUDIT.md` records the final runtime verification status of the portfolio.

---

## Data Sources & Licensing

Datasets in this repository come from a mixture of public sources, coursework-provided datasets, and synthetic portfolio data.

Dataset provenance and usage notes are documented separately in [`DATA_SOURCES.md`](./DATA_SOURCES.md).

The repository license applies to original code and documentation unless otherwise stated. Third-party datasets remain subject to the terms of their original sources.
