-- One control row. Run before interpreting any cohort output.
SELECT
  (SELECT min(session_date) FROM fact_sessions) AS window_start,
  (SELECT max(session_date) FROM fact_sessions) AS window_end,
  (SELECT count(DISTINCT session_date) FROM fact_sessions) AS observed_session_dates,
  (SELECT count(*) FROM fact_sessions) AS sessions,
  (SELECT count(DISTINCT session_id) FROM fact_sessions) AS unique_sessions,
  (SELECT sum(event_count) FROM fact_sessions) AS events_represented_by_audited_sessions,
  (SELECT count(*) FROM user_cohorts) AS users,
  (SELECT count(*) FROM fact_purchases) AS purchase_events,
  (SELECT count(DISTINCT user_id) FROM fact_purchases) AS purchasers,
  (SELECT sum(purchase_revenue_usd) FROM fact_purchases) AS purchase_revenue_usd,
  (SELECT count(*) FROM user_cohorts WHERE observed_channel_variants > 1) AS users_with_varying_channel,
  (SELECT count(*) FROM user_cohorts WHERE anchor_day_channel_variants > 1) AS users_with_ambiguous_anchor_channel,
  (SELECT count(*) FROM user_cohorts WHERE anchor_day_sessions > 1) AS users_with_multiple_anchor_day_sessions,
  (SELECT count(*) FROM user_cohorts WHERE days_to_first_purchase < 0) AS purchase_before_anchor_users,
  (SELECT count(*) FROM fact_purchases p ANTI JOIN fact_sessions s USING (session_id)) AS orphan_purchase_events,
  (SELECT count(*) FROM fact_purchases p JOIN fact_sessions s USING (session_id)
      WHERE p.user_id <> s.user_id) AS purchase_user_mismatches;
