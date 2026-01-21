# Medical Insurance Charges — Exploratory Data Analysis (Python)

**Project type:** Exploratory Data Analysis (EDA)  
**Focus:** Identifying key factors associated with higher medical insurance charges  
**Tools:** Python (pandas, matplotlib)  

---

## 1. Business Context
Medical insurance charges vary significantly across individuals. Understanding which customer attributes are associated with higher charges can support better decision-making in **risk segmentation**, **pricing discussions**, and **customer profiling**.

This project explores how key variables (e.g., smoking status, age, BMI) relate to insurance charges using a structured EDA workflow.

---

## 2. Project Objectives
This analysis answers the following questions:

- How do insurance charges differ between **smokers vs non-smokers**?
- How do charges change across **age** and **BMI** levels?
- Which customer segments show the **highest cost risk**?

> Note: This is an observational analysis and does not establish causality.

---

## 3. Dataset
**Source:** Kaggle — *Insurance Dataset* by mirichoi0218  
https://www.kaggle.com/datasets/mirichoi0218/insurance

**Dataset description (from source):**  
Customer attributes and medical insurance charges.

**Columns:**
- `age` — age of primary beneficiary  
- `sex` — insurance contractor gender (`male`, `female`)  
- `bmi` — body mass index  
- `children` — number of dependents covered  
- `smoker` — smoking status (`yes`, `no`)  
- `region` — beneficiary region (`northeast`, `northwest`, `southeast`, `southwest`)  
- `charges` — individual medical costs billed by health insurance  

---

## 4. Analytical Workflow
The notebook follows a structured EDA process:

1. **Data loading & schema validation**  
   - Confirm dataset shape, column types, and value formats

2. **Data quality checks**  
   - Missing values  
   - Duplicate records  
   - Basic sanity checks (range and category validation)

3. **Univariate analysis**  
   - Distributions of numeric variables (age, BMI, charges)  
   - Frequency breakdown of categorical variables (sex, smoker, region)

4. **Bivariate / relationship analysis**  
   - Charges vs smoker status  
   - Charges vs age  
   - Charges vs BMI  
   - Charges vs number of children  
   - Correlation analysis (with interpretation caution due to skewness)

5. **Segmentation insights**  
   - Compare patterns within smoker vs non-smoker groups  
   - Identify high-cost risk segments

---

## 5. Key Findings (Summary)
- **Smoking status shows a strong association with higher insurance charges**, with smokers consistently paying much more than non-smokers.
- **Charges generally increase with age**, and the smoker vs non-smoker gap becomes more pronounced in older groups.
- **BMI shows a weaker overall relationship with charges**, but becomes more informative when analyzing specific segments (especially smokers).
- The distribution of `charges` is **right-skewed**, so both **average and median** summaries are used for interpretation.

---

## 6. Business Implications
- Smoking status is a high-impact attribute for **risk segmentation** and potential **pricing differentiation**.
- Age-based segmentation can improve identification of high-cost groups, especially when combined with smoker status.
- BMI may be more useful as a supporting feature within subgroups rather than a standalone predictor.

---

## 7. Limitations
- This analysis is **observational** and does not prove causal relationships.
- The dataset does not include medical history, claim details, or behavioral variables beyond smoking status.
- Charges are heavily skewed; results should be interpreted with robust statistics (median/percentiles) rather than mean alone.

---

## 8. Repository Structure
- `analysis.ipynb` — main EDA notebook  
- `data/insurance.csv` — dataset  
- `README.md` — project overview  

---

## 9. How to Run
1. Install required libraries:
   ```bash
   pip install pandas matplotlib
