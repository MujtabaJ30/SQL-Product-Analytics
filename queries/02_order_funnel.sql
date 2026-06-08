-- Order Funnel Analysis
-- Purpose: Understand how orders progress through statuses and identify drop-off points.
-- Business Question: At which stage do we lose most orders? What conversion rate do we see?
-- Product Insight: Funnel analysis reveals friction points. If many orders get stuck at "approved" but not "shipped", fulfillment is the bottleneck.

WITH order_funnel AS (
  SELECT
    order_status,
    COUNT(*) AS order_count,
    ROUND(100.0 * COUNT(*) / MAX(COUNT(*)) OVER(), 2) AS pct_of_total
  FROM olist_orders_dataset
  GROUP BY order_status
)
SELECT * FROM order_funnel
ORDER BY order_count DESC;

-- Delivery funnel: of all orders with a valid purchase timestamp,
-- how many reach each delivery milestone?
SELECT
  COUNT(*) AS total_orders,
  COUNT(order_approved_at) AS approved,
  COUNT(order_delivered_carrier_date) AS with_carrier,
  COUNT(order_delivered_customer_date) AS delivered_to_customer,
  ROUND(100.0 * COUNT(order_delivered_customer_date) / COUNT(*), 2) AS delivery_completion_rate
FROM olist_orders_dataset
WHERE order_status NOT IN ('unavailable', 'canceled');

-- Step-by-step conversion with drop-off
SELECT
  COUNT(*) AS total_orders,
  COUNT(order_approved_at) AS approved,
  ROUND(100.0 * COUNT(order_approved_at) / COUNT(*), 1) AS approved_pct,
  COUNT(order_delivered_carrier_date) AS handed_to_carrier,
  ROUND(100.0 * COUNT(order_delivered_carrier_date) / NULLIF(COUNT(order_approved_at), 0), 1) AS carrier_conversion_pct,
  COUNT(order_delivered_customer_date) AS delivered,
  ROUND(100.0 * COUNT(order_delivered_customer_date) / NULLIF(COUNT(order_delivered_carrier_date), 0), 1) AS delivery_conversion_pct
FROM olist_orders_dataset
WHERE order_status NOT IN ('unavailable', 'canceled');
