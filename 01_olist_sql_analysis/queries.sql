/* =====================================================================
   OLIST E-COMMERCE – SQL ANALYSIS
   Author: Pham Minh Khoi
   Database: PostgreSQL
   Schema: raw
   ===================================================================== */

/* =====================================================================
   A. Orders & Revenue Performance
   ===================================================================== */

---------------------------------------------------------------
-- Q1.1 – Monthly Revenue Overview
-- Goal:
--   • Track monthly orders, revenue, and average order value (AOV).
--   • Focus only on completed business (delivered orders).
---------------------------------------------------------------

SELECT
    date_trunc('month', o.order_purchase_timestamp::timestamp)::date AS month,
    COUNT(DISTINCT o.order_id)                                   AS order_count,
    SUM(p.payment_value)                                         AS revenue,
    ROUND(
        SUM(p.payment_value)::numeric
        / NULLIF(COUNT(DISTINCT o.order_id), 0),
        2
    )                                                            AS avg_order_value
FROM raw.orders o
JOIN raw.order_payments p
    ON p.order_id = o.order_id
WHERE o.order_status = 'delivered'
GROUP BY 1
ORDER BY 1;


---------------------------------------------------------------
-- Q1.2 - Order Status Distribution (Operational Funnel)
-- Goal:
--   • Assess operational outcomes by order status.
--   • Evaluate marketplace health via delivered vs failed vs in-progress orders.
-- Notes:
--   • This reflects a post-operational snapshot, not a real-time conversion funnel.
---------------------------------------------------------------

SELECT
    CASE
        WHEN order_status = 'delivered' THEN 'Delivered'
        WHEN order_status IN ('canceled', 'unavailable') THEN 'Failed'
        ELSE 'In Progress'
    END AS funnel_stage,
    COUNT(*) AS order_count,
    ROUND(
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (),
        2
    ) AS percentage
FROM raw.orders
GROUP BY funnel_stage
ORDER BY order_count DESC;

---------------------------------------------------------------
-- Q1.3 – Daily / Weekly Seasonality
-- Goal:
--   • Analyze sales seasonality by day-of-week and possibly by date.
--   • Use delivered orders as baseline.
---------------------------------------------------------------

-- TODO: write query for daily / weekly sales patterns.


---------------------------------------------------------------
-- Q1.4 – Freight Impact on Revenue
-- Goal:
--   • Compare product_value vs freight_value by customer state.
--   • Understand where shipping is relatively expensive.
---------------------------------------------------------------

-- TODO: write query joining orders, order_items, customers
--       and aggregating freight vs product value by state.



/* =====================================================================
   B. Customer Behavior & Loyalty
   ===================================================================== */

---------------------------------------------------------------
-- Q2.1 – Returning vs One-time Customers
-- Goal:
--   • Count how many customers ordered 1 time, 2–3 times, 4+ times.
---------------------------------------------------------------

-- TODO: write query grouping customers by order_count buckets.


---------------------------------------------------------------
-- Q2.2 – Customer LTV Approximation
-- Goal:
--   • Compute total order value per customer (delivered orders).
--   • Can later be bucketed into LTV tiers (low/medium/high).
---------------------------------------------------------------

-- TODO: write query summing payment_value per customer_id.


---------------------------------------------------------------
-- Q2.3 – Average Delivery Time per Customer Region
-- Goal:
--   • Compute avg delivery time (delivered_date - purchase_date)
--     by customer_state (or city).
---------------------------------------------------------------

-- TODO: write query with date_diff between delivered_customer_date
--       and purchase_timestamp, grouped by region.



/* =====================================================================
   C. Delivery & Logistics Efficiency
   ===================================================================== */

---------------------------------------------------------------
-- Q3.1 – Actual vs Estimated Delivery Time
-- Goal:
--   • Compare actual delivery_time vs estimated (carrier_date to limit_date).
--   • Detect whether Olist tends to under- or over-estimate.
---------------------------------------------------------------

-- TODO: write query with:
--   actual_days     = delivered_customer_date - purchase_timestamp
--   estimated_days  = order_estimated_delivery_date - purchase_timestamp


---------------------------------------------------------------
-- Q3.2 – Late Deliveries by State & Seller
-- Goal:
--   • Identify late deliveries and rank states / sellers by count and rate.
---------------------------------------------------------------

-- TODO: write query:
--   late_flag = delivered_customer_date > order_estimated_delivery_date.


---------------------------------------------------------------
-- Q3.3 – Inconsistent Timestamps
-- Goal:
--   • Find obviously wrong data (e.g., delivered before shipped).
---------------------------------------------------------------

-- TODO: write query selecting orders where
--   delivered_customer_date < order_delivered_carrier_date
--   OR other weird sequences.



/* =====================================================================
   D. Product & Category Insights
   ===================================================================== */

---------------------------------------------------------------
-- Q4.1 – Best-selling Product Categories
-- Goal:
--   • Rank categories by:
--       - number of orders
--       - total quantity
--       - total revenue
---------------------------------------------------------------

-- TODO: write query joining order_items, products,
--       product_category_name_translation (for English names),
--       aggregated by category.


---------------------------------------------------------------
-- Q4.2 – Categories with Highest Review Score
-- Goal:
--   • Compute avg review_score per product category.
---------------------------------------------------------------

-- TODO: write query joining order_reviews, order_items, products,
--       grouped by category with avg(review_score) and review_count.


---------------------------------------------------------------
-- Q4.3 – Price Distribution across Categories
-- Goal:
--   • Explore unit_price distribution (min, p25, median, p75, max)
--     by product category.
---------------------------------------------------------------

-- TODO: write query using price stats per category
--       (you can start with min/avg/max; later add percentiles with
--        PostgreSQL percentile_cont).



/* =====================================================================
   E. Seller Performance
   ===================================================================== */

---------------------------------------------------------------
-- Q5.1 – Top Sellers by Revenue
-- Goal:
--   • Rank sellers by total revenue and number of delivered orders.
---------------------------------------------------------------

-- TODO: write query joining order_items, orders, order_payments, sellers,
--       grouping by seller_id.


---------------------------------------------------------------
-- Q5.2 – Seller Cancellation Rate
-- Goal:
--   • For each seller, compute:
--       - total orders linked to that seller
--       - canceled orders
--       - cancellation_rate = canceled / total
---------------------------------------------------------------

-- TODO: write query using orders + order_items per seller.


---------------------------------------------------------------
-- Q5.3 – Seller Average Delivery Time
-- Goal:
--   • For each seller, compute avg customer delivery time.
---------------------------------------------------------------

-- TODO: write query using orders + order_items + sellers,
--       calculating delivered_customer_date - purchase_timestamp.



/* =====================================================================
   END OF FILE
   ===================================================================== */
