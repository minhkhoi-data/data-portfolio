-- One interval between successive distinct session-active dates per user.
-- Same-day sessions have already been collapsed in user_activity_days.
-- This is an interval distribution, not a user-level retention probability.
WITH gaps AS (
  SELECT *, CASE WHEN gap_days <= 7 THEN 0 WHEN gap_days <= 14 THEN 1
                WHEN gap_days <= 30 THEN 2 ELSE 3 END AS bucket_order
  FROM user_activity_days WHERE previous_activity_date IS NOT NULL
), buckets AS (
  SELECT * FROM (VALUES (0,'1-7 days'), (1,'8-14 days'),
    (2,'15-30 days'), (3,'31+ days')) b(bucket_order,gap_bucket)
)
SELECT b.bucket_order, b.gap_bucket, count(g.user_id) AS observed_intervals,
       count(DISTINCT g.user_id) AS users_contributing,
       count(g.user_id) * 1.0 / nullif((SELECT count(*) FROM gaps),0) AS share_of_intervals
FROM buckets b LEFT JOIN gaps g USING (bucket_order)
GROUP BY b.bucket_order,b.gap_bucket ORDER BY b.bucket_order;
