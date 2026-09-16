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

-- (Optional) Confirm current database/session context
SELECT
  current_database() AS current_db,
  current_schema()   AS current_schema,
  current_user       AS current_user;

-- Confirm raw source table exists
SELECT
  table_schema,
  table_name,
  table_type
FROM information_schema.tables
WHERE table_schema = 'raw'
  AND table_name   = 'insurance'
  AND table_type   = 'BASE TABLE'
ORDER BY table_schema, table_name;

-- Inspect column names and data types
SELECT
  ordinal_position,
  column_name,
  data_type,
  COALESCE(character_maximum_length::text, '-') AS char_len,
  COALESCE(numeric_precision::text, '-')        AS num_precision,
  COALESCE(numeric_scale::text, '-')            AS num_scale
FROM information_schema.columns
WHERE table_schema = 'raw'
  AND table_name   = 'insurance'
ORDER BY ordinal_position;

-- Row count
SELECT COUNT(*) AS row_cnt
FROM raw.insurance;

/* ===================================================================== */

/* =====================================================================
   1. BUILD ANALYSIS-READY VIEW (CUSTOMER-LEVEL)
   Goal:
     Standardize categorical fields and derive analysis buckets.
   Output:
     analytics.v_insurance_clean
   ===================================================================== */

-- 1A) Create analytics schema (safe to re-run)
CREATE SCHEMA IF NOT EXISTS analytics;

-- 1B) Create analysis-ready view
CREATE OR REPLACE VIEW analytics.v_insurance_clean AS
WITH base AS (
  SELECT
    age,
    LOWER(TRIM(sex))    AS sex,
    bmi,
    children,
    LOWER(TRIM(smoker)) AS smoker,
    LOWER(TRIM(region)) AS region,
    charges
  FROM raw.insurance
)
SELECT
  age,
  sex,
  bmi,
  children,
  smoker,
  region,
  charges,

  /* binary flag */
  CASE WHEN smoker = 'yes' THEN 1 ELSE 0 END AS is_smoker,

  /* age bucket (analyst-defined; stable for portfolio) */
  CASE
    WHEN age BETWEEN 18 AND 25 THEN '18-25'
    WHEN age BETWEEN 26 AND 35 THEN '26-35'
    WHEN age BETWEEN 36 AND 45 THEN '36-45'
    WHEN age BETWEEN 46 AND 55 THEN '46-55'
    ELSE '56+'
  END AS age_bucket,

  /* BMI bucket using common WHO cutoffs */
  CASE
    WHEN bmi < 18.5 THEN 'Underweight'
    WHEN bmi < 25   THEN 'Normal'
    WHEN bmi < 30   THEN 'Overweight'
    ELSE 'Obese'
  END AS bmi_bucket

FROM base;

-- 1C) Quick preview (screenshot-ready)
SELECT *
FROM analytics.v_insurance_clean
LIMIT 20;

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

-- 2A) Summary counts: row count + missing by column + basic sanity counts
SELECT
  COUNT(*) AS row_cnt,

  /* missing checks */
  SUM(CASE WHEN age      IS NULL THEN 1 ELSE 0 END) AS missing_age,
  SUM(CASE WHEN sex      IS NULL OR sex = '' THEN 1 ELSE 0 END) AS missing_sex,
  SUM(CASE WHEN bmi      IS NULL THEN 1 ELSE 0 END) AS missing_bmi,
  SUM(CASE WHEN children IS NULL THEN 1 ELSE 0 END) AS missing_children,
  SUM(CASE WHEN smoker   IS NULL OR smoker = '' THEN 1 ELSE 0 END) AS missing_smoker,
  SUM(CASE WHEN region   IS NULL OR region = '' THEN 1 ELSE 0 END) AS missing_region,
  SUM(CASE WHEN charges  IS NULL THEN 1 ELSE 0 END) AS missing_charges,

  /* out-of-range sanity checks (conservative thresholds) */
  SUM(CASE WHEN age < 0 OR age > 120 THEN 1 ELSE 0 END) AS bad_age_range,
  SUM(CASE WHEN bmi <= 0 OR bmi > 80 THEN 1 ELSE 0 END) AS bad_bmi_range,
  SUM(CASE WHEN charges <= 0 OR charges > 200000 THEN 1 ELSE 0 END) AS bad_charges_range

FROM analytics.v_insurance_clean;

-- 2B) Anomaly check result (expect "no_anomalies")

WITH anomalies AS (
  SELECT
    CASE
      WHEN age IS NULL THEN 'missing_age'
      WHEN sex IS NULL OR sex = '' THEN 'missing_sex'
      WHEN bmi IS NULL THEN 'missing_bmi'
      WHEN children IS NULL THEN 'missing_children'
      WHEN smoker IS NULL OR smoker = '' THEN 'missing_smoker'
      WHEN region IS NULL OR region = '' THEN 'missing_region'
      WHEN charges IS NULL THEN 'missing_charges'
      WHEN age < 0 OR age > 120 THEN 'bad_age_range'
      WHEN bmi <= 0 OR bmi > 80 THEN 'bad_bmi_range'
      WHEN charges <= 0 OR charges > 200000 THEN 'bad_charges_range'
      WHEN sex NOT IN ('male','female') THEN 'bad_sex_category'
      WHEN smoker NOT IN ('yes','no') THEN 'bad_smoker_category'
      WHEN region NOT IN ('northeast','northwest','southeast','southwest') THEN 'bad_region_category'
      ELSE NULL
    END AS anomaly_type
  FROM analytics.v_insurance_clean
)
SELECT
  COALESCE(anomaly_type, 'no_anomalies') AS anomaly_type,
  COUNT(*) AS anomaly_cnt
FROM anomalies
GROUP BY COALESCE(anomaly_type, 'no_anomalies')
ORDER BY anomaly_cnt DESC;

-- 2C) Duplicate check (exact full-row duplicates)

SELECT
  COUNT(*) AS total_rows,
  COUNT(DISTINCT (age, sex, bmi, children, smoker, region, charges)) AS distinct_rows,
  COUNT(*) - COUNT(DISTINCT (age, sex, bmi, children, smoker, region, charges)) AS duplicate_rows
FROM analytics.v_insurance_clean;

-- Duplicate rows detail (show duplicated groups)

SELECT
  age, sex, bmi, children, smoker, region, charges,
  COUNT(*) AS dup_count
FROM analytics.v_insurance_clean
GROUP BY age, sex, bmi, children, smoker, region, charges
HAVING COUNT(*) > 1
ORDER BY dup_count DESC, charges DESC;

-- 2D) Final analysis layer (deduplicated)

CREATE OR REPLACE VIEW analytics.v_insurance_final AS
SELECT DISTINCT *
FROM analytics.v_insurance_clean;

-- Confirm final row count after dedup

SELECT COUNT(*) AS final_row_cnt
FROM analytics.v_insurance_final;



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

SELECT
  COUNT(*) AS total_customers,

  /* smoker rate */
  ROUND(100.0 * AVG(is_smoker)::numeric, 2) AS smoker_rate_pct,

  /* charges */
  ROUND(AVG(charges)::numeric, 2) AS avg_charges,
  ROUND(
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY charges)::numeric
  , 2) AS median_charges,

  /* customer attributes */
  ROUND(AVG(age)::numeric, 2) AS avg_age,
  ROUND(AVG(bmi)::numeric, 2) AS avg_bmi

FROM analytics.v_insurance_final;


/* =====================================================================
   4. CORE RELATIONSHIP: SMOKER VS CHARGES 
   Analysis:
     - Charges summary by is_smoker
       count_customers
       avg_charges
       median_charges
       p90_charges
     - Add lift metrics vs overall + vs non-smoker

   Expected Outputs:
     - 1 main summary table
   ===================================================================== */

WITH overall AS (
  SELECT
    AVG(charges) AS overall_avg,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY charges) AS overall_median
  FROM analytics.v_insurance_final
),
by_smoker AS (
  SELECT
    is_smoker,
    COUNT(*) AS count_customers,
    AVG(charges) AS avg_charges,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY charges) AS median_charges,
    PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY charges) AS p90_charges
  FROM analytics.v_insurance_final
  GROUP BY is_smoker
),
pivot AS (
  SELECT
    MAX(CASE WHEN is_smoker = 0 THEN avg_charges END)    AS avg_non_smoker,
    MAX(CASE WHEN is_smoker = 1 THEN avg_charges END)    AS avg_smoker,
    MAX(CASE WHEN is_smoker = 0 THEN median_charges END) AS median_non_smoker,
    MAX(CASE WHEN is_smoker = 1 THEN median_charges END) AS median_smoker
  FROM by_smoker
)
SELECT
  CASE WHEN b.is_smoker = 1 THEN 'smoker' ELSE 'non_smoker' END AS smoker_group,
  b.count_customers,

  ROUND(b.avg_charges::numeric, 2)    AS avg_charges,
  ROUND(b.median_charges::numeric, 2) AS median_charges,
  ROUND(b.p90_charges::numeric, 2)    AS p90_charges,

  /* lifts vs overall */
  ROUND((b.avg_charges / o.overall_avg)::numeric, 2)       AS avg_lift_vs_overall_x,
  ROUND((b.median_charges / o.overall_median)::numeric, 2) AS median_lift_vs_overall_x,

  /* lifts vs non-smoker (only meaningful for smoker row; still shown for both) */
  ROUND((b.avg_charges / p.avg_non_smoker)::numeric, 2)       AS avg_lift_vs_non_smoker_x,
  ROUND((b.median_charges / p.median_non_smoker)::numeric, 2) AS median_lift_vs_non_smoker_x

FROM by_smoker b
CROSS JOIN overall o
CROSS JOIN pivot p
ORDER BY b.is_smoker;


/* =====================================================================
   5. INTERACTION: BMI BUCKET x SMOKER 
   Analysis:
     - Charges summary by (bmi_bucket, is_smoker)
       n
       avg_charges
       median_charges
     - Upgrades:
       - % of total customers (segment size context)
       - Smoker lift vs non-smoker within the same BMI bucket (avg + median)

   Expected Outputs:
     - 1 summary table
   ===================================================================== */

WITH overall AS (
  SELECT COUNT(*)::numeric AS total_customers
  FROM analytics.v_insurance_final
),
grp AS (
  SELECT
    bmi_bucket,
    is_smoker,
    COUNT(*) AS n,
    AVG(charges) AS avg_charges,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY charges) AS median_charges
  FROM analytics.v_insurance_final
  GROUP BY bmi_bucket, is_smoker
),
pivot AS (
  SELECT
    bmi_bucket,
    MAX(CASE WHEN is_smoker = 0 THEN n END) AS n_non_smoker,
    MAX(CASE WHEN is_smoker = 1 THEN n END) AS n_smoker,
    MAX(CASE WHEN is_smoker = 0 THEN avg_charges END) AS avg_non_smoker,
    MAX(CASE WHEN is_smoker = 1 THEN avg_charges END) AS avg_smoker,
    MAX(CASE WHEN is_smoker = 0 THEN median_charges END) AS median_non_smoker,
    MAX(CASE WHEN is_smoker = 1 THEN median_charges END) AS median_smoker
  FROM grp
  GROUP BY bmi_bucket
)
SELECT
  p.bmi_bucket,

  /* segment size */
  p.n_non_smoker,
  p.n_smoker,
  (p.n_non_smoker + p.n_smoker) AS n_total_in_bucket,
  ROUND(100.0 * (p.n_non_smoker + p.n_smoker) / o.total_customers, 2) AS pct_of_total_customers,

  /* level metrics */
  ROUND(p.avg_non_smoker::numeric, 2) AS avg_charges_non_smoker,
  ROUND(p.avg_smoker::numeric, 2)     AS avg_charges_smoker,
  ROUND(p.median_non_smoker::numeric, 2) AS median_charges_non_smoker,
  ROUND(p.median_smoker::numeric, 2)     AS median_charges_smoker,

  /* smoker lift within BMI bucket */
  ROUND((p.avg_smoker / NULLIF(p.avg_non_smoker, 0))::numeric, 2) AS avg_smoker_lift_x,
  ROUND((p.median_smoker / NULLIF(p.median_non_smoker, 0))::numeric, 2) AS median_smoker_lift_x

FROM pivot p
CROSS JOIN overall o
ORDER BY
  CASE p.bmi_bucket
    WHEN 'Underweight' THEN 1
    WHEN 'Normal' THEN 2
    WHEN 'Overweight' THEN 3
    WHEN 'Obese' THEN 4
    ELSE 99
  END;


/* =====================================================================
   6. SEGMENTATION: HIGH-COST RISK GROUPS 
   Analysis:
     - Segment by (age_bucket, bmi_bucket, is_smoker)
     - Rank top segments by median charges (robust to skew)
     - Upgrades:
       - Include segment size (% of total) for impact context
       - Include p90 charges to reflect high-cost tail
       - Apply a minimum segment size filter to avoid tiny/noisy segments

   Expected Outputs:
     - Top 10 segments table
   ===================================================================== */

WITH overall AS (
  SELECT COUNT(*)::numeric AS total_customers
  FROM analytics.v_insurance_final
),
seg AS (
  SELECT
    age_bucket,
    bmi_bucket,
    is_smoker,
    COUNT(*) AS n_customers,
    AVG(charges) AS avg_charges,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY charges) AS median_charges,
    PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY charges) AS p90_charges
  FROM analytics.v_insurance_final
  GROUP BY age_bucket, bmi_bucket, is_smoker
),
filtered AS (
  SELECT
    s.*,
    ROUND(100.0 * s.n_customers / o.total_customers, 2) AS pct_of_total_customers
  FROM seg s
  CROSS JOIN overall o
  WHERE s.n_customers >= 10
),
ranked AS (
  SELECT
    *,
    DENSE_RANK() OVER (ORDER BY median_charges DESC) AS risk_rank
  FROM filtered
)
SELECT
  risk_rank,
  age_bucket,
  bmi_bucket,
  CASE WHEN is_smoker = 1 THEN 'smoker' ELSE 'non_smoker' END AS smoker_group,
  n_customers,
  pct_of_total_customers,
  ROUND(avg_charges::numeric, 2)    AS avg_charges,
  ROUND(median_charges::numeric, 2) AS median_charges,
  ROUND(p90_charges::numeric, 2)    AS p90_charges
FROM ranked
WHERE risk_rank <= 10
ORDER BY risk_rank, n_customers DESC;

/* =====================================================================
   7. END OF FILE
   Notes:
     - Keep queries ordered by sections above.
     - Outputs are designed to be screenshot-ready for README.
     - Use analytics.v_insurance_final as the analysis source of truth.
   ===================================================================== */

