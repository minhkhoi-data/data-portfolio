-- Run from the project root with DuckDB 1.4.3.
-- Input files are byte-identical copies of the audited Power BI data.
-- Identifiers remain VARCHAR; money uses fixed decimal. No analytical logic in Python.

CREATE OR REPLACE TABLE fact_sessions AS
SELECT
    "session_id" AS "session_id",
    "user_id" AS "user_id",
    CAST(NULLIF("session_date", '') AS DATE) AS "session_date",
    CAST(NULLIF("channel_id", '') AS BIGINT) AS "channel_id",
    CAST(NULLIF("device_id", '') AS BIGINT) AS "device_id",
    CAST(NULLIF("geo_id", '') AS BIGINT) AS "geo_id",
    "source" AS "source",
    "medium" AS "medium",
    CAST(NULLIF("is_new_user", '') AS BIGINT) AS "is_new_user",
    CAST(NULLIF("engagement_known", '') AS BIGINT) AS "engagement_known",
    CAST(NULLIF("engaged_session", '') AS BIGINT) AS "engaged_session",
    CAST(NULLIF("engagement_seconds", '') AS DECIMAL(20,6)) AS "engagement_seconds",
    CAST(NULLIF("pageviews", '') AS BIGINT) AS "pageviews",
    CAST(NULLIF("view_item", '') AS BIGINT) AS "view_item",
    CAST(NULLIF("add_to_cart", '') AS BIGINT) AS "add_to_cart",
    CAST(NULLIF("begin_checkout", '') AS BIGINT) AS "begin_checkout",
    CAST(NULLIF("purchase", '') AS BIGINT) AS "purchase",
    CAST(NULLIF("ordered_view_item", '') AS BIGINT) AS "ordered_view_item",
    CAST(NULLIF("ordered_add_to_cart", '') AS BIGINT) AS "ordered_add_to_cart",
    CAST(NULLIF("ordered_begin_checkout", '') AS BIGINT) AS "ordered_begin_checkout",
    CAST(NULLIF("ordered_purchase", '') AS BIGINT) AS "ordered_purchase",
    CAST(NULLIF("event_count", '') AS BIGINT) AS "event_count",
    CAST(NULLIF("purchase_event_count", '') AS BIGINT) AS "purchase_event_count",
    CAST(NULLIF("session_revenue", '') AS DECIMAL(20,6)) AS "session_revenue"
FROM read_csv('data/audited/fact_sessions.csv', header=true, all_varchar=true,
              nullstr='__SQL_PROJECT_NULL_SENTINEL__', parallel=false);

CREATE OR REPLACE TABLE fact_purchases AS
SELECT
    CAST(NULLIF("purchase_key", '') AS BIGINT) AS "purchase_key",
    "source_event_id" AS "source_event_id",
    "session_id" AS "session_id",
    "user_id" AS "user_id",
    CAST(NULLIF("purchase_date", '') AS DATE) AS "purchase_date",
    "event_timestamp" AS "event_timestamp",
    "transaction_id" AS "transaction_id",
    CAST(NULLIF("purchase_revenue_usd", '') AS DECIMAL(20,6)) AS "purchase_revenue_usd",
    CAST(NULLIF("total_quantity", '') AS BIGINT) AS "total_quantity",
    CAST(NULLIF("distinct_products", '') AS BIGINT) AS "distinct_products",
    "currency" AS "currency",
    CAST(NULLIF("transaction_id_known", '') AS BIGINT) AS "transaction_id_known",
    CAST(NULLIF("channel_id", '') AS BIGINT) AS "channel_id",
    CAST(NULLIF("device_id", '') AS BIGINT) AS "device_id",
    CAST(NULLIF("geo_id", '') AS BIGINT) AS "geo_id"
FROM read_csv('data/audited/fact_purchases.csv', header=true, all_varchar=true,
              nullstr='__SQL_PROJECT_NULL_SENTINEL__', parallel=false);

CREATE OR REPLACE TABLE dim_date AS
SELECT
    CAST(NULLIF("date", '') AS DATE) AS "date",
    CAST(NULLIF("year", '') AS BIGINT) AS "year",
    CAST(NULLIF("month_no", '') AS BIGINT) AS "month_no",
    "month" AS "month",
    "year_month" AS "year_month",
    CAST(NULLIF("week_start", '') AS DATE) AS "week_start",
    "day_of_week" AS "day_of_week",
    CAST(NULLIF("day_of_week_no", '') AS BIGINT) AS "day_of_week_no",
    CAST(NULLIF("is_weekend", '') AS BIGINT) AS "is_weekend"
FROM read_csv('data/audited/dim_date.csv', header=true, all_varchar=true,
              nullstr='__SQL_PROJECT_NULL_SENTINEL__', parallel=false);

CREATE OR REPLACE TABLE dim_channel AS
SELECT
    CAST(NULLIF("channel_id", '') AS BIGINT) AS "channel_id",
    "channel" AS "channel"
FROM read_csv('data/audited/dim_channel.csv', header=true, all_varchar=true,
              nullstr='__SQL_PROJECT_NULL_SENTINEL__', parallel=false);

CREATE OR REPLACE TABLE dim_device AS
SELECT
    CAST(NULLIF("device_id", '') AS BIGINT) AS "device_id",
    "device_category" AS "device_category"
FROM read_csv('data/audited/dim_device.csv', header=true, all_varchar=true,
              nullstr='__SQL_PROJECT_NULL_SENTINEL__', parallel=false);

CREATE OR REPLACE TABLE dim_geo AS
SELECT
    CAST(NULLIF("geo_id", '') AS BIGINT) AS "geo_id",
    "country" AS "country",
    "region_group" AS "region_group"
FROM read_csv('data/audited/dim_geo.csv', header=true, all_varchar=true,
              nullstr='__SQL_PROJECT_NULL_SENTINEL__', parallel=false);
