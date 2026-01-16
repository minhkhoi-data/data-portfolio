# 🧾 Insurance Charges Drivers & Risk Segmentation (SQL)

**Project type:** SQL Analytics Case Study (Portfolio)  
**Focus:** Key drivers of insurance charges and high-cost risk segmentation  
**Tools:** PostgreSQL, DBeaver Ultimate  

---

## 1. Business Context
Insurance pricing and underwriting decisions rely on understanding which customer attributes are associated with higher expected medical costs. Factors such as smoking status, age, and BMI are commonly linked to health risk and can materially impact insurance charges.

This project analyzes how customer attributes relate to insurance charges and identifies high-cost risk segments that may require pricing adjustment, risk controls, or targeted interventions.

---

## 2. Project Scope
This SQL-based analysis examines the relationship between customer attributes and insurance charges using a public insurance dataset.

**Key questions explored:**
- Which factors are most strongly associated with higher insurance charges (e.g., smoker vs non-smoker)?
- How do charges vary across age and BMI levels?
- Which customer segments represent the highest cost risk?

The analysis is intentionally constrained to **SQL only**, reflecting analytics environments where SQL is the primary analysis tool.

---

## 3. Dataset
**Source:** Kaggle — *Insurance Dataset* by mirichoi0218  
https://www.kaggle.com/datasets/mirichoi0218/insurance

**Database:** `insurance`  
**Schema / Table:** `raw.insurance`

**Core fields used:**
- `age`
- `sex`
- `bmi`
- `children`
- `smoker`
- `region`
- `charges`

All analyses are conducted at the **customer level** after type validation and data quality checks.

---

## 4. Data Quality Checks
Before analysis, the dataset is validated for common data quality issues:
- Missing or invalid values (age, bmi, charges)
- Out-of-range values (sanity thresholds)
- Category consistency for text fields (sex, smoker, region)
- Duplicate records (if present)

The goal is to ensure that observed patterns are not driven by data errors or inconsistent formatting.

---

## 5. Analytical Approach
The workflow follows a structured SQL approach:

1. Validate dataset structure and data types  
2. Run data quality and distribution checks  
3. Compute baseline KPIs for charges and population composition  
4. Compare charges across key drivers (smoking status, BMI bucket, age bucket)  
5. Produce risk segmentation tables for high-cost groups  

Both **average and median** statistics are used to reduce sensitivity to skewness.

---

## 6. Outputs Produced (Final Tables)
The final outputs are designed to be presentation-ready tables:

- **Baseline Summary KPIs**
  - total customers, average/median charges, percentiles (optional)

- **Charges by Smoking Status**
  - count, average/median charges, high-cost tail indicators

- **Charges by Age Bucket**
  - distribution of charges across age segments

- **Charges by BMI Bucket**
  - distribution of charges across BMI segments

- **High-Risk Segment Table**
  - smoker × BMI bucket × age bucket ranking by median charges / high-cost percentiles

---

## 7. Business Implications
- Smoking status and BMI are strong candidates for risk-based pricing differentiation.
- High-cost segments can be prioritized for underwriting controls or prevention-focused programs.
- Segment-level monitoring helps identify where cost risk concentrates.

---

## 8. Limitations
- Observational associations only; no causal inference.
- Dataset lacks medical history and claims details, limiting explanatory depth.
- Bucket thresholds are analyst-defined and may vary by insurer policy.

---

## 9. How to Run
1. Load the dataset into PostgreSQL as `raw.insurance`
2. Open `queries.sql` in DBeaver
3. Run queries from top to bottom (each section outputs 1–2 final tables)

---

## 10. Tools & SQL Features
- PostgreSQL  
- DBeaver Ultimate  
- SQL: CTEs, aggregations, CASE bucketing, window functions, `percentile_cont()` for median
