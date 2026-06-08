-- Customer Segmentation using RFM Analysis
-- Purpose: Segment customers into high-value, at-risk, lost, and new segments based on their purchase behavior.
-- Business Question: Which customers should we invest in retaining? Who is likely to churn?
-- Product Insight: RFM (Recency, Frequency, Monetary) is a classic marketing segmentation framework.
-- The top 20% of customers by value often drive 80% of revenue. Identifying at-risk whales prevents revenue loss.
-- An interviewer might ask: "Why NTILE(4) instead of NTILE(5)? Why not use k-means?"
-- Interview answer: "NTILE(4) gives quartiles — simple, interpretable, no library needed.
--   K-means would be more precise but harder to explain to stakeholders. For a portfolio project, quartiles strike the right balance."

WITH customer_rfm AS (
  SELECT
    c.customer_unique_id,
    -- Recency: days since last purchase (lower = more recent)
    ROUND(JULIANDAY('2018-10-17') - JULIANDAY(MAX(o.order_purchase_timestamp)), 1) AS recency,
    -- Frequency: total orders
    COUNT(DISTINCT o.order_id) AS frequency,
    -- Monetary: total spend
    ROUND(SUM(oi.price) + SUM(oi.freight_value), 2) AS monetary
  FROM olist_customers_dataset c
  INNER JOIN olist_orders_dataset o ON c.customer_id = o.customer_id
  INNER JOIN olist_order_items_dataset oi ON o.order_id = oi.order_id
  WHERE o.order_status NOT IN ('canceled', 'unavailable')
  GROUP BY c.customer_unique_id
),
rfm_scores AS (
  SELECT
    customer_unique_id,
    recency,
    frequency,
    monetary,
    -- NTILE(4): divide into quartiles. For recency, lower is better so invert the score.
    NTILE(4) OVER (ORDER BY recency DESC) AS recency_score,
    NTILE(4) OVER (ORDER BY frequency ASC) AS frequency_score,
    NTILE(4) OVER (ORDER BY monetary ASC) AS monetary_score
  FROM customer_rfm
),
rfm_combined AS (
  SELECT
    customer_unique_id,
    recency,
    frequency,
    monetary,
    recency_score,
    frequency_score,
    monetary_score,
    (recency_score + frequency_score + monetary_score) AS rfm_total,
    CASE
      WHEN (recency_score + frequency_score + monetary_score) >= 10 THEN 'high_value'
      WHEN (recency_score + frequency_score + monetary_score) BETWEEN 7 AND 9 THEN 'loyal'
      WHEN (recency_score + frequency_score + monetary_score) BETWEEN 5 AND 6 THEN 'at_risk'
      WHEN (recency_score + frequency_score + monetary_score) <= 4 THEN 'lost'
    END AS customer_segment
  FROM rfm_scores
)
SELECT
  customer_segment,
  COUNT(*) AS customer_count,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 1) AS pct_of_customers,
  ROUND(AVG(monetary), 2) AS avg_monetary,
  ROUND(AVG(frequency), 1) AS avg_frequency,
  ROUND(AVG(recency), 1) AS avg_recency_days,
  ROUND(SUM(monetary), 2) AS total_segment_value
FROM rfm_combined
GROUP BY customer_segment
ORDER BY
  CASE customer_segment
    WHEN 'high_value' THEN 1
    WHEN 'loyal' THEN 2
    WHEN 'at_risk' THEN 3
    WHEN 'lost' THEN 4
  END;
