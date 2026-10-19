-- Grain: one pseudonymous user, then one user x horizon.
-- Day 0 is MIN(session_date), not a proven first-ever visit.
-- Session-date ties are resolved by session_id for reproducibility, not chronology.
CREATE OR REPLACE TABLE observation_window AS
SELECT min(session_date) AS window_start, max(session_date) AS window_end
FROM fact_sessions;

CREATE OR REPLACE TABLE analysis_horizons AS
SELECT * FROM (VALUES (7), (14), (30)) AS h(horizon_days);

CREATE OR REPLACE TABLE user_activity_days AS
WITH daily AS (
    SELECT user_id, session_date AS activity_date, count(*) AS sessions
    FROM fact_sessions GROUP BY user_id, session_date
)
SELECT *,
    row_number() OVER (PARTITION BY user_id ORDER BY activity_date) AS activity_day_number,
    lag(activity_date) OVER (PARTITION BY user_id ORDER BY activity_date) AS previous_activity_date,
    date_diff('day', lag(activity_date) OVER (
        PARTITION BY user_id ORDER BY activity_date), activity_date) AS gap_days
FROM daily;

CREATE OR REPLACE TABLE user_cohorts AS
WITH ranked_sessions AS (
    SELECT *, row_number() OVER (
        PARTITION BY user_id ORDER BY session_date, session_id
    ) AS session_rank
    FROM fact_sessions
), first_session AS (
    SELECT user_id, session_id AS anchor_session_id,
           session_date AS first_observed_date, channel_id AS anchor_channel_id,
           device_id AS anchor_device_id, is_new_user AS anchor_new_user_flag
    FROM ranked_sessions WHERE session_rank = 1
), session_profile AS (
    SELECT user_id, count(*) AS observed_sessions,
           count(DISTINCT channel_id) AS observed_channel_variants
    FROM fact_sessions GROUP BY user_id
), purchase_profile AS (
    -- Aggregate purchases before joining to sessions: prevent fact-to-fact fan-out.
    SELECT user_id, min(purchase_date) AS first_purchase_date,
           count(*) AS observed_purchase_events,
           sum(purchase_revenue_usd) AS observed_purchase_revenue_usd
    FROM fact_purchases GROUP BY user_id
), return_profile AS (
    SELECT d.user_id, min(d.activity_date) AS first_return_date
    FROM user_activity_days d JOIN first_session f USING (user_id)
    WHERE d.activity_date > f.first_observed_date GROUP BY d.user_id
), anchor_day_profile AS (
    SELECT s.user_id, count(*) AS anchor_day_sessions,
           count(DISTINCT s.channel_id) AS anchor_day_channel_variants
    FROM fact_sessions s JOIN first_session f USING (user_id)
    WHERE s.session_date = f.first_observed_date GROUP BY s.user_id
)
SELECT f.*, CAST(date_trunc('month', f.first_observed_date) AS DATE) AS cohort_month,
       s.observed_sessions, s.observed_channel_variants,
       a.anchor_day_sessions, a.anchor_day_channel_variants,
       r.first_return_date,
       date_diff('day', f.first_observed_date, r.first_return_date) AS days_to_first_return,
       p.first_purchase_date,
       date_diff('day', f.first_observed_date, p.first_purchase_date) AS days_to_first_purchase,
       coalesce(p.observed_purchase_events, 0) AS observed_purchase_events,
       coalesce(p.observed_purchase_revenue_usd, 0)::DECIMAL(20,6) AS observed_purchase_revenue_usd
FROM first_session f
JOIN session_profile s USING (user_id)
JOIN anchor_day_profile a USING (user_id)
LEFT JOIN return_profile r USING (user_id)
LEFT JOIN purchase_profile p USING (user_id);

CREATE OR REPLACE TABLE user_windows AS
WITH window_purchases AS (
    SELECT u.user_id, h.horizon_days,
           sum(p.purchase_revenue_usd)::DECIMAL(20,6) AS purchase_revenue_usd,
           count(*) AS purchase_events
    FROM user_cohorts u CROSS JOIN analysis_horizons h
    JOIN fact_purchases p ON p.user_id = u.user_id
      AND p.purchase_date BETWEEN u.first_observed_date
                              AND u.first_observed_date + h.horizon_days
    GROUP BY u.user_id, h.horizon_days
), eligible AS (
    SELECT u.*, h.horizon_days, w.window_end,
           u.first_observed_date + h.horizon_days <= w.window_end AS is_eligible
    FROM user_cohorts u CROSS JOIN analysis_horizons h CROSS JOIN observation_window w
)
SELECT e.*,
       CASE WHEN is_eligible THEN coalesce(days_to_first_return BETWEEN 1 AND horizon_days, false)
            ELSE NULL END AS returned_by_horizon,
       CASE WHEN is_eligible THEN coalesce(days_to_first_purchase BETWEEN 0 AND horizon_days, false)
            ELSE NULL END AS purchased_by_horizon,
       CASE WHEN is_eligible THEN coalesce(p.purchase_events, 0) ELSE NULL END AS purchase_events_by_horizon,
       CASE WHEN is_eligible THEN coalesce(p.purchase_revenue_usd, 0)::DECIMAL(20,6)
            ELSE NULL END AS purchase_revenue_by_horizon_usd
FROM eligible e LEFT JOIN window_purchases p USING (user_id, horizon_days);
