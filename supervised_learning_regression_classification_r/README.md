# Supervised Learning in R — Regression & Classification

**Tools:** R, R Markdown, `boot`, `pROC`  
**Focus:** model selection, cross-validation, diagnostics, ROC/AUC, threshold trade-offs

## Project Overview

This project applies a complete supervised-learning workflow to two prediction problems:

1. **Regression:** predict residential heating load from building-design characteristics.
2. **Classification:** predict whether an online learner will complete a course from early behavioural and performance variables.

The goal is not only to fit models, but to compare alternatives honestly and translate evaluation metrics into practical decisions.

## Part 1 — Heating Load Regression

Models evaluated:

- simple linear regression;
- polynomial regression;
- multiple regression;
- an interaction model;
- 10-fold cross-validation for model comparison.

A quadratic model improved the single-predictor relationship between glazing area and heating load, but the stronger final specification used multiple design variables.

### Final regression comparison

| Model | Adjusted R² | AIC | 10-fold CV MSE |
|---|---:|---:|---:|
| Model A | 0.9121 | 4010.293 | 10.8406 |
| Model B + `wall_area × glazing_area` | **0.9130** | **4003.650** | **10.7544** |

The interaction coefficient was statistically significant (`p = 0.0035`). Model B was preferred because it improved both training-fit criteria and out-of-sample error, although the improvement was modest.

## Part 2 — Learner Completion Classification

Dataset:

- 2,000 learners;
- 57.2% non-completers / 42.8% completers;
- stratified 80/20 train-test split.

The final logistic model used learner background, engagement, assessment, subscription, and device variables.

### Test performance at threshold 0.50

- Accuracy: **73.6%**
- Sensitivity: **64.5%**
- Specificity: **80.3%**
- AUC: **0.813**

10-fold cross-validated accuracy was **71.8%**, reasonably close to the single holdout result.

## Threshold Decision Example

| Completion threshold | Sensitivity | Specificity |
|---:|---:|---:|
| 0.50 | 0.645 | 0.803 |
| 0.60 | 0.535 | 0.878 |

Raising the threshold identifies more true non-completers but also flags more actual completers as at risk. This is a decision trade-off rather than a purely statistical optimisation problem.

## Why This Project Matters

The project demonstrates:

- regression versus classification framing;
- training fit versus out-of-sample performance;
- 10-fold cross-validation;
- interaction modelling;
- odds-ratio interpretation;
- confusion matrices;
- ROC/AUC;
- threshold selection based on operational costs.

## Files

```text
supervised_learning_regression_classification_r/
├── analysis/
│   └── supervised_learning_regression_classification.Rmd
├── report/
│   └── supervised_learning_regression_classification_report.pdf
└── README.md
```

The original course datasets are not redistributed in this public portfolio copy.
