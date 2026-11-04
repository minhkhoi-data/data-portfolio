-- Day-level monitoring exposes within-month partial follow-up explicitly.
WITH counts AS (
 SELECT first_observed_date AS cohort_date, horizon_days,
   count(*) AS cohort_users,
   count(*) FILTER (WHERE is_eligible) AS eligible_users,
   count(*) FILTER (WHERE NOT is_eligible) AS excluded_incomplete_followup,
   count(*) FILTER (WHERE returned_by_horizon) AS returned_users,
   count(*) FILTER (WHERE purchased_by_horizon) AS purchasing_users
 FROM user_windows GROUP BY first_observed_date,horizon_days
)
SELECT *, returned_users * 1.0 / nullif(eligible_users,0) AS return_rate,
    purchasing_users * 1.0 / nullif(eligible_users,0) AS first_purchase_rate
FROM counts ORDER BY cohort_date,horizon_days;
