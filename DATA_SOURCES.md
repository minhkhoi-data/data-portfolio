# Data Sources & Usage Notes

This file documents the provenance of datasets bundled with or referenced by the portfolio.

The repository license applies to original code and documentation unless otherwise stated. **Third-party datasets are not relicensed by this repository** and remain subject to the terms of their original providers.

---

## 1. E-commerce Customer Segmentation & Retention Analysis

**Project:** `ecommerce_customer_segmentation_rfm/`  
**Bundled file:** `data/online_retail_II.csv.gz`

**Dataset:** Online Retail II  
**Original source:** UCI Machine Learning Repository  
**Creator:** Daqing Chen  
**DOI:** `10.24432/C5CG6D`  
**Source page:** https://archive.ics.uci.edu/dataset/502/online+retail+ii  
**License shown by UCI:** CC BY 4.0

The repository stores a compressed CSV representation for reproducibility. The data describe transactions from a UK-based non-store online retailer between December 2009 and December 2011.

---

## 2. Marketing Campaign Funnel & Channel Performance

**Project:** `marketing_campaign_funnel_analysis/`

**Dataset:** Marketing Campaign Performance Dataset  
**Source:** Kaggle  
**Source page:** https://www.kaggle.com/datasets/mirzayasirabdullah07/marketing-campaign-performance-dataset

The dataset is used as a portfolio analysis dataset and is not presented as proprietary data from a specific employer or client.

Refer to the source page for the dataset's current licensing and usage terms.

---

## 3. Commercial & CRM Operations Analysis

**Project:** `commercial_crm_excel_analytics/`  
**Bundled file:** `data/crm_sales_pipeline_raw.csv`

**Source type:** Synthetic portfolio data

The dataset was created for reproducible portfolio demonstration. It does not represent real customer, employer, or confidential business data.

The synthetic records are designed to support practical CRM analysis including source normalisation, pipeline health, funnel conversion, sales-rep performance, target attainment, and stale-opportunity analysis.

---

## 4. E-commerce Growth & Conversion Analytics

**Project:** `ecommerce_growth_conversion_power_bi/`  
**Bundled files:** CSV tables under `data/`

**Source type:** Deterministic synthetic GA4-style e-commerce data

The bundled dataset was created for reproducible Power BI portfolio use and is **not** presented as official Google production data.

The project also includes BigQuery SQL templates that document a compatible analytical pathway using Google's public GA4 Merchandise Store sample dataset.

**Google reference:**  
https://developers.google.com/analytics/bigquery/web-ecommerce-demo-dataset

The bundled synthetic CSVs and the public Google sample should be treated as separate data sources.

---

## 5. Supervised Learning — Regression & Classification

**Project:** `supervised_learning_regression_classification_r/`  
**Bundled files:**
- `data/energy_homes.csv`
- `data/learners.csv`

**Source type:** Coursework-provided datasets

The analysis describes `energy_homes.csv` as simulated residential-building data. The repository does not establish an external public source or redistribution license for these coursework-provided files.

Accordingly, these datasets are included only as supporting material for the reproduced analysis and are **not claimed as original data created or owned by the portfolio author**.

If a public version of the repository is distributed beyond assessment/portfolio review, the dataset files should be retained only where redistribution is permitted by the course/provider terms.

---

## 6. Insurance Risk Segmentation

**Project:** `insurance_risk_segmentation_sql/`  
**Bundled file:** `data/insurance.csv`

**Dataset:** Insurance dataset  
**Source:** Kaggle — `mirichoi0218/insurance`  
**Source page:** https://www.kaggle.com/datasets/mirichoi0218/insurance

The SQL workflow was tested with 1,338 raw rows and produces 1,337 final analytical rows after exact-duplicate removal.

Refer to the Kaggle source page for the dataset's current licensing and usage terms.

---

## 7. Product Affinity & Co-Purchase Network Analysis

**Project:** `product_affinity_network_analysis/`  
**Bundled file:** `data/raw/online_retail_II.csv.gz`

**Dataset:** Online Retail II  
**Original source:** UCI Machine Learning Repository  
**Creator:** Daqing Chen  
**DOI:** `10.24432/C5CG6D`  
**Source page:** https://archive.ics.uci.edu/dataset/502/online+retail+ii  
**License shown by UCI:** CC BY 4.0

This project uses the same underlying transaction dataset as the RFM project but answers a different question: repeated product co-purchase relationships rather than customer segmentation.

Large intermediate network files are regenerated locally and are not required to be distributed with the repository.

---

## 8. Australian Airline Performance Visual Analytics

**Project:** `airline_performance_visual_analytics/`  
**Bundled raw file:** `data/raw/Dataset Assignment 2.xlsx`

**Bundled-file provenance:** Coursework-provided workbook containing Australian domestic airline on-time performance data.

The underlying public statistics are published by the Australian Government's **Bureau of Infrastructure and Transport Research Economics (BITRE)**.

**BITRE reference:**  
https://www.bitre.gov.au/resource/aviation/airline-time-performance-monthly-reports-and-time-series-data

The bundled workbook is retained as the reproducible input used for this portfolio analysis. It should not be interpreted as an original dataset created by the portfolio author.

---

## Licensing Scope

Unless a project states otherwise:

- Original analysis code, project documentation, and portfolio-written material are covered by the repository's own license.
- Third-party and coursework-provided datasets remain subject to their original terms.
- A dataset being included in this repository does **not** transfer ownership or relicense that dataset under the repository license.
- Synthetic datasets created specifically for this portfolio are identified explicitly as synthetic.
