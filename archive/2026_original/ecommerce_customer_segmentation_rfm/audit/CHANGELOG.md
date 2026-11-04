# Remaster 1.0 — substantive changes from the uploaded project

- Replaced rank(method='first') quintiles with tie-preserving raw cutoffs; tested permutation stability and all 125 score combinations.
- Renamed unproven “New Customers” and “Loyal Customers” labels to observable/relative descriptions; separated absolute lifecycle from relative RFM.
- Retained credits and introduced net recorded value for M, with credit-only reconciliation and a review override. Removed automatic preference based on gross revenue alone.
- Connected raw lifecycle, RFM components/Champion context and value tiers in one explicit CRM queue; M affects every lifecycle state.
- Corrected the 90-day window to exact elapsed timestamps, using the actual observation end instead of the added snapshot day. Rates changed; no old percentages are retained as current results.
- Added same-day versus different-day repeat, mature repeat curve/cohorts, tenure context and recorded 365-day context fields. These are sensitivity/context checks, not individual predictions.
- Masked incomplete/future cohort months rather than zero-filling headline retention; labelled month-n activity rather than continuous survival. Full 0–100% colour scale includes cohort baseline.
- Removed the unsupported recommendation to trigger a campaign before the repeaters' median day. Added conditional test proposals with missing consent/margin/cost and pre-assignment measurement requirements.
- Added sequential row/value reconciliation, typed input validation, schema/grain failure handling, prepared line/order outputs, rule and duplicate sensitivity, fixture tests and independent SQL checks.
- Replaced the stale parallel notebook implementation with an executable walkthrough of the canonical pipeline; regenerated charts, memo and standalone links.
- Verified source against official UCI workbook, added source/license/hash records, pinned the tested environment and disclosed AI assistance.
- Preserved the original business question. Stronger unsupported interpretations (profit, newly acquired customers, validated optimal strategy, measured impact) were corrected; they were not delivered or silently counted as verified.

## Release 1.0.1 — verification of the delivered ZIP

- The original ZIP passed CRC and all 56 manifest hashes, but it omitted `outputs/duplicate_sensitivity.json`: notebook refresh replaced outputs after the validator had generated it. This contradicted README links and the previous artifact verdict (RUN-04, OUT-03/05/06). The report is now a canonical pipeline output; the validator checks it instead of silently generating it. A double-refresh regression fixture verifies it survives notebook-style reruns.
- Corrected audit assessment coverage from 100% to 63/66 = 95.45%; personal HR evidence remains BLOCKED. Artifact-only assessment/pass coverage is 63/63 = 100%, excluding the three HR checks and two N/A criteria.
- Clarified the dashboard's yellow series as net after recorded credits; it was previously ambiguously labelled “Less recorded credits”.
- Added exhaustive expected RFM label counts over all 125 score profiles.
- Final validation runs in a folder extracted from the supplied release ZIP, with link checks after notebook execution.

## Release 1.0.2 — 2026-10-07

- Verified exact supplied ZIP: CRC and 58 manifest hashes pass. The new attachment contains the same 1.0.1 project files, so no change is assumed from its filename.
- Fixed out-of-range Customer ID conversion: 1e20 formerly became -9223372036854775808. IDs/absolute integer quantities beyond 2^53−1 are now excluded and counted before casting; valid rows survive. Existing bundled results do not change.
- Fixed undefined-rate rendering: show N/A for zero eligible customers, retain all four mature cohort horizons, and keep the repeat x-axis at 0–90 days rather than an auto-scaled empty range. Visually reviewed empty-population and normal charts; added a regression fixture.
- Hardened notebook environment selection and exception handling. Subprocess mode uses the runner's interpreter; cell/dependency errors propagate. Managed runtime selects the supported fresh in-process path and records it; an observed failed subprocess startup is retained, not labelled PASS.
- Added a production-independent SQL/raw-value verifier covering every customer field, order keys/times/values, scores, labels, grouping and cohort cell. Re-downloaded the official source and verified every row/field against the bundled raw CSV.
- Regenerated all outputs/notebook/HTML and tested 12 fixtures, 45 existing independent checks, 68 extended independent checks, a deliberate notebook-error case, all 26 fresh generated files and the final package. Earlier audit/scope/manifest snapshots are labelled historical; current 107-ID inventory is explicit.
- Criteria unchanged; 63 applicable artifact criteria PASS. HR-01/02/03 remain BLOCKED. No deployment, measured impact, sole authorship, frontend or universal error-free claim is added.

## Standalone takeover — 2026-10-15

- Closed the missing fresh-kernel gate through actual default runner execution. Retained a failed TCP subprocess attempt and recorded the supported in-process success.
- Independently downloaded and compared the official source again across every row/field; added an optional reproducible source-verification script and requirements.
- Corrected standalone parent-file references, evidence pointers, scope denominator and HR closure text to match the existing criteria; did not change criterion conditions or analytical rules.
- Moved prior root execution evidence to history, refreshed notebook/HTML, and verified every generated analytical output remains byte-identical to the upload.
- Artifact 63/63 PASS; interview gates HR-01/02/03 remain BLOCKED.
