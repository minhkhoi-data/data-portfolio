# Analytical data dictionary

Source strings and identifiers are preserved as text. Flags/counts are integers; date fields use source property calendar dates. Money is recorded USD purchase-event revenue. See METHODOLOGY.md for population and date-context definitions.

## FactSessions

| Column | Model type | Definition |
| --- | --- | --- |
| session_id | text | Composite source user_pseudo_id + \| + ga_session_id; unique observed-session key |
| user_id | text | Pseudonymous source user_pseudo_id; not an identified person |
| session_date | date | Property event_date of earliest observed session event |
| channel_id | integer | Shared dimension surrogate key; many-to-one fact relationship |
| device_id | integer | Shared dimension surrogate key; many-to-one fact relationship |
| geo_id | integer | Shared dimension surrogate key; many-to-one fact relationship |
| source | text | Raw first-user traffic_source; not session attribution |
| medium | text | Raw first-user traffic_medium; not session attribution |
| is_new_user | integer | 1: GA4 new indication; 0: returning indication; -1: unknown |
| engagement_known | integer | 1: at least one observed session_engaged flag; 0: no observed flag |
| engaged_session | integer | Maximum observed source session_engaged flag; null when unavailable |
| engagement_seconds | number | Sum of observed engagement_time_msec / 1000; not elapsed duration |
| pageviews | integer | Recorded page_view event count in this session |
| view_item | integer | 1 when any view_item event occurs in the session; 0 otherwise |
| add_to_cart | integer | 1 when any add_to_cart event occurs in the session; 0 otherwise |
| begin_checkout | integer | 1 when any begin_checkout event occurs in the session; 0 otherwise |
| purchase | integer | 1 when any purchase event occurs in the session; 0 otherwise |
| ordered_view_item | integer | 1 when view_item is reached with every prior commerce step at strictly increasing timestamps |
| ordered_add_to_cart | integer | 1 when add_to_cart is reached with every prior commerce step at strictly increasing timestamps |
| ordered_begin_checkout | integer | 1 when begin_checkout is reached with every prior commerce step at strictly increasing timestamps |
| ordered_purchase | integer | 1 when purchase is reached with every prior commerce step at strictly increasing timestamps |
| event_count | integer | All observed source events attached to this session |
| purchase_event_count | integer | Number of recorded purchase events attached to this session |
| session_revenue | fixed decimal USD | Sum of all recorded purchase-event USD revenue attached to this session |

## FactPurchases

| Column | Model type | Definition |
| --- | --- | --- |
| purchase_key | integer | Original source row number for this recorded purchase event |
| source_event_id | text | Source event_id, preserved without deduplication |
| session_id | text | Composite source user_pseudo_id + \| + ga_session_id; unique observed-session key |
| user_id | text | Pseudonymous source user_pseudo_id; not an identified person |
| purchase_date | date | Property event_date of the purchase event |
| event_timestamp | text | Source purchase-event timestamp, microseconds since Unix epoch, preserved text |
| transaction_id | text | Raw ecommerce_transaction_id; missing/repeated values are not corrected |
| purchase_revenue_usd | fixed decimal USD | Recorded USD revenue on this purchase event |
| total_quantity | integer | Source aggregate item quantity; nullable; no item rows |
| distinct_products | integer | Source aggregate unique item count; nullable; no SKU detail |
| currency | text | Source event currency label; money measure uses separately supplied USD field |
| transaction_id_known | integer | 1 when source transaction ID is not blank/masked/not-set; not proof of order uniqueness |
| channel_id | integer | Shared dimension surrogate key; many-to-one fact relationship |
| device_id | integer | Shared dimension surrogate key; many-to-one fact relationship |
| geo_id | integer | Shared dimension surrogate key; many-to-one fact relationship |

## DimDate

| Column | Model type | Definition |
| --- | --- | --- |
| date | date | Unique contiguous source-property date; date dimension key |
| year | integer | Calendar year |
| month_no | integer | Calendar month number 1–12 |
| month | text | Calendar month name |
| year_month | text | Calendar year-month YYYY-MM |
| week_start | date | Monday of calendar week, may precede source window |
| day_of_week | text | Calendar weekday name |
| day_of_week_no | integer | Monday=1 through Sunday=7 |
| is_weekend | integer | 1 for Saturday/Sunday; else 0 |

## DimChannel

| Column | Model type | Definition |
| --- | --- | --- |
| channel_id | integer | Shared dimension surrogate key; many-to-one fact relationship |
| channel | text | Declared first-user source/medium grouping including unknown/masked |

## DimDevice

| Column | Model type | Definition |
| --- | --- | --- |
| device_id | integer | Shared dimension surrogate key; many-to-one fact relationship |
| device_category | text | Source device category; missing/masked bucket explicit |

## DimGeo

| Column | Model type | Definition |
| --- | --- | --- |
| geo_id | integer | Shared dimension surrogate key; many-to-one fact relationship |
| country | text | Source country; blank/masked values retain explicit Unknown / masked grouping |
| region_group | text | Source geo_continent; not a sales territory |
