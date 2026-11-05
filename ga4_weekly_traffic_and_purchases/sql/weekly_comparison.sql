-- Start with the calendar so dates without any sessions still count toward coverage.
WITH weekly_rates AS (
    SELECT
        calendar.week_start,
        COUNT(sessions.session_id) AS total_sessions,
        COALESCE(SUM(sessions.purchase), 0) AS sessions_with_purchase,
        100.0 * SUM(sessions.purchase)
            / NULLIF(COUNT(sessions.session_id), 0) AS purchase_rate_pct
    FROM dim_date AS calendar
    LEFT JOIN fact_sessions AS sessions
        ON calendar.date = sessions.session_date
    GROUP BY calendar.week_start
    HAVING COUNT(DISTINCT calendar.date) = 7
),
weekly_with_previous AS (
    SELECT
        week_start,
        total_sessions,
        sessions_with_purchase,
        purchase_rate_pct,
        LAG(week_start) OVER (ORDER BY week_start) AS previous_week_start,
        LAG(purchase_rate_pct) OVER (ORDER BY week_start) AS previous_rate_pct
    FROM weekly_rates
)
SELECT
    week_start,
    total_sessions,
    sessions_with_purchase,
    ROUND(purchase_rate_pct, 2) AS purchase_rate_pct,
    CASE WHEN previous_week_start = DATE(week_start, '-7 days')
        THEN ROUND(previous_rate_pct, 2)
    END AS previous_week_rate_pct,
    CASE WHEN previous_week_start = DATE(week_start, '-7 days')
        THEN ROUND(purchase_rate_pct - previous_rate_pct, 2)
    END AS change_pp
FROM weekly_with_previous
ORDER BY week_start;
