# Bàn giao tiếp quản Excel Olist - 14/10/2026

## Kết luận đúng phạm vi

Đã sửa các lỗi layout có bằng chứng và hoàn tất static/analytical/Calc full-recalculation checks. **Microsoft Excel Desktop và INTERVIEW READY vẫn BLOCKED. Chưa ARTIFACT VERIFIED/FREEZE toàn project.** Không đổi thiếu access thành N/A.

Workbook cuối: `Olist_CRM_Acquisition_Seller_Value.xlsx`, SHA256 `4f718187e1935bc32501622f29b28f1f69aa545592bbb2c95c46805806f4345b`. Bản trước: `ed98f65649dead67154450a32e17c262fa6fc46e45badf0bec88c16b44c82d17`. 5 CSV source giữ nguyên bytes; 12 sheet và 4 chart native được giữ. Gói trước tên VERIFIED không đủ chứng minh gate Excel.

## Scope và criteria

Áp dụng 66/107 tiêu chí context: AUD + common + XLS; 41 module khác N/A vì khác loại project. 59 PASS, 0 FAIL hiện hành, 7 BLOCKED, 41 N/A. Tỷ lệ đạt = 59/66 = 89,4%; coverage đã kết luận = (59+0)/66 = 89,4%. Đây là tiến độ audit, không điểm chất lượng. Riêng gate sản phẩm loại HR-01/02/03: 59 PASS + 4 BLOCKED trên 63 criterion, 93,7%; chưa freeze. File `AUDIT_CRITERIA.csv`/`.json` có từng ID và evidence.

4 gate sản phẩm còn BLOCKED: RUN-03, RUN-04, OUT-02, XLS-05. HR-01/02/03 cần evidence từ người học. Không project/skill SQL hoặc các flagship khác được đánh giá trong phiên này. Full XLSX authoring reconstruction là workflow optional, đã sửa hướng dẫn/code nhưng chưa chạy trọn trong takeover; mandatory analytical reproduction đã fresh-run.

## Đã thực hiện

| Check | Evidence và kết quả |
|---|---|
| Archive/source integrity | ZIP CRC pass; 34/34 original release file hashes match trước sửa; 5 source CSV SHA256 vẫn match |
| Fresh analytical run | Outputs ban đầu rỗng; Python 3.12.14, pandas 2.2.3; exit 0, RUN_STATUS PASS; summary/source hashes/channel/month/SR/SDR files khớp byte bản giao |
| Final workbook baseline | LibreOfficeDev 26.8.0.0.alpha0, separate file evaluation; 139/139 PASS; all lead/item inputs/derived fields, 842 seller aggregates, summaries, headlines, error scan/reconciliations |
| Full-recalc controls | 4 disposable copies authored with native typed controls; clear formula caches before independent Calc import; 11/11 PASS; 30->14 days gives 287->414; Action_List evidence updates; invalid controls expose INVALID/#N/A |
| Preservation | LAYOUT_REPAIR.json: only native anchors and column/header dimensions changed; all source cells/formulas/styles/chart definitions/series/table metadata retained |
| Visual | Calc PDF viewports of all 12 sheets observed; final Dashboard/Seller/Leads/Sales_Items retest; source IDs readable; all 11 origin bars and 10 SR bars visible |
| Negative run | Missing source file -> exit 1, RUN_STATUS FAIL; no fabricated successful fresh summary |

150 individual automated checks are 139 baseline + 11 full-recalc scenario checks. They are **not** 150 audit criteria and do not prove native Excel UI interactions. CSV/module criteria are assessed separately.

## Issues và retest

1. **P1: Dashboard charts overlap.** Original drawing: left chart spans column markers 0..8; right chart starts at 7. Final origin category and tenth SR bar were hidden. Artifact Tool authored new placements (A11:G29/H11:N29 and A33:G51/H33:N51), transferred only authored anchor markers. Final Calc render shows all categories; chart-series XML unchanged.
2. **P2: Prepared-source columns clipped IDs/headers.** Widen required Lead/Sales item IDs/dates and Seller value columns; first header rows 48pt. Data and cell styles unchanged. Final viewports checked; raw sheets intentionally require horizontal/vertical scrolling.
3. **P1 reproduction guidance:** README referred to the whole-data authoring script that previously exceeded memory. Now points to `rebuild_in_codex.py`, documents runtime/LibreOffice/Python dependencies and optional full-build verification limit. Rebuild hook includes bounded layout repair. Syntax checks and repair execution passed; full rebuilt artifact is not claimed verified.
4. **Test-method correction, not a native Excel verdict:** first offline control copies retained old saved formula caches. Calc conversion kept 287 in slow-detail/headline while reading the new 14 control. That attempt had 8/11 pass and is preserved under `history/SCENARIO_FIRST_ATTEMPT.json`. All caches were cleared only in subsequent disposable test inputs; full evaluation then passed 11/11. Thus full formula semantics are verified; live UI dependency remains BLOCKED, not silently passed.
5. **Inspection-tool limit:** full Artifact Tool import exhausted a 4GB JavaScript heap; it was stopped without changing the input. Use Calc PDF viewports and small Artifact Tool layout fragments; do not repeat full-workbook import as the normal repair path.

## Giới hạn nghiệp vụ

8.000 sampled MQLs / 842 recorded wins; no-won record is not Lost/Open. 841 valid calendar cycles, median 14 days; 1 chronology anomaly retained in wins. 380 won sellers match source items, 376 have eligible delivered activity. 5.044 candidates -> 4.984 eligible items, 4.463 seller-order links vs 4.457 distinct global orders. Eligible price sum 664.858,00 original recorded units, excluding freight; not Olist revenue/profit/LTV/deal value. Samples have unequal coverage/follow-up. Controls are review assumptions. Findings support review/data collection, not causal claims or measured uplift.

## Một bước cần người dùng hoàn tất

Open đúng workbook cuối trong Microsoft Excel, kiểm không có Repair, Automatic + Ctrl+Alt+F9, kiểm Dashboard/charts; Lookups B3 30->14 và xác nhận 287->414, rồi restore 30, save/reopen. Chụp Dashboard sau đổi control và ghi Excel version. Checklist đầy đủ ở `docs/MICROSOFT_EXCEL_CHECKLIST.md`; không dùng lần mở synthetic workbook trước làm evidence cho bản này.

Không có native Desktop Excel tool được sử dụng, không có dữ liệu riêng tư/CV hoặc public publication/outreach. Phần artifact có AI hỗ trợ mạnh. Chưa dạy/quiz và chưa kiểm chứng independent mastery. Không tự nâng interview status từ việc auditor hiểu code.

## Truy vết

TAKEOVER_SCOPE.md; WORKBOOK_VALIDATION.json; SCENARIO_VALIDATION.json; LAYOUT_REPAIR.json; TAKEOVER_EXECUTION.json; AUDIT_CRITERIA.csv/json; preview/Dashboard.png; source_manifest.json. Historical report trước takeover nằm trong audit/history và không đóng native gate.

## Update STYLEFIX v3

Native open of a previously delivered Olist file required styles repair. See STYLE_FIX_HANDOFF.md and STYLE_REPAIR.json for the corrected orphan xfComplement, hash and retest. Baseline 139 checks were rerun on v3; scenario evidence is reused by exact non-style part preservation. Microsoft Excel v3 open remains pending.
