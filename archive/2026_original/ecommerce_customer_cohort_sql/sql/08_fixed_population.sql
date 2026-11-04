-- One common population observable through the maximum configured horizon.
-- A valid cumulative 7/14/30 trajectory; denominator stays fixed in every row.
WITH counts AS (
 SELECT w.horizon_days, count(*) AS eligible_users,
   count(*) FILTER (WHERE w.returned_by_horizon) AS returned_users,
   count(*) FILTER (WHERE w.purchased_by_horizon) AS purchasing_users,
   sum(w.purchase_events_by_horizon) AS purchase_events,
   sum(w.purchase_revenue_by_horizon_usd) AS purchase_revenue_usd
 FROM user_windows w
 WHERE w.first_observed_date + (SELECT max(horizon_days) FROM analysis_horizons) <= w.window_end
 GROUP BY w.horizon_days
)
SELECT *, returned_users * 1.0 / nullif(eligible_users,0) AS return_rate,
    purchasing_users * 1.0 / nullif(eligible_users,0) AS first_purchase_rate
FROM counts ORDER BY horizon_days;
