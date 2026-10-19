# Power BI — final remaster audit

Release: flagship-remaster-2026-10-13. Current verdicts: **{'PASS': 52, 'BLOCKED': 11, 'N/A': 44}**. Applicable N=63; pass=82.54%; coverage=82.54%.

**No artifact freeze / perfection claim while non-personal gates are BLOCKED.** HR-01/02/03 are personal evidence gates, not deliverable defects. Every criterion’s mandatory wording is retained in FINAL_CHECKLIST.csv.

## Remaining gates

| ID | Evidence gap | Required closure |
|---|---|---|
| AUD-03 | TMDL/M/opener historical tests match current tested-input hashes. Current report JSON schema was not freshly validated; Desktop/M/DAX execution remains absent. | Run official report schema validation and native checks on final bytes; keep partial evidence labelled. |
| SRC-05 | Mirror code licence is not accepted as dataset redistribution permission; private handoff does not establish public-publishing rights. | Verify dataset-specific redistribution rights or arrange a permitted source acquisition before public data publication. |
| MET-06 | All35 DAX definitions inspected and matched; a20-context ×35-measure query/independent expectation matrix is prepared, not executed in DAX. | Run audit/native_contract/validate_all_contexts.dax after refresh; compare every result with expected.csv, including BLANK vs0 and date/filter contexts. |
| RUN-03 | Power BI Desktop/Windows M/DAX/all-page rendering and interactions were unavailable. Python preview/static parsing do not certify them. | Open final PBIP through MO_PROJECT.cmd, refresh, check native semantic matrix/pages/filters and attach version-bound evidence. |
| RUN-04 | Power BI Desktop/Windows M/DAX/all-page rendering and interactions were unavailable. Python preview/static parsing do not certify them. | Open final PBIP through MO_PROJECT.cmd, refresh, check native semantic matrix/pages/filters and attach version-bound evidence. |
| OUT-01 | Power BI Desktop/Windows M/DAX/all-page rendering and interactions were unavailable. Python preview/static parsing do not certify them. | Open final PBIP through MO_PROJECT.cmd, refresh, check native semantic matrix/pages/filters and attach version-bound evidence. |
| OUT-02 | All35 DAX definitions inspected and matched; a20-context ×35-measure query/independent expectation matrix is prepared, not executed in DAX. | Run audit/native_contract/validate_all_contexts.dax after refresh; compare every result with expected.csv, including BLANK vs0 and date/filter contexts. |
| HR-01 | Personal explanation/oral interview evidence is not supplied. | The author must independently explain metric logic, assumptions and decisions. |
| HR-02 | Independent live coding/formula/debugging evidence is not supplied. | Complete a personally performed practical exercise; AI-generated fixes do not close this criterion. |
| HR-03 | Independent ownership and transfer-to-new-case evidence is not supplied. | Rebuild/explain an analogous case without delegating the core reasoning. |
| EXP-02 | All35 DAX definitions inspected and matched; a20-context ×35-measure query/independent expectation matrix is prepared, not executed in DAX. | Run audit/native_contract/validate_all_contexts.dax after refresh; compare every result with expected.csv, including BLANK vs0 and date/filter contexts. |

## Verified scope

RFM: original analytical core preserved; new consolidated runner and fresh analytical checks. Power BI: canonical rebuild and157 static/analytical checks; parser evidence reused only for exact inputs. Excel: all raw/derived cells and summaries checked in a separately running Calc engine, with95 independent checks and deliberate invalid-input/scenario fixtures. These are project-specific scopes, not interchangeable engine claims.

See ../../START_HERE_MASTER.md for cross-project context and FINAL_CHECKLIST.csv for all107 IDs.
