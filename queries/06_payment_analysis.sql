-- Payment Method Analysis
-- Purpose: Understand how customers pay — which methods are preferred, how installments are used.
-- Business Question: Should Olist prioritize certain payment methods? What's the default user preference?
-- Product Insight: Payment method distribution affects checkout UX prioritization. High installment usage suggests price sensitivity.
-- An interviewer might ask: "How would you use this to improve checkout conversion?"

-- 1. Payment method distribution
SELECT
  payment_type,
  COUNT(*) AS usage_count,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 2) AS pct_of_transactions,
  ROUND(AVG(payment_value), 2) AS avg_payment,
  ROUND(AVG(payment_installments), 1) AS avg_installments
FROM olist_order_payments_dataset
GROUP BY payment_type
ORDER BY usage_count DESC;

-- 2. Installment usage — how many installments do customers prefer?
SELECT
  payment_installments,
  COUNT(*) AS usage_count,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 2) AS pct
FROM olist_order_payments_dataset
WHERE payment_installments > 0
GROUP BY payment_installments
ORDER BY payment_installments;

-- 3. Revenue by payment type
SELECT
  p.payment_type,
  ROUND(SUM(p.payment_value), 2) AS total_revenue,
  ROUND(AVG(p.payment_value), 2) AS avg_transaction_value
FROM olist_order_payments_dataset p
GROUP BY p.payment_type
ORDER BY total_revenue DESC;

-- 4. Multi-payment orders (paying in multiple installments across methods)
SELECT
  COUNT(DISTINCT order_id) AS multi_payment_orders,
  ROUND(100.0 * COUNT(DISTINCT order_id) / (SELECT COUNT(DISTINCT order_id) FROM olist_order_payments_dataset), 2) AS pct_of_orders
FROM olist_order_payments_dataset
GROUP BY order_id
HAVING COUNT(payment_sequential) > 1;
