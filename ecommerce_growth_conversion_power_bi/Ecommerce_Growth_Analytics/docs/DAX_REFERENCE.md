# DAX Measure Library

Create a dedicated table called `_Measures` and store the measures there.

## Traffic

```DAX
Sessions =
DISTINCTCOUNT ( FactSessions[session_id] )
```

```DAX
Users =
DISTINCTCOUNT ( FactSessions[user_id] )
```

```DAX
New User Sessions =
CALCULATE (
    [Sessions],
    FactSessions[is_new_user] = 1
)
```

```DAX
Returning User Sessions =
CALCULATE (
    [Sessions],
    FactSessions[is_new_user] = 0
)
```

```DAX
Engaged Sessions =
CALCULATE (
    [Sessions],
    FactSessions[engaged_session] = 1
)
```

```DAX
Engagement Rate =
DIVIDE ( [Engaged Sessions], [Sessions] )
```

```DAX
Avg Engagement Seconds =
AVERAGE ( FactSessions[engagement_seconds] )
```

```DAX
Avg Pageviews per Session =
DIVIDE (
    SUM ( FactSessions[pageviews] ),
    [Sessions]
)
```

## Funnel

```DAX
Product View Sessions =
CALCULATE (
    [Sessions],
    FactSessions[view_item] = 1
)
```

```DAX
Add to Cart Sessions =
CALCULATE (
    [Sessions],
    FactSessions[add_to_cart] = 1
)
```

```DAX
Checkout Sessions =
CALCULATE (
    [Sessions],
    FactSessions[begin_checkout] = 1
)
```

```DAX
Purchase Sessions =
CALCULATE (
    [Sessions],
    FactSessions[purchase] = 1
)
```

```DAX
Product View Rate =
DIVIDE ( [Product View Sessions], [Sessions] )
```

```DAX
View to Cart Rate =
DIVIDE ( [Add to Cart Sessions], [Product View Sessions] )
```

```DAX
Cart to Checkout Rate =
DIVIDE ( [Checkout Sessions], [Add to Cart Sessions] )
```

```DAX
Checkout to Purchase Rate =
DIVIDE ( [Purchase Sessions], [Checkout Sessions] )
```

```DAX
Session Conversion Rate =
DIVIDE ( [Purchase Sessions], [Sessions] )
```

```DAX
View to Cart Drop-off =
1 - [View to Cart Rate]
```

```DAX
Cart to Checkout Drop-off =
1 - [Cart to Checkout Rate]
```

```DAX
Checkout to Purchase Drop-off =
1 - [Checkout to Purchase Rate]
```

## Revenue

```DAX
Revenue =
SUM ( FactOrders[total_revenue] )
```

```DAX
Transactions =
DISTINCTCOUNT ( FactOrders[order_id] )
```

```DAX
AOV =
DIVIDE ( [Revenue], [Transactions] )
```

```DAX
Revenue per Session =
DIVIDE ( [Revenue], [Sessions] )
```

```DAX
Revenue per User =
DIVIDE ( [Revenue], [Users] )
```

```DAX
Units Sold =
SUM ( FactOrders[total_quantity] )
```

```DAX
Units per Order =
DIVIDE ( [Units Sold], [Transactions] )
```

## Customer

```DAX
Purchasers =
DISTINCTCOUNT ( FactOrders[user_id] )
```

```DAX
Repeat Purchasers =
VAR CustomerOrders =
    ADDCOLUMNS (
        VALUES ( FactOrders[user_id] ),
        "__OrderCount", CALCULATE ( DISTINCTCOUNT ( FactOrders[order_id] ) )
    )
RETURN
    COUNTROWS (
        FILTER ( CustomerOrders, [__OrderCount] > 1 )
    )
```

```DAX
Repeat Purchase Rate =
DIVIDE ( [Repeat Purchasers], [Purchasers] )
```

```DAX
New User Session Conversion =
DIVIDE (
    CALCULATE ( [Purchase Sessions], FactSessions[is_new_user] = 1 ),
    CALCULATE ( [Sessions], FactSessions[is_new_user] = 1 )
)
```

```DAX
Returning User Session Conversion =
DIVIDE (
    CALCULATE ( [Purchase Sessions], FactSessions[is_new_user] = 0 ),
    CALCULATE ( [Sessions], FactSessions[is_new_user] = 0 )
)
```

## Product

Use these measures with `DimProduct` fields.

```DAX
Product Revenue =
SUM ( FactOrderItems[item_revenue] )
```

```DAX
Product Units =
SUM ( FactOrderItems[quantity] )
```

```DAX
Product Orders =
DISTINCTCOUNT ( FactOrderItems[order_id] )
```

```DAX
Average Selling Price =
DIVIDE ( [Product Revenue], [Product Units] )
```

```DAX
Revenue Share % =
DIVIDE (
    [Product Revenue],
    CALCULATE ( [Product Revenue], ALL ( DimProduct ) )
)
```

## Time intelligence

Mark `DimDate[date]` as the Date table.

```DAX
Revenue Previous Month =
CALCULATE (
    [Revenue],
    DATEADD ( DimDate[date], -1, MONTH )
)
```

```DAX
Revenue MoM % =
DIVIDE (
    [Revenue] - [Revenue Previous Month],
    [Revenue Previous Month]
)
```

```DAX
Sessions Previous Month =
CALCULATE (
    [Sessions],
    DATEADD ( DimDate[date], -1, MONTH )
)
```

```DAX
Sessions MoM % =
DIVIDE (
    [Sessions] - [Sessions Previous Month],
    [Sessions Previous Month]
)
```

```DAX
Conversion Previous Month =
CALCULATE (
    [Session Conversion Rate],
    DATEADD ( DimDate[date], -1, MONTH )
)
```

```DAX
Conversion Change pp =
[Session Conversion Rate] - [Conversion Previous Month]
```

```DAX
Revenue 7D Rolling =
CALCULATE (
    [Revenue],
    DATESINPERIOD (
        DimDate[date],
        MAX ( DimDate[date] ),
        -7,
        DAY
    )
)
```

## Formatting

Use:
- Revenue, AOV, Revenue per Session, Product Revenue: Currency, 2 decimals
- Conversion / Engagement / Drop-off / Share: Percentage, 1–2 decimals
- Sessions / Users / Transactions / Units: Whole number
- Conversion Change pp: Percentage, 2 decimals
