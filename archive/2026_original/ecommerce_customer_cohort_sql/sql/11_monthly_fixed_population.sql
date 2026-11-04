-- Matched-window comparison: each month uses only users observable through D30,
-- even in its D7/D14 row. January therefore represents January 1 only, not the
-- full January cohort, when the window ends January 31.
WITH counts AS (
 SELECT cohort_month,horizon_days,count(*) AS eligible_users,
   count(*) FILTER (WHERE returned_by_horizon) AS returned_users,
   count(*) FILTER (WHERE purchased_by_horizon) AS purchasing_users
 FROM user_windows
 WHERE first_observed_date + (SELECT max(horizon_days) FROM analysis_horizons) <= window_end
 GROUP BY cohort_month,horizon_days
)
SELECT *, returned_users * 1.0 / nullif(eligible_users,0) AS return_rate,
    purchasing_users * 1.0 / nullif(eligible_users,0) AS first_purchase_rate
FROM counts ORDER BY cohort_month,horizon_days;
