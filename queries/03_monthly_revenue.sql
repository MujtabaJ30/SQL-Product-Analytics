-- Monthly Revenue Trend
-- Purpose: Track revenue by month, calculate MoM growth, identify peak and trough periods.
-- Business Question: Is the platform growing month-over-month? Which months drive highest revenue?
-- Product Insight: Revenue trends reveal seasonality, growth trajectory, and business health.
-- An interviewer might ask: "What would you do if you saw declining MoM growth?"

WITH monthly_revenue AS (
  SELECT
    STRFTIME('%Y-%m', o.order_purchase_timestamp) AS year_month,
    ROUND(SUM(oi.price), 2) AS revenue,
    COUNT(DISTINCT o.order_id) AS order_count
  FROM olist_orders_dataset o
  INNER JOIN olist_order_items_dataset oi ON o.order_id = oi.order_id
  WHERE o.order_status NOT IN ('canceled', 'unavailable')
  GROUP BY STRFTIME('%Y-%m', o.order_purchase_timestamp)
)
SELECT
  year_month,
  revenue,
  order_count,
  ROUND(revenue / order_count, 2) AS avg_order_value,
  ROUND(
    100.0 * (revenue - LAG(revenue) OVER (ORDER BY year_month))
    / NULLIF(LAG(revenue) OVER (ORDER BY year_month), 0), 1
  ) AS mom_growth_pct
FROM monthly_revenue
ORDER BY year_month;
