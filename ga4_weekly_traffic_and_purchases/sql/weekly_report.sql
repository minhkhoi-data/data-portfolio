-- fact_sessions has one row per session. dim_date has one row per date.
SELECT
    calendar.week_start,
    COUNT(*) AS total_sessions,
    SUM(sessions.purchase) AS sessions_with_purchase,
    ROUND(100.0 * SUM(sessions.purchase) / COUNT(*), 2) AS session_purchase_rate_pct
FROM fact_sessions AS sessions
JOIN dim_date AS calendar
    ON sessions.session_date = calendar.date
GROUP BY calendar.week_start
ORDER BY calendar.week_start;
