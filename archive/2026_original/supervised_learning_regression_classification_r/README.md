# Supervised Learning — Regression & Classification

**Tools:** R, R Markdown, `boot`, `pROC`  
**Focus:** model selection, diagnostics, cross-validation, ROC/AUC, and threshold trade-offs

## Business Question

How should predictive models be selected and evaluated when the outcome is continuous versus binary?

This project uses two supervised-learning tasks to demonstrate the full reasoning chain from data inspection and model specification through validation and interpretation:

1. **Regression:** predict residential heating load from building-design characteristics.
2. **Classification:** predict learner course completion from early behavioural and performance variables.

---

## Part 1 — Heating Load Regression

The regression workflow compares:

- simple linear regression
- polynomial regression
- multiple regression
- an interaction model
- 10-fold cross-validation

### Final model comparison

| Model | Adjusted R² | AIC | 10-fold CV MSE |
|---|---:|---:|---:|
| Model A | 0.9121 | 4010.293 | 10.8406 |
| Model B + `wall_area × glazing_area` | **0.9130** | **4003.650** | **10.7544** |

The interaction term is statistically significant (`p ≈ 0.0035`). Model B is preferred because it produces slightly better fit statistics and slightly lower estimated out-of-sample error.

The improvement is modest, so the project treats this as an incremental gain rather than a dramatic change in predictive performance.

---

## Part 2 — Learner Completion Classification

The classification dataset contains:

- **2,000 learners**
- **57.2% non-completers**
- **42.8% completers**
- a stratified **80/20 train-test split**

The final logistic model uses learner background, engagement, assessment, subscription, device, and verification variables.

### Test performance at threshold 0.50

| Metric | Result |
|---|---:|
| Accuracy | **73.6%** |
| Sensitivity | **64.5%** |
| Specificity | **80.3%** |
| AUC | **0.813** |

The AUC indicates useful separation between completers and non-completers, while the threshold analysis shows why classification decisions should depend on the operational cost of false positives and false negatives.

### Threshold trade-off

| Completion threshold | Sensitivity | Specificity |
|---:|---:|---:|
| 0.50 | 0.645 | 0.803 |
| 0.60 | 0.535 | 0.878 |

Raising the threshold increases specificity but reduces sensitivity. The project therefore treats threshold selection as a decision problem rather than a purely statistical optimisation step.

---

## Techniques Demonstrated

- exploratory data inspection
- missing-value handling
- simple and multiple linear regression
- polynomial regression
- interaction terms
- model diagnostics
- adjusted R² and AIC
- 10-fold cross-validation
- logistic regression
- odds-ratio interpretation
- confusion matrices
- sensitivity and specificity
- ROC curve and AUC
- threshold adjustment
- reproducible train-test splitting

---

## Reproducibility

The analysis uses project-relative paths:

```text
../data/energy_homes.csv
../data/learners.csv
```

Required R packages:

```r
install.packages(c("boot", "pROC"))
```

PDF output also requires a LaTeX installation. The final runtime test used TinyTeX successfully.

A fixed seed of **599** is used for procedures involving random folds or train-test splitting.

To reproduce:

1. Open `analysis/supervised_learning_regression_classification.Rmd` in RStudio.
2. Install `boot` and `pROC` if required.
3. Ensure a LaTeX distribution such as TinyTeX is available for PDF output.
4. Knit the document from top to bottom.

The final runtime test produced a complete **35-page PDF** without R execution errors.

---

## Data

Bundled files:

```text
data/energy_homes.csv
data/learners.csv
```

These are coursework-provided datasets used for the reproduced analysis. They are not presented as original data owned by the portfolio author.

Repository-wide provenance and licensing notes are documented in [`../DATA_SOURCES.md`](../DATA_SOURCES.md).

---

## Project Structure

```text
supervised_learning_regression_classification_r/
├── analysis/
│   └── supervised_learning_regression_classification.Rmd
├── data/
│   ├── energy_homes.csv
│   └── learners.csv
├── report/
│   └── supervised_learning_regression_classification.pdf
└── README.md
```

---

## Limitations

- The project is designed to demonstrate supervised-learning workflow rather than production deployment.
- Regression assumptions are reasonably acceptable but not perfectly satisfied.
- The learner-classification results depend partly on the specific train-test split.
- Threshold selection should be tied to real intervention costs before operational use.
- Predictive associations should not be interpreted as causal effects.
