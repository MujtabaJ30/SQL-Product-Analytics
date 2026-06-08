-- Executive Summary: Olist E-Commerce Health Dashboard
-- Purpose: Return the 8 most important KPIs in a single query for a stakeholder dashboard.
-- Business Question: "How is the business doing?" — answered at a glance.
-- Product Insight: A PM should always have a single source of truth for business health.
-- An interviewer might ask: "Why these 8 metrics? What would you add or remove?"
-- Interview answer: "These 8 cover the AARRR framework (Acquisition, Activation, Revenue, Retention, Referral).
--   I'd add repeat purchase rate and customer acquisition cost if that data were available."

WITH kpis AS (
  SELECT
    (SELECT COUNT(DISTINCT customer_unique_id) FROM olist_customers_dataset) AS total_customers,
    (SELECT COUNT(DISTINCT order_id) FROM olist_orders_dataset WHERE order_status NOT IN ('canceled', 'unavailable')) AS total_orders,
    (SELECT COUNT(DISTINCT order_id) FROM olist_orders_dataset WHERE order_status = 'delivered') AS delivered_orders,
    (SELECT ROUND(SUM(oi.price) + SUM(oi.freight_value), 2)
     FROM olist_order_items_dataset oi
     INNER JOIN olist_orders_dataset o ON oi.order_id = o.order_id
     WHERE o.order_status NOT IN ('canceled', 'unavailable')) AS total_revenue,
    (SELECT ROUND(AVG(review_score), 2) FROM olist_order_reviews_dataset) AS avg_review_score,
    (SELECT ROUND(AVG(JULIANDAY(order_delivered_customer_date) - JULIANDAY(order_purchase_timestamp)), 1)
     FROM olist_orders_dataset WHERE order_status = 'delivered') AS avg_delivery_days,
    (SELECT ROUND(SUM(oi.price), 2) / COUNT(DISTINCT o.order_id)
     FROM olist_order_items_dataset oi
     INNER JOIN olist_orders_dataset o ON oi.order_id = o.order_id
     WHERE o.order_status NOT IN ('canceled', 'unavailable')) AS avg_order_value,
    (SELECT ROUND(AVG(payment_value), 2) FROM olist_order_payments_dataset) AS avg_payment_value
)
SELECT
  total_customers,
  total_orders,
  delivered_orders,
  total_revenue,
  avg_review_score,
  avg_delivery_days,
  avg_order_value,
  avg_payment_value,
  ROUND(100.0 * delivered_orders / NULLIF(total_orders, 0), 1) AS delivery_success_rate,
  ROUND(total_revenue / NULLIF(total_customers, 0), 2) AS revenue_per_customer
FROM kpis;
