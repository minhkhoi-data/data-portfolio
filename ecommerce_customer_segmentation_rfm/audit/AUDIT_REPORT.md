# RFM — standalone takeover audit, 2026-10-15

**ARTIFACT VERIFIED / FREEZE WITHIN DECLARED SCOPE.** All 63 applicable artifact criteria PASS. **INTERVIEW READY: BLOCKED** at HR-01, HR-02 and HR-03, requiring evidence from the applicant.

| Full criteria inventory | Count |
|---|---:|
| PASS | 63 |
| FAIL | 0 |
| BLOCKED — personal evidence only | 3 |
| N/A | 41 |
| Total | 107 |

N = 66 applicable criteria including personal gates; pass rate and assessment coverage are each 95.45%. Artifact-only coverage and pass rate are 63/63. These are checklist counts, not a probability of being defect-free or getting hired. RUN-03 and OUT-02 are N/A because no native BI/Excel or interactive GUI deliverable is claimed; the other 39 unrelated specialist criteria remain N/A. Criterion conditions and mandatory evidence are preserved verbatim from CRITERIA_V2.md.

## What was verified now

- Inspected actual source schema, analytical code, methods, memo, all 107 criterion records and historical audit boundaries.
- Downloaded the official UCI workbook again and compared all 1,067,371 bundled rows, in original order, across all 8 fields. Zero mismatches after documented blank/text/date normalization and numeric absolute tolerance of 1e-10. Four numeric Description cells are text-equivalent. See `takeover_source_verification.json` and `analysis/verify_official_source.py`.
- Ran the documented `python analysis/run_all.py` successfully: pipeline; 12 known-answer/boundary tests; 45 SQL/counterexample/link checks; 68 extended independent checks covering all 5,878 customers, orders, labels, monetary values and cohort cells; 9 notebook code cells through a new in-process Jupyter kernel. Logs and exact execution status are in `remaster_execution.json`, `takeover_runner.log`, `remaster_*.log` and `notebook_execution.json`. Counts overlap in scope and are not added into a claim of unique criteria.
- Intentionally raised a notebook cell error in a separate fresh kernel; it propagated as CellExecutionError without a false success or hidden fallback. See `notebook_negative_check.json`.
- After the final notebook refresh, all 26 generated tables, figures and memo match the uploaded outputs byte-for-byte. The raw data, analytical core and configuration remain unchanged. See `takeover_output_comparison.json` and `release_manifest.json`.
- Viewed all three final PNGs directly. Axes, labels, units and cohort missingness display are readable. See `visual_review.json`.
- Validated notebook schema, sequential execution counts 1–9, absence of cell errors, current Markdown links and exact checklist wording. HTML embeds current notebook output; no browser GUI certification is claimed.

The main figures reconcile to 5,878 identified purchase customers; 36,969 positive purchase invoices; £17,374,804.268 gross purchase value; £1,023,763.31 recorded credits; £16,351,040.958 net recorded value; and 2,486/5,281 = 47.1% mature 90-day second-order rate. Displayed money is rounded; recorded net value is not profit or CLV.

## Issues resolved in this takeover

| Issue | Impact | Resolution |
|---|---|---|
| RUN-02 previously lacked a fresh notebook run | Required execution evidence was missing | Current dependencies installed; full documented runner and all nine cells executed successfully in a fresh kernel. |
| Standalone guide/current audit referenced missing master files outside the ZIP | A reader could not follow the standalone handoff | Replaced with paths inside this project; historical reports retained under history. |
| HR-02 and HR-03 closure text imposed live coding / from-scratch rebuilding not required by the actual criteria | Applicant could be judged against an expanded requirement | Restored small-example explanation and truthful contribution requirements; personal gates remain BLOCKED. Mandatory criteria text unchanged. |
| Old scope count said 68 without distinguishing 2 N/A conditions | Could confuse denominator | Documented 68 inventoried common/customer/governance IDs, 66 applicable, 63 artifact gates. |
| Evidence ledger cited cohort KPI output for the 90-day outcome and mentioned an older fixture count | Wrong evidence pointer / stale documentation | Pointed to repeat_90 outputs and current logs; corrected to 12 fixtures. |
| Prior execution reports and logs sat beside current evidence | Historical runs could be mistaken for this run | Archived prior root execution reports/logs; current report and manifest identify authoritative evidence. |

No analytical metric or rule change was needed after the fresh checks. No unresolved P0/P1/P2 artifact violation was identified within this scope. Optional presentation additions do not reopen the audit.

## Remaining personal gates — exact criteria meaning

| ID | Evidence still needed |
|---|---|
| HR-01 | Explain the six pillars in the applicant's own words: purpose, data, preparation, analysis, findings and limitations/contribution. |
| HR-02 | Explain one small customer/order metric example, the denominator and why the selected method fits the question. Memorising every syntax or live coding is not required. |
| HR-03 | Truthfully explain personal work versus AI assistance; no unsupported claim of independent authorship, source creation or earlier verification. A from-scratch rebuild is not required. |

## Scope and limits

This is descriptive historical analysis of one UK retailer (2009–2011), using identified positive-purchase customers. Missing IDs, credit-only customers, unmatched credits, duplicates and observation tenure limit interpretation. Thresholds are analyst-defined hypotheses, not validated optima. Cohort activity is not survival; first observed purchase is not confirmed acquisition. No measured uplift, profit, future CLV, deployed campaign or current Vietnam market conclusion is established. All ContactReady flags remain false.

This host rejected the TCP subprocess kernel; the failed attempt is retained at `history/pre_takeover_20261015/takeover_subprocess_socket_failure.log`. The project already supports a fresh in-process kernel, which is the tested managed-runtime mode and completed successfully. This does not certify Jupyter browser/frontend, Windows/Anaconda or subprocess compatibility on every machine. The original locked scope required kernel execution and excluded frontend certification; no required artifact gate was dropped to hide this restriction.

Source data and all analytical outputs are unchanged; evidence is version-bound by the manifest. Reopen only for a material bug, changed data/rules/scope or invalidated evidence. Do not repeat the full audit solely to add optional charts or models.
