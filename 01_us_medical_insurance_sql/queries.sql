/* =====================================================================
   PROJECT: Insurance Charges Drivers & Risk Segmentation – SQL Analysis
   Author: Pham Minh Khoi
   Tool: DBeaver Ultimate | Database: PostgreSQL
   Scope: Portfolio (SQL-only), single business story
   Grain: 1 row = 1 customer record
   ===================================================================== */

/* =====================================================================
   0. PROJECT FRAME
   Business Story:
     Customer attributes (e.g., smoker, age, BMI) are associated with
     insurance charges. We quantify key drivers and identify high-cost segments.

   Core Questions:
     Q1. Which factors show the strongest association with higher charges?
     Q2. How do charges change across age and BMI levels?
     Q3. Which customer segments represent highest cost risk?

   Output Standard:
     - Each section returns 1–2 screenshot-ready tables max.
   ===================================================================== */

/* =====================================================================
   0A. SCHEMA & TYPE SANITY
   Goal:
     Confirm source table exists, verify column types, and check row count.
   ===================================================================== */

-- Confirm raw source table exists
SELECT
  table_schema,
  table_name
FROM information_schema.tables
WHERE table_catalog = 'insurance'
  AND table_schema = 'raw'
  AND table_name = 'insurance'
  AND table_type = 'BASE TABLE'
ORDER BY table_schema, table_name;

-- Inspect column names and data types
SELECT
  column_name,
  data_type,
  COALESCE(character_maximum_length::text, '-') AS char_len
FROM information_schema.columns
WHERE table_catalog = 'insurance'
  AND table_schema = 'raw'
  AND table_name = 'insurance'
ORDER BY ordinal_position;

-- Row count
SELECT COUNT(*) AS row_cnt
FROM raw.insurance;
   ===================================================================== */

/* =====================================================================
   1. BUILD ANALYSIS-READY TABLE (CUSTOMER-LEVEL)
   Goal:
     Standardize types and clean categorical fields.
     Derive:
       - is_smoker (0/1)
       - age_bucket
       - bmi_bucket

   Expected Output Columns:
     age
     sex
     bmi
     children
     smoker
     region
     charges
     is_smoker
     age_bucket
     bmi_bucket
   ===================================================================== */

/* =====================================================================
   2. DATA QUALITY CHECKS
   Checks:
     - Row count
     - Missing values by column
     - Out-of-range sanity checks (age, bmi, charges)
     - Category standardization validation (sex/smoker/region)

   Expected Outputs:
     - Summary counts table
     - Anomaly count + sample rows (LIMIT 20)
   ===================================================================== */

/* =====================================================================
   3. BASELINE METRICS (SANITY KPIs)
   KPIs:
     - Total customers
     - Smoker rate
     - Avg/Median charges
     - Avg age, avg BMI

   Expected Outputs:
     - 1 KPI table (single row)
   ===================================================================== */

/* =====================================================================
   4. CORE RELATIONSHIP: SMOKER VS CHARGES
   Analysis:
     - Charges summary by is_smoker
       count_customers
       avg_charges
       median_charges
       p90_charges (optional)

   Expected Outputs:
     - 1 main summary table
   ===================================================================== */

/* =====================================================================
   5. INTERACTION: BMI BUCKET x SMOKER
   Analysis:
     - Charges summary by (bmi_bucket, is_smoker)
       n
       avg_charges
       median_charges

   Expected Outputs:
     - 1 summary table
   ===================================================================== */

/* =====================================================================
   6. SEGMENTATION: HIGH-COST RISK GROUPS
   Analysis:
     - Segment by (age_bucket, bmi_bucket, is_smoker)
     - Rank top 10 segments by median_charges (or avg)

   Expected Outputs:
     - Top 10 segments table
   ===================================================================== */

/* =====================================================================
   7. SYNTHESIS (FINAL TABLES FOR README)
   Goal:
     Produce final presentation-ready outputs:
       - Key Findings table (smoker + bmi interaction)
       - Top Risk Segments table

   Expected Outputs:
     - 2 final tables, stable formatting
   ===================================================================== */

/* =====================================================================
   8. END OF FILE
   Notes:
     - Keep queries ordered by sections above.
     - Keep outputs screenshot-ready.
   ===================================================================== */
