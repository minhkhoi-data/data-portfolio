# Data Model

## Grain

- `FactSessions`: session grain
- `FactOrders`: order grain
- `FactOrderItems`: order-line grain

Do not merge these into one table. Each fact answers a different type of question and merging would duplicate revenue or sessions.

## Relationships

Create all relationships as **1 → many** and **single direction**.

| Dimension | Fact | Key |
|---|---|---|
| DimDate | FactSessions | Date → session_date |
| DimDate | FactOrders | Date → order_date |
| DimDate | FactOrderItems | Date → order_date |
| DimChannel | FactSessions | channel_id |
| DimChannel | FactOrders | channel_id |
| DimChannel | FactOrderItems | channel_id |
| DimDevice | FactSessions | device_id |
| DimDevice | FactOrders | device_id |
| DimDevice | FactOrderItems | device_id |
| DimGeo | FactSessions | geo_id |
| DimGeo | FactOrders | geo_id |
| DimGeo | FactOrderItems | geo_id |
| DimProduct | FactOrderItems | product_key |

## Why a star schema?

A star schema keeps business dimensions reusable across several fact tables. It also avoids fact-to-fact relationships, bidirectional filtering, and ambiguous filter paths.

## Measure ownership

Use:
- `FactSessions` for traffic, funnel, engagement, session conversion
- `FactOrders` for revenue, orders, AOV, purchasers, repeat purchase
- `FactOrderItems` for SKU/category revenue and units
