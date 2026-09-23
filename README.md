# Customer & Growth Analytics Portfolio

I am an entry-level, business-facing Data Analyst focused on customer, marketing, product, and commercial decisions. This portfolio shows how I move from data quality and metric design to an actionable recommendation—without presenting descriptive patterns as causal proof.

**Core tools:** SQL · Excel · Power BI/DAX · Python · Statistics · Tableau  
**Target roles:** Customer Analyst · CRM Analyst · Growth Analyst · Marketing/Data Analyst · Product Analyst · Commercial Analyst

## Start here: three flagship decisions

These three projects are the shortest route through the portfolio.

### 1. [Customer Lifecycle, Retention & CRM Prioritisation](ecommerce_customer_segmentation_rfm/)

**Decision:** who should be protected, developed, won back, or deprioritised?  
**Evidence:** 5,878 customers; RFM, repeat purchase, mature-cohort retention, lifecycle state, right-censoring control, and CRM action queue.  
**Result:** 72.4% repeat-customer rate; 47.6% 90-day repeat among eligible customers; active repeat customers generated 79.7% of historical revenue.

### 2. [Campaign & Growth Performance](marketing_campaign_funnel_analysis/)

**Decision:** where does the funnel weaken, and which campaigns deserve scale, optimisation, pause, or investigation review?  
**Evidence:** 10,000 reproducible synthetic campaigns; weighted CTR, lead rates, CAC, ROAS, data-quality gates, and transparent triage rules.  
**Result:** 4.20% weighted CTR, $22.52 observed CAC, and 3.35x observed ROAS; recommendations remain review actions rather than automatic budget changes.

### 3. [Product Funnel, Growth & Experimentation](ecommerce_growth_conversion_power_bi/)

**Decision:** where does the product funnel lose users, and should a checkout change be rolled out?  
**Evidence:** a five-page Power BI funnel model plus a 32,000-user synthetic randomised experiment with SRM, balance, 95% CI, p-value, MDE/power, guardrails, and subgroup cautions.  
**Result:** treatment conversion increased from 5.28% to 6.06%; the pre-declared gates support a monitored staged rollout.

## Supporting evidence

| Project | Primary proof | Why it remains in the portfolio |
|---|---|---|
| [Commercial & CRM Operations](commercial_crm_excel_analytics/) | Excel formulas, pipeline logic, dashboarding | Demonstrates auditable spreadsheet analysis for sales and CRM decisions |
| [Insurance Cost Drivers](insurance_risk_segmentation_sql/) | PostgreSQL, CTEs, windows, percentiles, QA | Demonstrates SQL depth and careful descriptive segmentation |
| [Product Affinity Network](product_affinity_network_analysis/) | Python, basket transformation, network exports | Demonstrates an additional customer/product analytical technique |
| [Australian Airline Performance](airline_performance_visual_analytics/) | R pipeline and Tableau | Demonstrates reproducible visual analytics on a public operational domain |

Supporting projects add tool evidence; they are not presented as equally important flagship stories.

## How the portfolio is evaluated

Every flagship contains:

1. a decision question;
2. metric definitions and data-quality gates;
3. reproducible analysis and inspectable outputs;
4. findings connected to an action;
5. limitations, causal boundaries, and a next test.

The repository-level [`FUNCTIONAL_AUDIT.md`](FUNCTIONAL_AUDIT.md) records runtime, integrity, link, hygiene, and recruiter-readiness checks. Dataset origin and redistribution scope are documented in [`DATA_SOURCES.md`](DATA_SOURCES.md).

## Reproduce the Python flagships

```bash
python ecommerce_customer_segmentation_rfm/analysis/run_analysis.py
python marketing_campaign_funnel_analysis/src/generate_synthetic_campaigns.py
python marketing_campaign_funnel_analysis/analysis/run_analysis.py
python ecommerce_growth_conversion_power_bi/experiment/run_experiment.py
python ecommerce_growth_conversion_power_bi/scripts/validate_dataset.py
```

All paths are repository-relative. Generated outputs are deterministic, and each canonical script stops on failed validation gates.

## Repository structure

```text
data-portfolio/
├── ecommerce_customer_segmentation_rfm/       # flagship 1
├── marketing_campaign_funnel_analysis/        # flagship 2
├── ecommerce_growth_conversion_power_bi/      # flagship 3
├── commercial_crm_excel_analytics/             # supporting Excel
├── insurance_risk_segmentation_sql/            # supporting SQL
├── product_affinity_network_analysis/           # supporting network analysis
├── airline_performance_visual_analytics/        # supporting R/Tableau
├── DATA_SOURCES.md
└── LICENSE
```

## Scope

Synthetic datasets are labelled explicitly. Third-party data retain their original terms and are not relicensed by this repository. Descriptive projects identify patterns and prioritise follow-up; only a randomised design can support an incremental causal claim.
