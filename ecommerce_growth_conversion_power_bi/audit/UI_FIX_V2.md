# UI fix v2 — 2026-10-15

The user supplied screenshots showing all five baseline report pages render. Observed issues: all footers clipped, a misleading First-observed CVR label, and coarse auto-scaled count cards.

Changed presentation only: page height 720 → 760, existing footer height 25 → 55 at the same position; renamed the GA4 new-user indicator card to New-user session CVR; set count card labelDisplayUnits to None (1) and labelPrecision to 0 using the official Microsoft theme schema. The canonical build_model.py report builder produces the same changes on rerun.

All data files and semantic model bytes are unchanged. Five baseline page screenshots are partial native-render evidence, not a full DAX/filter/Refresh certification. This revised layout still needs Desktop confirmation. Existing native, redistribution and personal gates are not automatically closed.

Targeted retest: current report schemas, static/analytical verifier, footer geometry, label absence and data/model byte equality. No 4.3-million-event rebuild is needed for these presentation changes.

First user check: open this revision in a fresh folder, Refresh, select Direct in Executive Overview. Expected Revenue USD 79,650 (79.65K if currency card remains abbreviated), Sessions 83,459, Purchase Events 1,251 and Session Conversion Rate 1.29%. Return to all channels after the screenshot.
