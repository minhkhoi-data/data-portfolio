# Microsoft Excel handoff

The new workbook is separate from the prior synthetic CRM file. Test this exact delivered file.

1. Open `Olist_CRM_Acquisition_Seller_Value.xlsx` in Microsoft Excel. If Repair is requested, retain the original and send its repair log; do not accept a repaired file as the release.
2. Set Calculation to Automatic, press Ctrl+Alt+F9 and wait. Dashboard should show 8,000 / 842 / 10.5% / 14 / 380 / 664,858 / 287, with the default controls.
3. Check all four Dashboard charts, Channel_Performance, both SR and SDR tables in Rep_Performance, Monthly_Trend and Seller_Value. Unlinked seller monetary cells should be blank. Do not Restore an inconsistent table formula without reviewing any warning.
4. Change Lookups B3 from 30 to 14: Slow won cycles should change from 287 to 414, and Action_List evidence should update. Source counts, recorded won share and linked item value should stay unchanged. Restore 30.
5. Filter Leads by Date_issue: exactly one chronology exception; its observed-win flag remains 1 while its valid cycle is blank. Filter Seller_Value to no linked sample items: 462 sellers; monetary results stay blank.
6. Save a copy, close/reopen, recalculate and verify the baseline and chart/table behavior persist. Record Excel version and date when these steps are completed.

Calc/structural evidence is supplied separately in audit. It does not prove Microsoft Desktop behavior or personal mastery. Avoid public data redistribution until the recorded licence and intended use are reviewed.

