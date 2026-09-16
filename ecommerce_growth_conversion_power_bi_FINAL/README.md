# E-commerce Growth & Conversion Analytics | Power BI

An end-to-end Power BI portfolio case study that connects acquisition, funnel behaviour, customer quality, and product performance to practical growth decisions.

## Business question

> Where is the e-commerce journey losing the most value, which segments are commercially strongest, and what should the growth team investigate first?

The analysis is designed for Growth, E-commerce, Marketing, and Customer Analytics stakeholders. It covers five report views:

1. Executive Overview
2. Conversion Funnel
3. Acquisition & Channel
4. Product Performance
5. Customer & Geography

## Project deliverables

- Power BI Project source (`.pbip`) with a PBIR report and TMDL semantic model
- 3 fact tables, 5 shared dimensions, and 13 one-to-many relationships
- 31 explicit DAX measures in a dedicated measure table
- 5 report pages containing 45 native Power BI visuals
- Reproducible summary outputs and static source-validation scripts
- Business brief, data dictionary, model notes, DAX reference, and analysis report
- BigQuery SQL templates for adapting the model to Google's public GA4 sample

Open the report from:

`powerbi/EcommerceGrowth_PBIP/EcommerceGrowth.pbip`

Power BI Desktop must have the **Power BI Project (.pbip)** and **enhanced report format (PBIR)** preview features enabled.

## Data model

The model separates facts by grain so product-level analysis does not duplicate session or order metrics.

| Table | Grain | Primary use |
|---|---|---|
| `FactSessions` | One row per session | Traffic, engagement, funnel, conversion |
| `FactOrders` | One row per order | Revenue, transactions, AOV, purchasers |
| `FactOrderItems` | One row per order line | Product revenue, units, category and SKU analysis |

Shared dimensions: `DimDate`, `DimChannel`, `DimDevice`, `DimGeo`, and `DimProduct`. A disconnected `FunnelStage` table controls funnel ordering.

## Core metrics

| Metric | Value |
|---|---:|
| Sessions | 75,237 |
| Users | 32,000 |
| Transactions | 4,737 |
| Revenue | $217,478.50 |
| Session conversion rate | 6.30% |
| Average order value | $45.91 |

The DAX library includes traffic and engagement, stage-to-stage funnel rates, revenue and efficiency, purchaser quality, product performance, and month-over-month measures. See [`docs/DAX_REFERENCE.md`](docs/DAX_REFERENCE.md).

## Findings and decisions

| Finding in the demo period | Business interpretation | Recommended next step |
|---|---|---|
| Product-view to add-to-cart is **29.25%**, the largest stage loss | Product consideration is the clearest friction point | Diagnose mobile product pages by SKU: CTA visibility, price communication, stock, content, and page speed |
| Mobile produces **57.8%** of sessions but converts at **4.76%**, versus **8.77%** on desktop | More mobile traffic alone is unlikely to close the revenue gap | Segment the mobile funnel by channel and product; prioritize the largest high-volume loss before acquisition expansion |
| Email converts at **8.85%** and generates **$4.17 revenue per session** | Lifecycle traffic is efficient, but it is not directly comparable with paid acquisition | Protect lifecycle programs; evaluate paid channels with cost, reach, and incrementality before reallocating budget |
| Returning-user sessions convert at **6.98%**, versus **5.37%** for new-user sessions | Retention and remarketing audiences are commercially stronger | Test repeat-purchase and remarketing journeys by customer cohort |
| The top-revenue SKU is **Google Zip Hoodie** at **$17,973.38** | Product revenue is concentrated | Review availability and merchandising for leading SKUs while monitoring concentration risk |

These findings are diagnostic, not causal. The dataset does not contain experiment assignment, media spend, margin, inventory, or page-performance data.

## Data and refresh path

The bundled CSV files are synthetic, fixed demo data created for portfolio analysis. They are not official Google production figures.

The current Power Query partitions read the same CSV filenames from this repository's configured raw GitHub path. The `data/` directory is also included for inspection and validation. If the repository location changes, update the base URL in the TMDL partition queries before refreshing.

The SQL templates in `sql/` show how the session and order-item structures can be adapted to Google's public, obfuscated GA4 Merchandise Store sample. They are an optional source pathway and are not the origin of the bundled values.

## Validation

Run the source checks from the repository root:

```bash
python -m pip install -r requirements.txt
python scripts/build_outputs.py
python scripts/validate_project.py
```

The checks cover dataset grain, keys, referential integrity, revenue reconciliation, funnel logic, expected totals, JSON validity, report-page count, visual bounds, and visual-to-model field bindings.

Static validation is intentionally separate from Power BI Desktop acceptance. A portfolio release should also be opened, refreshed, and visually checked in Power BI Desktop before screenshots or a `.pbix` export are published.

## Repository structure

```text
ecommerce_growth_conversion_power_bi/
├── README.md
├── DATA_NOTE.md
├── data/
├── docs/
├── outputs/
├── powerbi/
│   └── EcommerceGrowth_PBIP/
├── requirements.txt
├── scripts/
└── sql/
```

## Scope

The project demonstrates the path from **business question → data model → measures → report → recommendation → limitation**. It does not claim causal inference or metrics that the source cannot support, such as CAC, ROAS, profit, or experiment lift.
