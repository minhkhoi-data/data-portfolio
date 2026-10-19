# GA4 Power BI — takeover audit, 2026-10-15

**ANALYTICAL / STATIC CHECKS PASSED. NATIVE AND REDISTRIBUTION GATES REMAIN BLOCKED.** This is not ARTIFACT VERIFIED or INTERVIEW READY.

| Verdict | Count |
|---|---:|
| PASS | 53 |
| FAIL | 0 |
| BLOCKED | 10 |
| N/A | 44 |
| Total IDs | 107 |

N=63 applicable criteria; pass rate and assessment coverage are both 84.13%. 53/60 artifact criteria pass; the other three applicable criteria concern personal evidence. Scores do not offset missing gates. Mandatory criterion wording is preserved verbatim from CRITERIA_V2.md. The analytical module is EXP-01/02; no observed experiment exists, so EXP-03–08 remain N/A.

## Executed checks on this release

- Fresh complete rebuild exited 0: all 4,295,584 bundled source events; 360,129 sessions; 270,154 pseudonymous users; 5,692 purchase events; USD 362,165 recorded purchase-event revenue; 4,848 purchasing sessions; strict stage counts 77,020 / 14,380 / 5,187 / 2,778. Overall totals and funnel match the supplied snapshot.
- 159/159 analytical/static checks passed. Six regression tests cover report aliases/bounds and masked channel rules. Five executed pipeline fixtures cover wrong hash, missing input, bad schema, known-answer serialization and honest import dates. Counts overlap in scope and are not interpreted as unique criteria.
- A separate DuckDB implementation imported no production analytical functions, scanned every source event and compared all session/purchase fields against the final CSVs: 45 checks PASS; complete 360,129-session and 5,692-purchase populations. DuckDB was capped at 1 GB and one thread, using temporary disk tables. An initial 512 MB attempt stopped cleanly at its own cap; it is historical failure evidence, not a successful check. See evidence/takeover_sql_validation.json and takeover_sql.log.
- 55 current JSON files passed official Microsoft schemas (9 schema documents). TMDL and M grammar parser evidence is reused only for SHA-256-identical tested inputs, explicitly historical; it does not execute native DAX/M.
- Fresh PowerShell 7.5.3 Linux ConfigureOnly tests passed for Unicode/spaces/special characters, exact path decoding, idempotence, relocation, missing/altered CSVs and missing PBIP. These tests do not certify Windows launch or Windows PowerShell 5.1. See evidence/opener_tests.json.
- Viewed the actual current Python preview; labels, values and axes are readable. It is not a Power BI screenshot. See evidence/takeover_visual_review.json.
- Native DAX matrix regenerated for 19 contexts x 35 measures (665 comparisons), tied to current CSV hashes. It remains PREPARED_NOT_NATIVE_EXECUTED. Comparator fixtures accept an identical fixture and reject zero substituted for BLANK; those fixtures are not native execution evidence.
- Bounded full rebuild completed in 67.9 seconds; maximum sampled total sandbox cgroup memory was 4.913 GiB, below the 7 GiB stop threshold. No memory/time stop occurred in the final build. This is a sampled sandbox total, not a universal hardware benchmark.

## Material findings and repairs

| Issue | Evidence and impact | Resolution and retest |
|---|---|---|
| P1: deleted acquisition data labelled as observed channels | 22,233 sessions in Other observed and 3 in Referral had source=(data deleted). The old unknown count understated acquisition uncertainty. | Unknown / masked is now 119,526 sessions, up 22,236 from 97,290. Existing 396 <Other> sessions with deleted medium were already unknown. All raw strings preserved. Five channels remain; raw-SQL comparison and regression fixtures passed. |
| P1: incomplete session CSV observed during an intermediate rebuild | A generated CSV contained 359,972 rows, 157 fewer than the in-memory headline; independent checks stopped that build. The exact underlying I/O cause was not established. | Publish via flushed/synced temporary CSV; verify header, every row width and total row count before replacement. Final physical file contains all 360,129 rows, matches every raw-SQL field and passes the final complete runner. No claim is made that the old submitted CSV had this defect. |
| P2: importer hard-coded archive download date | Any future import would claim 2026-10-08 regardless of acquisition time. | Future imports keep acquisition date unknown and record actual projection creation UTC time. Executed fixture passed. Existing supplied provenance is retained as historical, not rewritten as a new download. |
| P2: native comparison matrix could remain stale after a rebuild | The consolidated runner did not regenerate it. | Added build_native_contract.py to run_all.py; current 19-context matrix matches all eight CSV hashes. Added a CSV comparator for later native export checks. |
| P2: audit handoff mixed cross-project references and expanded HR demands | Current report pointed outside the standalone folder; HR-02/03 closure descriptions added live coding / rebuilding requirements absent from criteria. | Standalone report and exact criteria included; HR closure text restored without changing mandatory criterion wording. |

Current channel results: Unknown / masked 119,526 sessions / USD 131,163; Referral 28,849 / USD 46,521. No Other observed group is present in this snapshot after correction. It remains a legitimate fallback for genuinely observed unclassified combinations, as the fixture confirms. Channel comparisons describe first-user acquisition, not session attribution or causal channel efficiency.

## Remaining gates

| IDs | What remains unavailable |
|---|---|
| MET-06, RUN-03, RUN-04, OUT-01, OUT-02, EXP-02 | Open/Refresh in Windows Power BI Desktop; Windows M; actual DAX outputs and BLANK semantics; five-page rendering and interactions. The connected Desktop device was offline. A single Overview screenshot is the agreed limited first check and does not certify every native gate. |
| SRC-05 | Dataset-specific rights to republish raw/derived data have not been independently established. A mirror code license or documentation-page license is not treated as dataset permission. No public publication was performed. |
| HR-01 | Applicant explains six pillars in their own words. |
| HR-02 | Applicant explains one small metric example, denominator and method choice; live coding is not required. |
| HR-03 | Applicant accurately explains actual personal and AI-assisted contributions; rebuilding from scratch is not required. |

## Source and interpretation boundary

The bundled 25-column projection is unchanged and its hash matches the supplied provenance. Public official Google documentation confirms a three-month obfuscated Google Merchandise Store sample, with placeholders and limited internal consistency. The mirrored archive and original 88-column CSV hashes are retained as supplied historical provenance; this audit did not redownload/recompare that entire 438 MB / 2.17 GB original. Included BigQuery control counts/revenue reconcile; no fresh authenticated BigQuery query was executed.

Official documentation: https://developers.google.com/analytics/bigquery/web-ecommerce-demo-dataset . Mirror: https://www.kaggle.com/datasets/hashiromer/ga4-merchandise-store-flattened-bigquery . This is a public obfuscated analytics sample, not an unaltered production ledger and not AI-generated outcomes. Source provenance is distinct from a guarantee of real-world accounting accuracy.

Revenue is recorded purchase-event USD, not audited orders, net sales, profit or CLV. First-user channel is not current-session campaign attribution. Missing/repeated transaction IDs prevent AOV/order-count claims. Product-level data and random experiment assignments are absent; no SKU ranking, measured uplift or rollout winner is claimed. Proposed tests remain designs.

## Native handoff

Extract a fresh folder, run MO_PROJECT.cmd, then Refresh in Power BI Desktop. First provide Executive Overview as agreed. For later full semantic closure, run audit/native_contract/validate_all_contexts.dax in DAX query view and export unformatted numeric CSV; run scripts/compare_native_dax.py --actual path/to/export.csv. All contexts/measures must match; blanks remain distinct from zero. Rendering/interactions require separate observation. Native gates remain blocked until actual evidence is supplied.

Stop this audit at the checked version. Reopen for material errors, changed source/rules/scope or new native evidence; optional charts/models do not justify repeating all checks.


## UI fix v2

Five baseline native page screenshots were reviewed. Footer geometry, new-user CVR label and count-card units have been updated; current layout/filters still need native confirmation. Data and semantic model are unchanged. See audit/UI_FIX_V2.md (or UI_FIX_V2.md from this audit folder).
