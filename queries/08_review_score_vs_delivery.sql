-- Review Score vs Delivery Time Correlation
-- Purpose: Does late delivery cause lower review scores? Quantify the impact.
-- Business Question: How much does a delayed delivery affect customer satisfaction?
-- Product Insight: If late delivery drops scores by >1 point, it's a retention risk that costs more than fixing logistics.
-- An interviewer might ask: "Is this causation or correlation? How would you isolate the effect?"
-- Interview answer: "Correlation, not causation. Late deliveries may correlate with other factors like seller quality or product category.
--   An A/B test with delivery estimate messaging would isolate the effect."

WITH delivery_review AS (
  SELECT
    o.order_id,
    r.review_score,
    JULIANDAY(o.order_delivered_customer_date) - JULIANDAY(o.order_purchase_timestamp) AS actual_delivery_days,
    JULIANDAY(o.order_estimated_delivery_date) - JULIANDAY(o.order_purchase_timestamp) AS estimated_days,
    CASE
      WHEN o.order_delivered_customer_date <= o.order_estimated_delivery_date THEN 'on_time'
      ELSE 'late'
    END AS delivery_status,
    CASE
      WHEN o.order_delivered_customer_date IS NULL THEN 'not_delivered'
      WHEN JULIANDAY(o.order_delivered_customer_date) - JULIANDAY(o.order_estimated_delivery_date) <= 0 THEN 'on_time'
      WHEN JULIANDAY(o.order_delivered_customer_date) - JULIANDAY(o.order_estimated_delivery_date) <= 3 THEN 'late_1_3_days'
      WHEN JULIANDAY(o.order_delivered_customer_date) - JULIANDAY(o.order_estimated_delivery_date) <= 7 THEN 'late_4_7_days'
      ELSE 'late_7_plus_days'
    END AS delay_severity
  FROM olist_orders_dataset o
  INNER JOIN olist_order_reviews_dataset r ON o.order_id = r.order_id
  WHERE o.order_status = 'delivered'
)

-- Average review score by delivery status
SELECT
  delivery_status,
  COUNT(*) AS orders,
  ROUND(AVG(review_score), 2) AS avg_review_score,
  ROUND(AVG(actual_delivery_days), 1) AS avg_delivery_days
FROM delivery_review
GROUP BY delivery_status;

-- Finer breakdown: score by delay severity
SELECT
  delay_severity,
  COUNT(*) AS orders,
  ROUND(AVG(review_score), 2) AS avg_review_score,
  ROUND(100.0 * SUM(CASE WHEN review_score <= 2 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_negative_reviews
FROM delivery_review
GROUP BY delay_severity
ORDER BY
  CASE delay_severity
    WHEN 'on_time' THEN 1
    WHEN 'late_1_3_days' THEN 2
    WHEN 'late_4_7_days' THEN 3
    WHEN 'late_7_plus_days' THEN 4
    WHEN 'not_delivered' THEN 5
  END;

-- Score distribution: on-time vs late
SELECT
  review_score,
  SUM(CASE WHEN delivery_status = 'on_time' THEN 1 ELSE 0 END) AS on_time_orders,
  SUM(CASE WHEN delivery_status = 'late' THEN 1 ELSE 0 END) AS late_orders
FROM delivery_review
GROUP BY review_score
ORDER BY review_score DESC;
