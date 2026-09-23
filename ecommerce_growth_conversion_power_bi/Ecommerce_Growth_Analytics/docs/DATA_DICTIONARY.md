# Data Dictionary

## FactSessions

One row = one website session.

| Column | Type | Meaning |
|---|---|---|
| session_id | text | Unique session key |
| user_id | text | Anonymous user key |
| session_date | date | Session date |
| channel_id | whole number | Acquisition channel key |
| device_id | whole number | Device key |
| geo_id | whole number | Geography key |
| source | text | Traffic source |
| medium | text | Traffic medium |
| is_new_user | 0/1 | 1 for user's first observed session |
| engaged_session | 0/1 | Demo engagement flag |
| engagement_seconds | whole number | Session engagement duration |
| pageviews | whole number | Page views in session |
| view_item | 0/1 | Session reached product view |
| add_to_cart | 0/1 | Session reached add-to-cart |
| begin_checkout | 0/1 | Session reached checkout |
| purchase | 0/1 | Session completed purchase |
| order_id | text | Order key when purchase occurred |
| session_revenue | decimal | Revenue attributed to purchase session |

## FactOrders

One row = one order.

| Column | Type | Meaning |
|---|---|---|
| order_id | text | Unique transaction |
| session_id | text | Originating session |
| user_id | text | Anonymous purchaser |
| order_date | date | Purchase date |
| channel_id | whole number | Acquisition channel key |
| device_id | whole number | Device key |
| geo_id | whole number | Geography key |
| total_quantity | whole number | Units in order |
| distinct_products | whole number | Distinct SKUs |
| total_revenue | currency | Order revenue |

## FactOrderItems

One row = one product line within an order.

| Column | Type | Meaning |
|---|---|---|
| order_id | text | Transaction key |
| session_id | text | Originating session |
| user_id | text | Anonymous purchaser |
| order_date | date | Purchase date |
| product_key | whole number | Product dimension key |
| channel_id | whole number | Acquisition channel key |
| device_id | whole number | Device key |
| geo_id | whole number | Geography key |
| quantity | whole number | Units on line |
| unit_price | currency | Selling price per unit |
| item_revenue | currency | quantity × unit_price |

## Dimensions

### DimDate
Calendar attributes used for filtering and time intelligence.

### DimChannel
Marketing channel group.

### DimDevice
Device category: mobile, desktop, tablet.

### DimGeo
Country and region grouping.

### DimProduct
SKU, product name, category, subcategory, and base price.
