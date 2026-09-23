# QA Checks

These values are reference totals. After building the Power BI model, use them to verify that relationships and measures are correct.

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

## Revenue reconciliation

`FactOrders[total_revenue]` and `FactOrderItems[item_revenue]` should sum to the same number.

Expected:
- FactOrders revenue = $217,478.50
- FactOrderItems revenue = $217,478.50

## Relationship QA

If a channel slicer changes Sessions but does not change Revenue, the `DimChannel → FactOrders` relationship is missing or inactive.

If product charts show repeated total revenue for every product, use `FactOrderItems[item_revenue]`, not `FactOrders[total_revenue]`.
