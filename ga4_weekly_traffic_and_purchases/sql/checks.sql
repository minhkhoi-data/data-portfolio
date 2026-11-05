-- Roll purchase events up to one row per session before joining.
WITH purchase_sessions AS (
    SELECT session_id, COUNT(*) AS event_count
    FROM fact_purchases
    GROUP BY session_id
)
SELECT
    (SELECT COUNT(*) FROM fact_sessions) AS input_sessions,
    COUNT(*) AS sessions_checked,
    SUM(CASE WHEN calendar.date IS NULL THEN 1 ELSE 0 END) AS missing_calendar_dates,
    SUM(sessions.purchase) AS sessions_flagged_with_purchase,
    COUNT(purchases.session_id) AS sessions_matched_to_purchase_events,
    (SELECT COUNT(*) FROM fact_purchases) AS input_purchase_events,
    COALESCE(SUM(purchases.event_count), 0) AS matched_purchase_events,
    SUM(CASE
        WHEN sessions.purchase = 1 AND purchases.session_id IS NULL THEN 1
        WHEN sessions.purchase = 0 AND purchases.session_id IS NOT NULL THEN 1
        ELSE 0
    END) AS purchase_flag_mismatches
FROM fact_sessions AS sessions
LEFT JOIN dim_date AS calendar
    ON sessions.session_date = calendar.date
LEFT JOIN purchase_sessions AS purchases
    ON sessions.session_id = purchases.session_id;
