# Native handoff — current release

Open the project on Windows with Power BI Desktop using `MO_PROJECT.cmd`, refresh, and inspect Overview. The launcher configures the single local DataFolder parameter and checks the eight runtime CSV hashes before opening. The agreed Overview screenshot is a useful limited opening check; it does not certify all DAX/filter interactions.

For full semantic validation, `audit/native_contract/validate_all_contexts.dax` is one query to paste into Desktop's DAX query view after refresh. Compare the exported results with `expected.csv`: every context × measure, absolute numeric tolerance 0.000001, blank kept distinct from zero, exact text. `contract.json` binds expectations to the actual data hashes. The query is prepared, not natively executed in this environment.

The matrix covers all data, each full month, partial/multiple months, each channel/device, country, crossed filters, empty country and selected funnel stage. It checks event-date revenue separately from session-attributed revenue. First-month / partial-month / multi-month MoM should be blank.

Historical parser tests are reused only for byte-identical inputs, labelled explicitly in `build_status.json`; all 55 current report JSON files passed official schema validation. Windows M execution, DAX compilation/evaluation, all-page rendering and interactions remain NOT_VERIFIED. Do not promote Python preview images to Desktop evidence.

This is a private handoff of the supplied public-sample projection. Dataset redistribution rights have not been independently established; the mirror's code licence is not treated as a data licence. No public upload was performed.

## Automated comparison of a later Desktop export

```bash
python scripts/compare_native_dax.py --actual /path/to/native_export.csv
```

Use unformatted numeric CSV, with Context/measure headers (bracketed DAX headers are also accepted). The tool checks exact contexts/columns, numeric absolute tolerance 1e-6 and exact BLANK versus zero. A comparator PASS alone does not establish export provenance or visual interaction correctness. Current matrix: 19 contexts and 35 measures.
