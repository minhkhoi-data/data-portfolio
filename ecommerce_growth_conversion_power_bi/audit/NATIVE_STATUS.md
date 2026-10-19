# Native Power BI status

| Check | Status | Explanation |
| --- | --- | --- |
| Prior delivered revision: PBIP open | FAILED | User screenshot reports UnknownKeyword isKey in DimDate, line 13; see evidence/native_error_dimdate.png |
| First correction: PBIP open | FAILED | Second user screenshot reports InvalidLineType ReferenceObject at ref table FactSessions, model line 15; see evidence/native_error_model_refs.png |
| Previous standalone CSV/GZip build: model creation | FAILED | User log reports PFE_M_ENGINE_INTERNAL / closed Stream during CreateDatabase/SaveChanges on Desktop August 2026 |
| JSON/Deflate mitigation: model creation | FAILED | User log on 13 October 2026 reports the same PFE_M_ENGINE_INTERNAL / closed Stream |
| User one-row Enter Data test | PASS | User states Load succeeded and supplied a chart showing Sum of Test = 1; this is a basic M scenario, not this project |
| Corrected model: official TMDL parser | PASS when evidence/tmdl_parser.json matches current model | Microsoft TmdlSerializer reads 8 tables, 8 relationships and 35 measures; rejects both malformed controls |
| Rebuilt loader: Microsoft M grammar parser | PASS when evidence/m_syntax_parser.json matches current model | Eight M imports and the DataFolder expression parse; function execution and Windows engine behavior are not tested |
| PBIP open and model load | NOT VERIFIED | Desktop is unavailable in the build environment |
| DAX compilation / evaluation | NOT VERIFIED | Static references and independent Python calculations are checked; no DAX engine run |
| File-backed CSV rebuild in Windows M Engine | NOT VERIFIED | CSV bytes/schema/types and short M expressions checked; syntax validation does not execute M |
| Page rendering / interactions | NOT VERIFIED | Bounds and bindings checked statically; preview is Python |
| User Overview screenshot | PENDING | Only Overview requested, as agreed with user |

Two previous revisions failed TMDL parsing; their scope/indentation defects are corrected. Both subsequent embedded CSV/GZip and JSON/Deflate versions failed Windows model creation with an M Engine closed-Stream error. The logs identify the stage/code, not a particular query or ultimate internal cause. The user's one-row Enter Data test then succeeded. This rebuild removes all large embedded M literals and both calculated partitions, reads bundled CSV files, and configures one path before opening. It changes loading and support-table initialization, while preserving source data and the 35 measure definitions. Windows M execution and Desktop opening are still NOT VERIFIED. Do not call this a confirmed engine fix. The user does not need a long checklist; an Overview screenshot is the agreed limited native confirmation.

## Current takeover evidence — 2026-10-15

All 55 report JSON files passed official schemas. Fresh PowerShell 7.5.3 Linux ConfigureOnly tests passed on current runtime hashes. TMDL/M parser evidence is historical and SHA-256-identical-input reused. Independent source-to-fact SQL checks and current Python visual inspection passed. The connected Windows device was offline; Windows open/Refresh, DAX and report interactions remain NOT_VERIFIED. See AUDIT_REPORT.md for the exact current checklist.


## UI fix v2

Five baseline native page screenshots were reviewed. Footer geometry, new-user CVR label and count-card units have been updated; current layout/filters still need native confirmation. Data and semantic model are unchanged. See audit/UI_FIX_V2.md (or UI_FIX_V2.md from this audit folder).
