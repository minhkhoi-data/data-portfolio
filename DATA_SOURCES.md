# Data Sources, Licensing & Disclosure

The repository license covers original code and documentation only. Third-party data retain their original terms and are not relicensed here. Synthetic data are labelled explicitly so portfolio demonstrations cannot be mistaken for employer or client results.

## Customer Lifecycle, Retention & CRM Prioritisation

**Bundled file:** `ecommerce_customer_segmentation_rfm/data/online_retail_II.csv.gz`  
**Source:** UCI Machine Learning Repository, *Online Retail II*  
**Creator:** Daqing Chen  
**DOI:** `10.24432/C5CG6D`  
**Source page:** https://archive.ics.uci.edu/dataset/502/online+retail+ii  
**License displayed by UCI:** CC BY 4.0

The compressed CSV is retained for reproducibility with source attribution.

## Campaign & Growth Performance

**Bundled file:** `marketing_campaign_funnel_analysis/data/marketing_campaign_performance_10000.csv`  
**Source type:** deterministic synthetic portfolio data  
**Generator:** `marketing_campaign_funnel_analysis/src/generate_synthetic_campaigns.py`  
**Seed:** `2026`

The former third-party campaign file was replaced because its redistribution license was not explicit. The replacement data do not represent a real advertiser, employer, client, or commercial outcome.

## Commercial & CRM Operations

**Bundled file:** `commercial_crm_excel_analytics/data/crm_sales_pipeline_raw.csv`  
**Source type:** synthetic portfolio data

The records were created for auditable CRM, funnel, pipeline, sales-rep, and stale-opportunity analysis. They contain no real customers or confidential business information.

## Product Funnel, Growth & Experimentation

**Bundled files:** CSV tables under `ecommerce_growth_conversion_power_bi/data/` and `experiment/data/`  
**Source type:** deterministic synthetic GA4-style e-commerce and A/B-test data  
**Experiment generator:** `experiment/run_experiment.py`  
**Seed:** `2026`

The files are not presented as official Google or employer production data. BigQuery SQL templates show a compatible pathway using Google's public GA4 Merchandise Store sample dataset:

https://developers.google.com/analytics/bigquery/web-ecommerce-demo-dataset

## Insurance Cost Drivers

**Bundled file:** `insurance_risk_segmentation_sql/data/insurance.csv`  
**Source:** Kaggle, `mirichoi0218/insurance`  
**Source page:** https://www.kaggle.com/datasets/mirichoi0218/insurance  
**Source metadata:** Open Database

The SQL workflow uses 1,338 input rows and produces 1,337 rows after exact-duplicate removal. Users should review the current source terms before redistributing a modified copy.

## Product Affinity Network

**Bundled file:** `product_affinity_network_analysis/data/raw/online_retail_II.csv.gz`  
**Source:** the same UCI *Online Retail II* dataset used by the lifecycle project  
**DOI:** `10.24432/C5CG6D`  
**License displayed by UCI:** CC BY 4.0

This project answers a different question: product co-purchase relationships rather than customer lifecycle and retention.

## Australian Airline Performance

**Bundled analytical files:** processed CSVs under `airline_performance_visual_analytics/data/processed/`  
**Underlying public source:** Bureau of Infrastructure and Transport Research Economics (BITRE), Australian airline on-time performance reports and time-series data  
**Source page:** https://www.bitre.gov.au/resource/aviation/airline-time-performance-monthly-reports-and-time-series-data

The coursework-packaged raw workbook is intentionally not redistributed because its wrapper did not state explicit redistribution permission. [`airline_performance_visual_analytics/data/raw/README.md`](airline_performance_visual_analytics/data/raw/README.md) explains how to supply an authorised local input. The Tableau workbook remains inspectable using the bundled processed analytical CSV.

## Publication rule

- Never describe synthetic results as real business impact.
- Preserve attribution for UCI, Kaggle, Google, and BITRE sources.
- Do not add coursework, employer, customer, or confidential raw data without explicit permission.
- Recheck external source terms before republishing third-party files in another channel.
