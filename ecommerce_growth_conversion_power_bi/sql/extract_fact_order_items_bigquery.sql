-- GA4 -> purchase item analytical extract

SELECT
  PARSE_DATE('%Y%m%d', event_date) AS order_date,
  user_pseudo_id AS user_id,
  ecommerce.transaction_id AS order_id,

  item.item_id AS product_id,
  item.item_name AS product_name,
  item.item_category AS category,

  COALESCE(item.quantity, 1) AS quantity,
  item.price AS unit_price,
  COALESCE(item.quantity, 1) * item.price AS item_revenue,

  traffic_source.source AS source,
  traffic_source.medium AS medium,
  device.category AS device_category,
  geo.country AS country

FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`,
UNNEST(items) AS item

WHERE event_name = 'purchase'
  AND ecommerce.transaction_id IS NOT NULL;
