-- Descriptive timing among observed purchasers. Everyone remains in the output.
-- No-observed-purchase includes right-censored users, not proven non-buyers.
-- Population differs from the fully observable horizon cohorts.
WITH timing AS (
  SELECT user_id, CASE
    WHEN days_to_first_purchase IS NULL THEN 5
    WHEN days_to_first_purchase = 0 THEN 0
    WHEN days_to_first_purchase <= 7 THEN 1
    WHEN days_to_first_purchase <= 14 THEN 2
    WHEN days_to_first_purchase <= 30 THEN 3
    ELSE 4 END AS bucket_order
  FROM user_cohorts
), buckets AS (
  SELECT * FROM (VALUES
    (0, 'Day 0'), (1, 'Days 1-7'), (2, 'Days 8-14'),
    (3, 'Days 15-30'), (4, 'Day 31 or later'), (5, 'No observed purchase')
  ) b(bucket_order, timing_bucket)
)
SELECT b.bucket_order, b.timing_bucket, count(t.user_id) AS users,
  count(t.user_id) * 1.0 / nullif((SELECT count(*) FROM user_cohorts), 0) AS share_of_all_users,
  CASE WHEN b.bucket_order < 5 THEN count(t.user_id) * 1.0 /
       nullif((SELECT count(*) FROM user_cohorts WHERE first_purchase_date IS NOT NULL), 0)
       ELSE NULL END AS share_of_observed_purchasers
FROM buckets b LEFT JOIN timing t USING (bucket_order)
GROUP BY b.bucket_order, b.timing_bucket ORDER BY b.bucket_order;
