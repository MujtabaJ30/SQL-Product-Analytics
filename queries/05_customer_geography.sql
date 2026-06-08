-- Customer Geography Analysis
-- Purpose: Analyze order distribution, revenue, and average order value by state.
-- Business Question: Which states are our strongest markets? Are there untapped regions?
-- Product Insight: Geographic concentration means regional risk. Concentrating marketing in top states may maximize short-term ROI,
-- but expanding to underserved states may unlock long-term growth.
-- An interviewer might ask: "How would you use this data for a market expansion strategy?"

WITH state_metrics AS (
  SELECT
    c.customer_state,
    COUNT(DISTINCT o.order_id) AS order_count,
    COUNT(DISTINCT c.customer_unique_id) AS customer_count,
    ROUND(SUM(oi.price), 2) AS total_revenue,
    ROUND(AVG(oi.price), 2) AS avg_order_value
  FROM olist_orders_dataset o
  INNER JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
  INNER JOIN olist_order_items_dataset oi ON o.order_id = oi.order_id
  WHERE o.order_status NOT IN ('canceled', 'unavailable')
  GROUP BY c.customer_state
)
SELECT
  customer_state,
  order_count,
  customer_count,
  total_revenue,
  avg_order_value,
  ROUND(100.0 * order_count / SUM(order_count) OVER(), 2) AS pct_of_total_orders
FROM state_metrics
ORDER BY order_count DESC;

-- Top 10 cities by revenue
SELECT
  c.customer_city,
  c.customer_state,
  ROUND(SUM(oi.price), 2) AS revenue,
  COUNT(DISTINCT o.order_id) AS orders
FROM olist_orders_dataset o
INNER JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
INNER JOIN olist_order_items_dataset oi ON o.order_id = oi.order_id
WHERE o.order_status NOT IN ('canceled', 'unavailable')
GROUP BY c.customer_city, c.customer_state
ORDER BY revenue DESC
LIMIT 10;
