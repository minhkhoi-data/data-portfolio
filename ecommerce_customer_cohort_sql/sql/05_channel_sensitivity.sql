-- Source channel labels vary within some pseudonymous users (obfuscated data).
-- Anchor = channel recorded on the deterministic first observed session.
-- Show ALL users and a CONSISTENT-CHANNEL subset; this is sensitivity analysis,
-- not a causal channel comparison or current-session attribution.
WITH populations AS (
  SELECT 'All observed users' AS population, w.* FROM user_windows w
  UNION ALL
  SELECT 'Consistent channel only' AS population, w.* FROM user_windows w
  WHERE observed_channel_variants = 1
), counts AS (
  SELECT p.population, c.channel AS anchor_channel, p.horizon_days,
    count(*) AS cohort_users,
    count(*) FILTER (WHERE p.is_eligible) AS eligible_users,
    count(*) FILTER (WHERE NOT p.is_eligible) AS excluded_incomplete_followup,
    count(*) FILTER (WHERE p.returned_by_horizon) AS returned_users,
    count(*) FILTER (WHERE p.purchased_by_horizon) AS purchasing_users
  FROM populations p JOIN dim_channel c ON p.anchor_channel_id = c.channel_id
  GROUP BY p.population, c.channel, p.horizon_days
)
SELECT *, returned_users * 1.0 / nullif(eligible_users, 0) AS return_rate,
    purchasing_users * 1.0 / nullif(eligible_users, 0) AS first_purchase_rate
FROM counts ORDER BY population, horizon_days, anchor_channel;
