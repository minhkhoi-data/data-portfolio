# QA Reference

## Expected business totals

| Check | Expected |
|---|---:|
| Sessions | 75,237 |
| Users | 32,000 |
| Transactions | 4,737 |
| Revenue | $217,478.50 |
| Session conversion | 6.2961% |
| AOV | $45.91 |
| Product-view sessions | 51,592 |
| Add-to-cart sessions | 15,090 |
| Checkout sessions | 8,111 |
| Purchase sessions | 4,737 |
| Purchasers | 4,428 |
| Repeat purchasers | 293 |

## Automated source checks

`python scripts/validate_project.py` verifies:

- unique session and order grains
- expected null patterns and binary funnel flags
- dimension-key referential integrity
- order-to-session and item-to-order consistency
- revenue and quantity reconciliation
- monotonic funnel stages
- expected portfolio totals
- valid PBIP/PBIR JSON files
- 5 report pages and 45 visual definitions
- visual positions within each page canvas
- every visual field and measure binding against the TMDL model

## Power BI Desktop acceptance

Before publishing screenshots or a `.pbix` file:

1. Open `EcommerceGrowth.pbip` with PBIP and PBIR preview features enabled.
2. Refresh all tables without credential, privacy-level, or source errors.
3. Confirm the business totals above in the report.
4. Test Channel and Month slicers on every page where they appear.
5. Check that each page fits a 16:9 canvas with no clipped titles, labels, or scrollbars in the intended visuals.
6. Confirm product charts are sorted by the intended measure and remain readable.
7. Save the project, reopen it, and confirm no pending-change or schema errors.
8. Export one clean 16:9 screenshot per page directly from the refreshed Power BI report.

Source checks prove the definitions are internally consistent. Only the Desktop acceptance pass proves the report opens, refreshes, and renders correctly.
