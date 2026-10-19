# Remaster acceptance scope — locked before implementation

Version: Remaster 1.0.2; input: the uploaded standalone customer project. Acceptance standard: Portfolio Audit Criteria v2.0 (local copy: CRITERIA_V2.md).

Purpose: describe observed customer purchasing, return/credit-adjusted value, repeat behaviour and calendar-cohort activity; create defensible historical CRM test audiences. Audience: CRM/marketing analyst and portfolio reviewer. No measured campaign impact, individual response probability, profit, CLV or production deployment is promised.

Required deliverables: runnable Python pipeline; executable Jupyter notebook using the same pipeline; auditable transaction-to-order-to-customer lineage; repeat/cohort analysis; explicit RFM/lifecycle/action rules; sensitivity checks; figures; generated decision memo; beginner explanation; complete audit record and reproducible validation.

Applicable: AUD-01–05, all 56 common criteria, CUS-01–07 (68 inventoried; RUN-03 and OUT-02 are N/A, leaving 66 applicable criteria). HR-01/02/03 require evidence from the applicant and cannot be passed by automated review. Other specialist modules do not apply to this descriptive Python project. Native Excel/Power BI/Tableau operation is not a promised deliverable. Jupyter kernel execution, notebook validity and saved rendered outputs will be checked; GUI/browser behaviour is not certified.

Changes required without abandoning the original question: remove input-order RFM tie splitting; correct customer labels; account for observed credits when prioritising historical value; correct repeat-window eligibility and censored cohort display; connect analysis to conditional test proposals; regenerate notebook and outputs together; repair attribution and standalone paths. Recommendations remain proposals because contact permission, margin, treatment cost and live-system access are absent.

Critical claims and checks: row/value conservation (sequential ledger and independent recomputation); one customer/invoice per order (key/cardinality assertions); complete 90-day eligibility (exact timestamp boundaries); no fake zero for future cohorts (mask checks); deterministic scores (tie/permutation tests); action coverage and monetary/credit gates (exhaustive rule tests); all reported numbers trace to final outputs; CLI and notebook fresh runs; malformed inputs fail without falsely publishing successful outputs.

Tolerance: monetary reconciliation within GBP 0.01 absolute; rates within 1e-10 before CSV serialization and 1e-7 after serialization. Counts and labels match exactly. These are numerical tolerances, not uncertainty intervals. No inferential causal claim is in scope.

Freeze: every applicable artifact criterion outside personal HR checks must PASS. Keep applicant readiness separate. Any unavailable required evidence remains BLOCKED. Scope/logic changes are recorded in CHANGELOG.md; a correct narrower claim does not prove an abandoned stronger claim.

## 1.0.2 verification extension (2026-10-07)

Original purpose, expected outputs and criterion meanings are unchanged. Revision repairs invalid-integer and undefined-rate rendering defects and adds independent customer/cohort checks; it does not add native/interactivity/production claims. All 107 IDs are inventoried; 39 unrelated specialist IDs and two unsupported native/interactive conditions are N/A, with reasons. Applicable artifact gates remain separate from applicant HR evidence. Original 1.0.1 scope is retained under audit/history. Current verdicts are set only after fresh execution and package checks.

## Standalone takeover — 2026-10-15

Same analytical question, bundled source and acceptance criteria. Restore standalone documentation, align HR closure requirements exactly with criteria v2, and execute the documented runner with current dependencies. Current evidence is recorded separately from history; no new GUI/Windows claim is introduced. Source workbook comparisons dated 2026-10-07 are retained historical provenance, not a new workbook comparison.
