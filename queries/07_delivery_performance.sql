-- Delivery Performance Analysis
-- Purpose: Measure actual delivery times vs estimates, identify late delivery patterns.
-- Business Question: How reliable is our delivery estimation? Which categories/regions have the worst delays?
-- Product Insight: Late deliveries directly impact customer satisfaction and retention.
-- A category with 40%+ late deliveries needs operational intervention before it becomes a churn driver.
-- An interviewer might ask: "What metrics would you track on a delivery performance dashboard?"

WITH delivery_metrics AS (
  SELECT
    o.order_id,
    o.order_purchase_timestamp,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    JULIANDAY(o.order_delivered_customer_date) - JULIANDAY(o.order_purchase_timestamp) AS actual_delivery_days,
    JULIANDAY(o.order_estimated_delivery_date) - JULIANDAY(o.order_purchase_timestamp) AS estimated_delivery_days,
    CASE
      WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1
      ELSE 0
    END AS is_late
  FROM olist_orders_dataset o
  WHERE o.order_status = 'delivered'
    AND o.order_delivered_customer_date IS NOT NULL
)
SELECT
  ROUND(AVG(actual_delivery_days), 1) AS avg_actual_delivery_days,
  ROUND(AVG(estimated_delivery_days), 1) AS avg_estimated_delivery_days,
  ROUND(AVG(actual_delivery_days - estimated_delivery_days), 1) AS avg_deviation_days,
  SUM(is_late) AS late_orders,
  ROUND(100.0 * SUM(is_late) / COUNT(*), 1) AS late_order_pct
FROM delivery_metrics;

-- Late delivery rate by product category
SELECT
  COALESCE(t.product_category_name_english, p.product_category_name) AS category,
  COUNT(*) AS total_orders,
  SUM(CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1 ELSE 0 END) AS late_orders,
  ROUND(100.0 *
    SUM(CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1 ELSE 0 END)
    / COUNT(*), 1) AS late_pct,
  ROUND(AVG(JULIANDAY(o.order_delivered_customer_date) - JULIANDAY(o.order_purchase_timestamp)), 1) AS avg_delivery_days
FROM olist_orders_dataset o
INNER JOIN olist_order_items_dataset oi ON o.order_id = oi.order_id
INNER JOIN olist_products_dataset p ON oi.product_id = p.product_id
LEFT JOIN product_category_name_translation t ON p.product_category_name = t.product_category_name
WHERE o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL
  AND p.product_category_name IS NOT NULL
GROUP BY category
ORDER BY late_pct DESC
LIMIT 15;
