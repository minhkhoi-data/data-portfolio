# RFM — final remaster audit

Release: flagship-remaster-2026-10-13. Current verdicts: **{'PASS': 62, 'BLOCKED': 4, 'N/A': 41}**. Applicable N=66; pass=93.94%; coverage=93.94%.

**No artifact freeze / perfection claim while non-personal gates are BLOCKED.** HR-01/02/03 are personal evidence gates, not deliverable defects. Every criterion’s mandatory wording is retained in FINAL_CHECKLIST.csv.

## Remaining gates

| ID | Evidence gap | Required closure |
|---|---|---|
| RUN-02 | Fresh CLI, 12 fixtures, pipeline validator and 68 extended SQL/boundary checks passed; fresh notebook kernel was not executed because declared notebook dependencies are unavailable. Historical notebook/code/data remain unchanged. | Install requirements-notebook.txt and run analysis/run_all.py; full success requires a new actual kernel execution. Exit2 is explicitly BLOCKED, not PASS. |
| HR-01 | Personal explanation/oral interview evidence is not supplied. | The author must independently explain metric logic, assumptions and decisions. |
| HR-02 | Independent live coding/formula/debugging evidence is not supplied. | Complete a personally performed practical exercise; AI-generated fixes do not close this criterion. |
| HR-03 | Independent ownership and transfer-to-new-case evidence is not supplied. | Rebuild/explain an analogous case without delegating the core reasoning. |

## Verified scope

RFM: original analytical core preserved; new consolidated runner and fresh analytical checks. Power BI: canonical rebuild and157 static/analytical checks; parser evidence reused only for exact inputs. Excel: all raw/derived cells and summaries checked in a separately running Calc engine, with95 independent checks and deliberate invalid-input/scenario fixtures. These are project-specific scopes, not interchangeable engine claims.

See ../../START_HERE_MASTER.md for cross-project context and FINAL_CHECKLIST.csv for all107 IDs.
