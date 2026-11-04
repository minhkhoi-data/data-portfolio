-- Return = any later-day session start during days 1..H.
-- Purchase = first observed purchase during days 0..H, inclusive.
-- Each horizon uses its own fully observable population; do not treat the rows
-- as one user's cumulative trajectory. Use 08_fixed_population for that purpose.
WITH counts AS (
  SELECT horizon_days, count(*) AS cohort_users,
    count(*) FILTER (WHERE is_eligible) AS eligible_users,
    count(*) FILTER (WHERE NOT is_eligible) AS excluded_incomplete_followup,
    count(*) FILTER (WHERE returned_by_horizon) AS returned_users,
    count(*) FILTER (WHERE purchased_by_horizon) AS purchasing_users,
    sum(purchase_events_by_horizon) AS purchase_events,
    sum(purchase_revenue_by_horizon_usd) AS purchase_revenue_usd
  FROM user_windows GROUP BY horizon_days
)
SELECT *, returned_users * 1.0 / nullif(eligible_users, 0) AS return_rate,
    purchasing_users * 1.0 / nullif(eligible_users, 0) AS first_purchase_rate,
    purchase_revenue_usd / nullif(eligible_users, 0) AS purchase_revenue_per_eligible_user_usd
FROM counts ORDER BY horizon_days;
