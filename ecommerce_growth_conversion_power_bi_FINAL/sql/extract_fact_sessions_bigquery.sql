-- GA4 -> session-level analytical extract
-- Target:
-- bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*

WITH event_base AS (
  SELECT
    PARSE_DATE('%Y%m%d', event_date) AS session_date,
    user_pseudo_id AS user_id,
    event_name,
    event_timestamp,

    (SELECT value.int_value
     FROM UNNEST(event_params)
     WHERE key = 'ga_session_id') AS ga_session_id,

    COALESCE(
      (SELECT value.int_value
       FROM UNNEST(event_params)
       WHERE key = 'engagement_time_msec'),
      0
    ) AS engagement_time_msec,

    traffic_source.source AS source,
    traffic_source.medium AS medium,
    device.category AS device_category,
    geo.country AS country,

    ecommerce.transaction_id AS transaction_id,
    ecommerce.purchase_revenue AS purchase_revenue
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
),

session_rollup AS (
  SELECT
    CONCAT(
      user_id, '-',
      CAST(ga_session_id AS STRING)
    ) AS session_id,
    user_id,
    MIN(session_date) AS session_date,
    ANY_VALUE(source) AS source,
    ANY_VALUE(medium) AS medium,
    ANY_VALUE(device_category) AS device_category,
    ANY_VALUE(country) AS country,

    SUM(engagement_time_msec) / 1000.0 AS engagement_seconds,
    COUNTIF(event_name = 'page_view') AS pageviews,

    MAX(IF(event_name = 'view_item', 1, 0)) AS view_item,
    MAX(IF(event_name = 'add_to_cart', 1, 0)) AS add_to_cart,
    MAX(IF(event_name = 'begin_checkout', 1, 0)) AS begin_checkout,
    MAX(IF(event_name = 'purchase', 1, 0)) AS purchase,

    MAX(IF(event_name = 'purchase', transaction_id, NULL)) AS order_id,
    MAX(IF(event_name = 'purchase', purchase_revenue, NULL)) AS session_revenue
  FROM event_base
  WHERE ga_session_id IS NOT NULL
  GROUP BY session_id, user_id
),

first_seen AS (
  SELECT
    user_id,
    MIN(session_date) AS first_session_date
  FROM session_rollup
  GROUP BY user_id
)

SELECT
  s.* EXCEPT(source, medium, device_category, country),
  s.source,
  s.medium,

  CASE
    WHEN LOWER(s.medium) = 'organic' THEN 'Organic Search'
    WHEN LOWER(s.medium) IN ('cpc', 'ppc', 'paidsearch') THEN 'Paid Search'
    WHEN LOWER(s.medium) = 'email' THEN 'Email'
    WHEN LOWER(s.medium) = 'display' THEN 'Display'
    WHEN LOWER(s.medium) IN ('social', 'social-network', 'social-media') THEN 'Organic Social'
    WHEN LOWER(s.medium) = 'referral' THEN 'Referral'
    WHEN s.source = '(direct)' OR s.medium = '(none)' THEN 'Direct'
    ELSE 'Other'
  END AS channel,

  s.device_category,
  s.country,

  IF(s.session_date = f.first_session_date, 1, 0) AS is_new_user,

  IF(
    s.engagement_seconds >= 10
    OR s.pageviews >= 2
    OR s.purchase = 1,
    1,
    0
  ) AS engaged_session

FROM session_rollup s
LEFT JOIN first_seen f USING (user_id);
