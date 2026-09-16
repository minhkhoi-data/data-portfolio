# DAX Reference

The semantic model contains **31 explicit measures** in the `_Measures` table. The TMDL file below is the source of truth for complete definitions, descriptions, folders, and formats:

`powerbi/EcommerceGrowth_PBIP/EcommerceGrowth.SemanticModel/definition/tables/_Measures.tmdl`

## Measure library

| Display folder | Measures |
|---|---|
| Traffic & Engagement | Sessions; Users; Engaged Sessions; Engagement Rate |
| Funnel | Product View Sessions; Add to Cart Sessions; Checkout Sessions; Purchase Sessions; Product View Rate; View to Cart Rate; Cart to Checkout Rate; Checkout to Purchase Rate; Session Conversion Rate; Funnel Stage Sessions |
| Commercial | Revenue; Transactions; AOV; Revenue per Session; Revenue per User; Units Sold |
| Customer | Purchasers; Repeat Purchasers; Repeat Purchase Rate; New User Session Conversion; Returning User Session Conversion |
| Product | Product Revenue; Product Units; Product Orders; Average Selling Price |
| Time Intelligence | Revenue Previous Month; Revenue MoM % |

## Core calculation patterns

Traffic and funnel measures use the session-grain fact:

```DAX
Sessions =
DISTINCTCOUNT ( FactSessions[session_id] )

Purchase Sessions =
CALCULATE ( [Sessions], FactSessions[purchase] = 1 )

Session Conversion Rate =
DIVIDE ( [Purchase Sessions], [Sessions] )

View to Cart Rate =
DIVIDE ( [Add to Cart Sessions], [Product View Sessions] )
```

Commercial measures use the order-grain fact so product lines cannot duplicate revenue:

```DAX
Revenue =
SUM ( FactOrders[total_revenue] )

Transactions =
DISTINCTCOUNT ( FactOrders[order_id] )

AOV =
DIVIDE ( [Revenue], [Transactions] )

Revenue per Session =
DIVIDE ( [Revenue], [Sessions] )
```

Repeat purchase is calculated within the active filter context:

```DAX
Repeat Purchasers =
VAR CustomerOrders =
    ADDCOLUMNS (
        VALUES ( FactOrders[user_id] ),
        "__OrderCount", CALCULATE ( DISTINCTCOUNT ( FactOrders[order_id] ) )
    )
RETURN
    COUNTROWS ( FILTER ( CustomerOrders, [__OrderCount] > 1 ) )

Repeat Purchase Rate =
DIVIDE ( [Repeat Purchasers], [Purchasers] )
```

The funnel chart uses a disconnected stage table rather than a duplicated wide table:

```DAX
Funnel Stage Sessions =
SWITCH (
    SELECTEDVALUE ( FunnelStage[Stage] ),
    "Sessions", [Sessions],
    "Product View", [Product View Sessions],
    "Add to Cart", [Add to Cart Sessions],
    "Checkout", [Checkout Sessions],
    "Purchase", [Purchase Sessions]
)
```

Time intelligence uses the shared date dimension:

```DAX
Revenue Previous Month =
CALCULATE ( [Revenue], DATEADD ( DimDate[date], -1, MONTH ) )

Revenue MoM % =
DIVIDE ( [Revenue] - [Revenue Previous Month], [Revenue Previous Month] )
```

## Interpretation guardrails

- Revenue is gross order revenue, not profit.
- Session conversion is purchase sessions divided by sessions, not purchaser conversion.
- Repeat Purchase Rate is period-sensitive because it uses orders visible in the active filter context.
- New/returning conversion is based on the prepared `is_new_user` session flag.
- Product metrics come from `FactOrderItems`; commercial totals come from `FactOrders`.

## Formatting

- Currency measures: two decimal places
- Rate measures: two decimal places
- Counts and units: whole numbers with thousands separators
