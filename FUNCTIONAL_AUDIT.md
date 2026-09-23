# Portfolio Publication Audit

**Audit date:** 23 September 2026  
**Outcome:** PASS for public portfolio packaging  
**Career target:** entry-level Customer, CRM, Growth, Marketing, Product, or Commercial Analytics

## What changed

- Expanded the former RFM case into lifecycle state, repeat purchase, mature-cohort retention, CRM prioritisation, and a test plan.
- Added a complete checkout experimentation module to the product-funnel case: user-level randomisation, SRM, balance, 95% CI, p-value, 80% power MDE, guardrails, subgroup cautions, and a staged-rollout decision.
- Replaced the campaign source with deterministic synthetic data because the former third-party redistribution license was unclear.
- Removed duplicate nested Excel and Power BI project copies and local Power BI caches.
- Removed stale notebooks whose scope no longer matched the canonical scripts.
- Curated out the supervised-learning coursework project because it was less aligned to the career target, required a leakage correction, lacked clear raw-data redistribution permission, and could not be natively re-knitted in this environment. The original upload remains unchanged outside this public build.
- Excluded the coursework-packaged airline raw workbook while retaining the public BITRE attribution, processed analytical layer, Tableau workbook, scripts, figures, and report.
- Rebuilt the root README around three flagship decisions and four supporting proof projects.

## Automated publication gate

Command:

```bash
python scripts/audit_portfolio.py
```

Final result:

```text
PASS — customer lifecycle analysis completed
PASS — campaign analysis completed
PASS — experiment analysis completed
All QA checks passed.
PASS — portfolio publication audit completed
```

The automated gate verifies:

- exact seven-project scope;
- no embedded Git metadata, local Power BI caches, notebook checkpoints, or nested `FINAL` copies;
- no file at or above GitHub's 100 MiB limit;
- all local Markdown links resolve;
- no machine-specific user paths;
- Python syntax and notebook error-output checks;
- rerun of all three flagship Python analyses;
- rerun of the Power BI dataset validator;
- customer/revenue and cohort-range reconciliation;
- campaign data-quality and channel-metric checks;
- experiment SRM, pre-treatment balance, positive confidence interval, significance, and guardrail gates;
- presence of the intended recruiter fast path.

## Flagship results

| Flagship | Runtime status | Decision evidence |
|---|---|---|
| Customer Lifecycle & Retention | PASS | 5,878 unique customers; 72.39% repeat-customer rate; 47.59% eligible 90-day repeat; mature 1/3/6/12-month cohort metrics; lifecycle and CRM action tables reconcile to revenue |
| Campaign & Growth Performance | PASS | 10,000 deterministic records regenerate; zero missing/duplicate/date/funnel/negative-value failures; weighted CTR 4.20%, CAC $22.52, ROAS 3.35x |
| Product Funnel & Experimentation | PASS | Power BI dataset QA passes; experiment allocation 16,000/16,000, SRM p=1.000, all balance and guardrail gates pass, conversion 5.28%→6.06%, p=0.0027 |

## Supporting-project checks

### Commercial & CRM Excel

- Workbook contains ten sheets, ten structured tables, four charts, and 1,800 synthetic leads.
- Formula and displayed-value scan found no spreadsheet error tokens.
- Won revenue, open pipeline, weighted pipeline, win rate, average won deal, and stale-opportunity totals reconcile with supporting sheets.
- The duplicate nested `FINAL` workbook was removed; one canonical workbook remains.

### Insurance SQL

- Static SQL review covers schema setup, cleaning/final views, exact-duplicate control, safe division, CTEs, conditional segments, percentiles, interactions, and ranking.
- Included screenshots document the PostgreSQL execution path and row reconciliation.
- The supporting project is descriptive and does not claim that observed cost associations are causal.

### Product Affinity Network

- The executed notebook contains no error outputs.
- Independent Python execution reproduced 1,041,670 clean rows, 32,406 baskets, 2,076,826 raw edges, and the documented thresholded networks.
- The README states that co-occurrence is not the same as association strength or causality and identifies support/confidence/lift as the next extension.

### Airline R/Tableau

- Processed analytical data, report, figures, R Markdown scripts, and relative-path Tableau workbook remain inspectable.
- The raw coursework wrapper is not redistributed; an authorised-input instruction file links to the underlying BITRE public source.
- Native R rerun is not claimed in this environment. This project is supporting evidence rather than a flagship publication gate.

## Native-file boundary

The remaster did not modify the canonical Excel workbook, Power BI PBIP definitions, or Tableau workbook. Their previously validated native files and screenshots remain unchanged. The new retention, campaign, and experiment layers are independently reproducible with Python. Any future edit to a native workbook/report must be followed by the application spot checks in [`PUBLISHING_CHECKLIST.md`](PUBLISHING_CHECKLIST.md).

## Final rubric result

| Criterion | Status |
|---|---|
| North Star fit | PASS |
| Three-flagship completeness | PASS |
| Business framing and decision value | PASS |
| Metric correctness and quality controls | PASS |
| Retention/lifecycle depth | PASS |
| Experimentation/statistical reasoning | PASS |
| SQL/Excel/BI/Python evidence | PASS |
| Reproducibility and portability | PASS within declared native boundaries |
| Recruiter navigation | PASS |
| Repository hygiene | PASS |
| Synthetic-data disclosure and causal boundaries | PASS |
| Public-data packaging | PASS with external-source attribution and coursework raw input excluded |

**Release decision:** the portfolio is ready to use as the evidence base for CV construction. The CV should feature the three flagship projects and treat the remaining four as supporting proof rather than listing all projects equally.
