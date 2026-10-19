# Real-data Excel rebuild — executed checks

Baseline: **139/139 PASS** after separate LibreOffice Calc recalculation. These cover all lead source fields, all prepared/derived lead fields, all linked-item source/derived fields, all 842 seller aggregates, all channel/rep/month summaries, headline KPIs, error scan and reconciliations. **11/11 PASS** across four disposable control scenarios: valid slow threshold, invalid slow threshold, valid support threshold and invalid support threshold.

The analytical source was downloaded directly from Olist publisher endpoints. Five used CSVs retain their original bytes and SHA256 hashes. No synthetic filler outcomes, probabilities or monetary amounts were added.

Native structure: 12 worksheets, four editable worksheet-bound charts, full source rows, auto/full recalculation flags, and 52 synchronized uniform calculated-column definitions. Calculated caches and chart-reference caches are imported from separately evaluated results while authored native layout/styles/objects remain in place.

Visual QA: Calc-rendered viewports were inspected for every sheet. Top SR header formatting was restored after the second-table setup. Raw tabs are intentionally wide and require scrolling. Lower merged notes were reviewed separately from overview print viewports. No native Microsoft Excel execution is asserted.

During construction, whole-workbook authoring exceeded the available memory. The completed release instead uses 33 bounded Artifact Tool data fragments plus the summary skeleton. All fragments are assembled with style/shared-string remapping and source-bound formulas; no rows are dropped. Stale skeleton calculation caches were removed before independent recalculation. Explicit duration formats prevent date-style inference on calendar-day differences. These construction issues were corrected and do not count as successful checks.

Remaining gates: open/recalculate/save/reopen this exact new workbook in Microsoft Excel, inspect its charts/tables/control response, then assess personal explanation/mastery separately. The prior synthetic workbook's successful opening does not close this new file's gate.
