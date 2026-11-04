-- Anchor device = deterministic first observed session's recorded device.
-- Users may use other devices later; this is not device-specific session CVR.
WITH counts AS (
 SELECT d.device_category AS anchor_device, w.horizon_days,
   count(*) AS cohort_users,
   count(*) FILTER (WHERE w.is_eligible) AS eligible_users,
   count(*) FILTER (WHERE NOT w.is_eligible) AS excluded_incomplete_followup,
   count(*) FILTER (WHERE w.returned_by_horizon) AS returned_users,
   count(*) FILTER (WHERE w.purchased_by_horizon) AS purchasing_users
 FROM user_windows w JOIN dim_device d ON w.anchor_device_id=d.device_id
 GROUP BY d.device_category,w.horizon_days
)
SELECT *, returned_users * 1.0 / nullif(eligible_users,0) AS return_rate,
    purchasing_users * 1.0 / nullif(eligible_users,0) AS first_purchase_rate
FROM counts ORDER BY horizon_days,anchor_device;
