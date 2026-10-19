# DAX measure definitions

These are delivered definitions, not native execution evidence. Methodology describes eligibility, dates and interpretation.

## Sessions

```dax
COALESCE(DISTINCTCOUNT(FactSessions[session_id]), 0)
```

Format: #,##0

## Users

```dax
COALESCE(DISTINCTCOUNT(FactSessions[user_id]), 0)
```

Format: #,##0

## Engaged Sessions

```dax
CALCULATE([Sessions], FactSessions[engaged_session] = 1)
```

Format: #,##0

## Known Engagement Sessions

```dax
CALCULATE([Sessions], FactSessions[engagement_known] = 1)
```

Format: #,##0

## Engagement Rate

```dax
DIVIDE([Engaged Sessions], [Known Engagement Sessions])
```

Format: 0.00%

## Product View Sessions

```dax
CALCULATE([Sessions], FactSessions[ordered_view_item] = 1)
```

Format: #,##0

## Add to Cart Sessions

```dax
CALCULATE([Sessions], FactSessions[ordered_add_to_cart] = 1)
```

Format: #,##0

## Checkout Sessions

```dax
CALCULATE([Sessions], FactSessions[ordered_begin_checkout] = 1)
```

Format: #,##0

## Strict Journey Purchase Sessions

```dax
CALCULATE([Sessions], FactSessions[ordered_purchase] = 1)
```

Format: #,##0

## Purchase Sessions

```dax
CALCULATE([Sessions], FactSessions[purchase] = 1)
```

Format: #,##0

## Product View Rate

```dax
DIVIDE([Product View Sessions], [Sessions])
```

Format: 0.00%

## View to Cart Rate

```dax
DIVIDE([Add to Cart Sessions], [Product View Sessions])
```

Format: 0.00%

## Cart to Checkout Rate

```dax
DIVIDE([Checkout Sessions], [Add to Cart Sessions])
```

Format: 0.00%

## Checkout to Purchase Rate

```dax
DIVIDE([Strict Journey Purchase Sessions], [Checkout Sessions])
```

Format: 0.00%

## Session Conversion Rate

```dax
DIVIDE([Purchase Sessions], [Sessions])
```

Format: 0.00%

## Revenue

```dax
SUM(FactPurchases[purchase_revenue_usd])
```

Format: $#,##0.00

## Purchase Events

```dax
COALESCE(COUNTROWS(FactPurchases), 0)
```

Format: #,##0

## Average Purchase Event Value

```dax
DIVIDE([Revenue], [Purchase Events])
```

Format: $#,##0.00

## Session-attributed Revenue

```dax
SUM(FactSessions[session_revenue])
```

Format: $#,##0.00

## Revenue per Session

```dax
DIVIDE([Session-attributed Revenue], [Sessions])
```

Format: $#,##0.00

## Revenue per User

```dax
DIVIDE([Session-attributed Revenue], [Users])
```

Format: $#,##0.00

## Reported Item Quantity

```dax
SUM(FactPurchases[total_quantity])
```

Format: #,##0

## Purchasers

```dax
COALESCE(DISTINCTCOUNT(FactPurchases[user_id]), 0)
```

Format: #,##0

## Multiple-event Purchasers

```dax
VAR Activity = ADDCOLUMNS(VALUES(FactPurchases[user_id]), "__Events", CALCULATE(COUNTROWS(FactPurchases))) RETURN COUNTROWS(FILTER(Activity, [__Events] > 1))
```

Format: #,##0

## Multiple-event Purchaser Share

```dax
DIVIDE([Multiple-event Purchasers], [Purchasers])
```

Format: 0.00%

## New User Session Conversion

```dax
DIVIDE(CALCULATE([Purchase Sessions], FactSessions[is_new_user] = 1), CALCULATE([Sessions], FactSessions[is_new_user] = 1))
```

Format: 0.00%

## Returning User Session Conversion

```dax
DIVIDE(CALCULATE([Purchase Sessions], FactSessions[is_new_user] = 0), CALCULATE([Sessions], FactSessions[is_new_user] = 0))
```

Format: 0.00%

## Funnel Stage Sessions

```dax
SWITCH(SELECTEDVALUE(FunnelStage[Stage]), "Sessions", [Sessions], "Product View", [Product View Sessions], "Add to Cart", [Add to Cart Sessions], "Checkout", [Checkout Sessions], "Purchase", [Strict Journey Purchase Sessions])
```

Format: #,##0

## Revenue Previous Month

```dax
VAR FullMonth = HASONEVALUE(DimDate[year_month]) && COUNTROWS(VALUES(DimDate[date])) = DAY(EOMONTH(MAX(DimDate[date]), 0)) VAR StartPrevious = EOMONTH(MAX(DimDate[date]), -2) + 1 VAR EndPrevious = EOMONTH(MAX(DimDate[date]), -1) RETURN IF(FullMonth, CALCULATE([Revenue], REMOVEFILTERS(DimDate), DATESBETWEEN(DimDate[date], StartPrevious, EndPrevious)), BLANK())
```

Format: $#,##0.00

## Revenue MoM %

```dax
DIVIDE([Revenue] - [Revenue Previous Month], [Revenue Previous Month])
```

Format: 0.00%

## Product Data Status

```dax
"No item-level data"
```

Format: text

## Experiment Data Status

```dax
"No assignment data"
```

Format: text

## Attribution Scope

```dax
"First-user acquisition"
```

Format: text

## Revenue Scope

```dax
"Recorded purchase events"
```

Format: text

## Snapshot Note

```dax
"Google GA4 public sample | Nov 2020 - Jan 2021 | USD purchase-event revenue | Obfuscated data"
```

Format: text
