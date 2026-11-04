-- GoogleSQL. Independent source counts for the SAME selected event classes.
-- These are raw source controls, not reconciled orders or final portfolio KPIs.
-- Preserve the result as source_profile.csv; keep job ID/date with the exports.
WITH source AS (
 SELECT
  SUBSTR(_TABLE_SUFFIX, 1, 6) AS source_month,
  event_name,
  user_pseudo_id,
  (SELECT MAX(COALESCE(value.int_value, SAFE_CAST(value.string_value AS INT64))) FROM UNNEST(event_params) WHERE key = 'ga_session_id') AS ga_session_id,
  ecommerce.purchase_revenue_in_usd AS purchase_revenue_in_usd
 FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
 WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210131'
   AND event_name IN ('first_visit', 'session_start', 'page_view', 'user_engagement', 'view_item', 'add_to_cart', 'begin_checkout', 'add_shipping_info', 'add_payment_info', 'purchase', 'refund')
)
SELECT
 source_month,
 COUNT(*) AS exported_events,
 COUNTIF(event_name = 'purchase') AS purchase_events,
 COUNTIF(event_name = 'refund') AS refund_events,
 COUNTIF(user_pseudo_id IS NULL OR user_pseudo_id = '') AS missing_user_events,
 COUNTIF(ga_session_id IS NULL) AS missing_session_events,
 ROUND(SUM(IF(event_name = 'purchase', COALESCE(purchase_revenue_in_usd, 0), 0)), 2) AS purchase_revenue_usd_sum
FROM source
GROUP BY source_month
ORDER BY source_month;
