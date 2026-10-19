# Criteria v2 audit — Customer Lifecycle, RFM & Retention Remaster 1.0.2

Original audit: 2026-10-05. Recheck: 2026-10-07 (Asia/Ho_Chi_Minh). The locked scope is `audit/SCOPE.md`; the governing checklist is `audit/CRITERIA_V2.md`. The checked source is the bundled `data/online_retail_II.csv.gz`, SHA-256 `88703abba52824ab26c0f107fb8104637c5dc3a199c6cc5f180a980ea1c78c45`. The tested Python environment and rule hash are recorded in `outputs/run_summary.json`; the final file hashes are in `audit/release_manifest.json`.

The artifact verdict is **VERIFIED within the declared static Python scope**. All applicable artifact criteria pass; two native/interactive criteria are N/A because the project makes no such claim. Interview readiness is **BLOCKED** only for HR-01–HR-03 because reading an artifact cannot prove that the applicant can explain it or describe personal versus AI-assisted contribution. No FAIL remains in scope after the 1.0.2 repairs. The initial 1.0 ZIP omitted the linked duplicate sensitivity artifact; its earlier VERIFIED verdict was premature. Release 1.0.1 fixes publication and validates links after notebook refresh.

## Evidence run

- `python3 analysis/run_analysis.py` completed and published 5,878 customer rows, 36,969 purchase invoices and the regenerated figures/memo. The exact fresh-run output is `audit/fresh_run.log`.
- `python3 -m unittest discover -s tests -v` passed 12 semantic fixtures; the transcript is `audit/unit_tests.log`.
- `python3 analysis/validate_project.py` passed 45 independent SQL, sensitivity, source-hash, link and fail-closed checks; the record is `audit/independent_validation.json`.
- `python3 analysis/execute_notebook.py` executed all 9 code cells in a new Jupyter kernel with no cell errors. The managed runtime selects a network-free mode; the run used a fresh in-process kernel; this is recorded rather than presented as a subprocess run in `audit/notebook_execution.json`.
- `audit/fresh_run_comparison.json` compares a separate clean run against all 26 notebook-refreshed generated files byte-for-byte.
- `python analysis/verify_release.py` passed 68 additional independent checks without importing production functions: every customer column, all order keys/times/values, raw-value quantile cutoffs, RFM/lifecycle/value/action labels, summaries and every cohort cell.
- Official UCI source was downloaded again on 2026-10-07 and all 1,067,371 rows ×8 fields compared. Zero mismatches after documented normalization; audit/source_reverification.json records hashes and timing.
- Static visual QA is recorded in `audit/visual_review.json`; no browser/frontend or native workbook certification is claimed.
- Source attribution and the official UCI workbook comparison are recorded in `DATA_SOURCES.md` and `audit/source_verification.json`.

## Status counts

| Scope | PASS | FAIL | BLOCKED | N/A | N (PASS+FAIL+BLOCKED) | Pass rate | Assessment coverage |
|---|---:|---:|---:|---:|---:|---:|---:|
| All 68 in-scope criteria (including 2 N/A rows) | 63 | 0 | 3 | 2 | 66 | 95.45% | 95.45% |

N/A is excluded from the denominators. The 3 BLOCKED rows are the personal HR checks HR-01–HR-03. The 2 N/A rows are RUN-03 (no native Excel/BI/R/Tableau deliverable promised) and OUT-02 (no interactive dashboard/filter claim). PASS rate is a progress measure, not a scientific quality score.

## Criterion matrix

| ID | Applicability | Verdict | Evidence and observation | Retest / resolution |
|---|---|---|---|---|
| AUD-01 | Yes | PASS | `audit/SCOPE.md` locks purpose, claims, audience, inputs, outputs, dependencies and applied IDs before this report. | Scope and criteria hashes are carried in the release manifest. |
| AUD-02 | Yes | PASS | This matrix covers all AUD, common and CUS IDs; every row records a verdict and evidence. | No criterion was silently skipped; N/A reasons are explicit. |
| AUD-03 | Yes | PASS | Independent SQL, fixture tests, source workbook comparison, fresh-run byte comparison and environment records are separate from the implementation. | `audit/independent_validation.json`, `audit/extended_validation.json`, `audit/fresh_run_comparison.json`. |
| AUD-04 | Yes | PASS | `audit/CLAIM_EVIDENCE_LEDGER.md` lists high-risk claims; tests cover ties, boundaries, censoring, credits, malformed input and duplicate sensitivity. | Counterexamples pass; unsupported causal/profit claims were removed. |
| AUD-05 | Yes | PASS | `audit/CHANGELOG.md` records material fixes and why; this report separates artifact from interview verdict. | Retest logs and final manifest freeze the checked release. |
| BUS-01 | Yes | PASS | README and memo state the CRM/marketing analyst decision: which historical customer histories justify review or a test. | Scope excludes measured uplift, profit, CLV and production deployment. |
| BUS-02 | Yes | PASS | `docs/METHODS.md` maps invoice lines → orders → customers → lifecycle/RFM → conditional test audiences; the available fields support descriptive decisions only. | Claims were narrowed where data cannot answer them. |
| BUS-03 | Yes | PASS | `audit/SCOPE.md`, `DATA_SOURCES.md` and `outputs/run_summary.json` define UK retailer, source period, GBP, source-local timestamps and identified purchase customers. | Coverage limits appear next to the memo decisions. |
| BUS-04 | Yes | PASS | Methods, notebook and memo give each preparation, lifecycle, RFM, repeat, cohort and action component a separate input/output role. | Crosswalk and ledger connect analysis to decisions. |
| BUS-05 | Yes | PASS | Scope defines required outputs and checks; the release has runnable code, notebook, tables, figures, memo and audit records. | Fresh run and independent checks complete the acceptance test. |
| SRC-01 | Yes | PASS | `DATA_SOURCES.md` identifies UCI Online Retail II, DOI, official URL, workbook sheets and local/input hashes. | `audit/source_verification.json` and `audit/source_reverification.json` compare all 1,067,371 rows; source acquisition/reverification date is recorded. |
| SRC-02 | Yes | PASS | Methods define raw invoice/product line grain, customer/invoice order key and one-row-per-customer output. | SQL population, invoice count and uniqueness reconcile. |
| SRC-03 | Yes | PASS | Methods document signed quantity, GBP unit price, source-local timestamp, nominal Customer ID and unused Description/Country semantics. | Source schema and parser checks are recorded in outputs. |
| SRC-04 | Yes | PASS | Missing customer IDs (245,007), credit-only customers, partial months and wholesale/missing-coverage limits are quantified and disclosed. | `outputs/data_quality_summary.csv`, `DATA_SOURCES.md`. |
| SRC-05 | Yes | PASS | UCI CC BY 4.0 attribution is retained; no contact data, secrets or private identities are included. | License/PII boundaries are in `DATA_SOURCES.md` and README. |
| CLN-01 | Yes | PASS | `docs/METHODS.md` gives a business reason for each sequential exclusion, credit sign rule and duplicate assumption. | `outputs/cleaning_reconciliation.csv` records each stage. |
| CLN-02 | Yes | PASS | Row/value ledgers reconcile raw, retained and removed values; value reconciliation separates analysed and credit-only populations. | Fixture plus independent SQL checks pass within GBP 0.01. |
| CLN-03 | Yes | PASS | Blanks, exact duplicates, credits, cancellations, nonpositive prices and unusual large valid orders are handled by explicit rules. | Duplicate-retention sensitivity changes 55 actions and is disclosed. |
| CLN-04 | Yes | PASS | Positive lines are aggregated to distinct customer/invoice orders; ambiguous multi-customer or cross-date invoices fail validation. | `orders.csv` and SQL aggregation reconcile 36,969 invoices. |
| CLN-05 | Yes | PASS | Raw input, prepared purchase/credit lines, orders, customer table, config and output mappings are retained. | Input/config hashes and lineage appear in `run_summary.json` and METHODS. |
| CLN-06 | Yes | PASS | Dates/numerics use strict parsing; failures, invalid IDs, nonfinite values and signs are counted rather than silently coerced. | Parser fixtures and `data_quality_summary.csv` pass; out-of-range IDs/quantities are excluded before conversion rather than wrapped. |
| MET-01 | Yes | PASS | Methods define numerator, denominator and eligibility for orders, repeat rates, cohorts, R/F/M and value tiers. | Output names and independent SQL use the same definitions. |
| MET-02 | Yes | PASS | Gross purchases, recorded credits and net recorded value are named with GBP units; profit, margin and CLV are explicitly excluded. | Memo and README use the bounded terms consistently. |
| MET-03 | Yes | PASS | Mature repeat is pooled 2,486/5,281; cohort KPIs use weighted active/customers rather than averaging cohort rates. | SQL month-1/3/6/12 counts match retention outputs. |
| MET-04 | Yes | PASS | Reconciliation, SQL, bounds, exact fixtures, duplicate sensitivity and source checks independently recompute material totals. | `audit/independent_validation.json` contains 45 PASS checks; `audit/extended_validation.json` contains 68 additional independent checks. |
| MET-05 | Yes | PASS | Exact elapsed timestamps govern 90-day repeat; snapshot, complete-month policy and source-local timezone are documented. | Boundary and fresh-run checks pass. |
| MET-06 | Yes | PASS | Future/partial cohort cells are blank/NaN and grey; no-eligible repeat rates remain undefined rather than zero. | `test_future_cohorts_nan_and_observed_zero`, `test_no_eligible_not_zero`. |
| ANA-01 | Yes | PASS | Methods justify lifecycle, RFM, repeat curve and cohorts as descriptive tools for different CRM questions. | No model or causal claim is implied. |
| ANA-02 | Yes | PASS | Exact precedence for credit review, lifecycle, value tier and audience fallback is documented and exhaustive. | Segment coverage/precedence fixture passes; crosswalk has full customer coverage. |
| ANA-03 | Yes | PASS | Relative labels are “Recent/Lapsed/Frequent/Intermediate”; they do not claim “new” or “loyal” from a quantile alone. | Label semantics are tested against raw conditions. |
| ANA-04 | Yes | PASS | Crosswalk shows how lifecycle selects stage, RFM describes relative history, M supplies value context and credit review overrides outreach. | README/METHODS/memo agree; no disconnected integration claim remains. |
| ANA-05 | Yes | PASS | Rule sensitivity covers lifecycle, value and credit thresholds; tenure and duplicate alternatives are reported. | `outputs/rule_sensitivity.csv`, `duplicate_sensitivity.json`. |
| ANA-06 | Yes | PASS | Ties, cutoffs, 90/180-day boundaries and credit gates are tested; thresholds are called hypotheses, not optima. | All edge fixtures and sensitivity checks pass. |
| INF-01 | Yes | PASS | Critical claims have file/query/test destinations in `audit/CLAIM_EVIDENCE_LEDGER.md`. | Values match the frozen release outputs. |
| INF-02 | Yes | PASS | Memo/README distinguish descriptive history, proposed tests and missing causal evidence. | No uplift, profit or response-probability claim remains. |
| INF-03 | Yes | PASS | Tenure, seasonality/cohort, wholesale mix, credit linkage, selection and censored-window alternatives are disclosed. | `tenure_context.csv` and cohort outputs support the limitations. |
| INF-04 | Yes | PASS | This is a descriptive census; pooled rates, denominators, missing cells and rounded display are explicit without invented inferential precision. | Bounds and zero-denominator fixtures pass; N/A chart labels, all four mature horizons and the 0–90-day x-axis remain visible for empty eligible populations. |
| INF-05 | Yes | PASS | Material limits sit in the memo beside the decision: missing IDs, margin/cost/consent, source coverage, tenure and credit pairing. | README, METHODS and memo are reconciled. |
| DEC-01 | Yes | PASS | Each proposed audience/test in the memo is linked to lifecycle, value/credit or mature repeat/cohort evidence. | Conditional test list includes the objective and outcome. |
| DEC-02 | Yes | PASS | Missing margin, treatment cost, consent, current status and contactability are named before operational use. | No invented economic inputs. |
| DEC-03 | Yes | PASS | Outputs are review/test hypotheses; credit/value review gates outreach; no automatic discount, rollout or scale is recommended. | Memo language and priority labels are conditional. |
| DEC-04 | Yes | PASS | The memo says no messages were sent and no causal impact was measured. | Proposed tests are labelled proposals. |
| DEC-05 | Yes | PASS | Memo specifies assignment-time eligibility, holdout, 90-day follow-up, success/guardrail metrics and predeclared stopping/power inputs. | Next step is to collect missing inputs if the test cannot be run. |
| DEC-06 | Yes | PASS | Actions name audience, owner/CRM gate, KPI and contact/cost constraints at the level supported by the data. | Send-ready/contact-ready status is explicitly false. |
| RUN-01 | Yes | PASS | README gives pinned requirements, commands, data paths and notebook command; `audit/fresh_run.log` is a clean run record. | `requirements*.txt` and release manifest freeze the environment. |
| RUN-02 | Yes | PASS | Canonical CLI exits 0 and creates all promised outputs, figures and memo. | Fresh-run comparison matches the checked release. |
| RUN-03 | No | N/A | This release is a Python/CSV/PNG/HTML artifact; no native Excel, Power BI, Tableau or R usability claim is in scope. | Native verification would be required only after adding that deliverable/claim. |
| RUN-04 | Yes | PASS | Successful rerun regenerates tables, figures and memo; README says snapshots remain static until rerun. | Byte-identical clean rerun proves the shipped state is reproducible. |
| RUN-05 | Yes | PASS | Clean temporary run matches all 26 generated files byte-for-byte; SQL and fixture checks are not copies of the pipeline assertions. | `audit/fresh_run_comparison.json`. |
| RUN-06 | Yes | PASS | Missing/bad schema input exits nonzero, prints no PASS and preserves the destination marker without publishing outputs. | Negative CLI checks are in `audit/independent_validation.json`. |
| OUT-01 | Yes | PASS | Figures label counts, rates, GBP, horizons, cohort percentage and grey unobserved windows; visuals were inspected. | `audit/visual_review.json`; metrics match memo/output tables. |
| OUT-02 | No | N/A | The deliverable has static PNG/HTML outputs and makes no interactive filter/cross-highlight claim. | An interactive dashboard would add a new native scope and checks. |
| OUT-03 | Yes | PASS | README, methods, memo, tables, figures, notebook and preview are generated from the same canonical pipeline and match the fresh run. | No stale parallel notebook result remains. |
| OUT-04 | Yes | PASS | README has a Start here path; memo, methods and Vietnamese guide separate question, evidence, decision and limits. | Preview and static visual QA are supplied. |
| OUT-05 | Yes | PASS | Local-link checks cover README, memo, METHODS and learning guide; all referenced release files exist. | Validator includes 45 PASS checks. |
| OUT-06 | Yes | PASS | Final inventory contains source, code, tests, outputs, figures, memo and audit records without secrets, PII or obsolete success outputs. | Release manifest records the final inventory. |
| HR-01 | Yes | BLOCKED | The artifact includes `docs/LEARNING_GUIDE_VI.md`, but no file can prove the user can explain all six pillars aloud. | User practice/evidence is required; no artifact change can close this row. |
| HR-02 | Yes | BLOCKED | Tests demonstrate metric examples, but they do not establish the user's ability to explain a denominator and method in an interview. | User must work a small example verbally. |
| HR-03 | Yes | BLOCKED | `docs/CONTRIBUTION.md` accurately states AI assistance, but personal authorship/mastery is not independently verified. | User must describe their actual contribution and assistance honestly. |
| HR-04 | Yes | PASS | README, memo and contribution boundaries avoid measured uplift, profit, production deployment and false independent authorship claims. | Claim ledger and contribution note are frozen. |
| HR-05 | Yes | PASS | This report states verdicts, scope, evidence, N/A reasons and blocked conditions. | Artifact/interview verdicts remain separate. |
| CUS-01 | Yes | PASS | F is distinct positive customer/invoice count; purchase days and same-day invoices are separate; visits are not inferred. | SQL invoice check and methods caveat pass. |
| CUS-02 | Yes | PASS | R/F/M use raw-value quantile cutoffs with equal-value tie preservation and strict boundary rules. | Permutation/tie fixture and cutoffs output pass. |
| CUS-03 | Yes | PASS | Lifecycle and RFM have separate roles; M contributes to value/action context without being forced into every descriptive label. | Crosswalk demonstrates the mapping. |
| CUS-04 | Yes | PASS | Exact 90-day eligibility, mature cohort windows and repeater-only median are defined; first observed purchase is not called acquisition. | SQL, fixtures and cohort masking checks pass. |
| CUS-05 | Yes | PASS | 90/180 lifecycle, M-tier, credit override and precedence are explicit; alternate rules show label sensitivity. | Boundary fixtures and `rule_sensitivity.csv` pass. |
| CUS-06 | Yes | PASS | Positive purchases, credits and net recorded history are distinguished from profit/CLV; win-back and second-order actions are proposed tests. | Memo and value reconciliation pass. |
| CUS-07 | Yes | PASS | Tenure bands and last-365-day context expose unequal observation opportunity; F/M are not called future loyalty/value. | `outputs/tenure_context.csv` and methods limits pass. |

## Earlier release 1.0.1 recheck

The original supplied ZIP passed CRC and all original manifest hashes, so the file transfer was intact. The original content nevertheless had one P1 delivery issue (duplicate sensitivity omitted after notebook refresh), and P2 reporting issues (assessment coverage overstated and a net-value chart legend ambiguous). These were repaired in the extracted ZIP copy. The original RFM/customer/KPI results were independently rechecked. This paragraph describes the earlier 1.0.1 review, retained in audit/history; the current 1.0.2 review and archive checks are recorded below.

## Issues fixed during the remaster

The uploaded version had material issues that were repaired and retested: input-order-dependent RFM ties; unsupported “new/loyal” semantics; gross-only prioritisation despite credits; a 90-day denominator that used one extra snapshot day; future cohort cells shown as zeros; an unconnected repeat-purchase module; stale notebook logic; and broken/unsupported source/link documentation. The exact changes and rationale are in `audit/CHANGELOG.md`. The retained-duplicate assumption remains a disclosed sensitivity, not a hidden correction.

## Optional follow-up

The release does not need another feature to meet this scope. A later version could add native Excel/BI delivery or a real CRM experiment only with a new scope, data access and corresponding module checks. The immediate open item is interview practice for HR-01–HR-03.

## Release 1.0.2 — final review of the supplied ZIP

Input ZIP SHA-256: `d31963a0f1e3d9b4291a265206efd1ef4977b1735907d5d266f9e0f1a04d19bb`. ZIP CRC and all 58 original manifest entries passed. The new supplied ZIP is byte-equivalent in its project files to the previously supplied 1.0.1 project. This review therefore starts from that exact content, not an assumed newer implementation.

Resolved defects: out-of-range Customer IDs could wrap to negative integers during int64 conversion; IDs and quantities now have an explicit safe integer bound with counted exclusions. Undefined cohort rates had no explicit N/A labels and NaN-only plots could hide three horizons; all four categorical positions and the 0–90-day repeat axis now remain visible. Regression fixtures and visual review confirm the fixes. Headline customers, orders, values, scores, actions and retention outputs remain unchanged; version/config hashes and presentation changed intentionally.

Notebook execution now selects the runner's own interpreter for subprocess kernels and does not retry cell/dependency errors as sandbox permission problems. A subprocess attempt failed at startup in the managed network environment and is retained as `audit/notebook_subprocess_attempt.log`. The supported managed-runtime path uses a fresh in-process kernel; all 9 cells pass. A deliberately failing cell propagates CellExecutionError (audit/notebook_negative_check.json). No browser/frontend compatibility claim is added.

The original Criteria v2 text is unchanged. CHECKLIST.csv/json records all 107 IDs: 63 PASS, 0 FAIL, 3 BLOCKED, 41 N/A (39 other specialist criteria plus 2 unsupported native/interactive criteria). All 63 applicable artifact criteria pass. The 3 BLOCKED criteria concern the applicant's understanding/contribution; they cannot be closed by editing files. The release is frozen only within its declared artifact scope and tested environment, not certified error-free in every future environment.

Earlier audit records are labelled historical under audit/history; current evidence and final manifest bind this release. Changes invalidate relevant evidence and require a new audit. No future claim is inferred from the old audit or from successful packaging.
