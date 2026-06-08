-- Category Performance Analysis
-- Purpose: Find top-performing product categories by revenue, review score, and volume.
-- Business Question: Which categories drive the most revenue? Which have the best customer satisfaction?
-- Product Insight: A category with high revenue but low reviews may need quality improvements.
-- A category with great reviews but low revenue may need better visibility/marketing.

SELECT
  COALESCE(t.product_category_name_english, p.product_category_name) AS category,
  COUNT(DISTINCT oi.order_id) AS order_count,
  ROUND(SUM(oi.price), 2) AS total_revenue,
  ROUND(AVG(oi.price), 2) AS avg_price,
  ROUND(AVG(r.review_score), 2) AS avg_review_score,
  ROUND(AVG(oi.freight_value), 2) AS avg_freight,
  ROUND(SUM(oi.price) / COUNT(DISTINCT oi.order_id), 2) AS revenue_per_order
FROM olist_order_items_dataset oi
INNER JOIN olist_products_dataset p ON oi.product_id = p.product_id
LEFT JOIN product_category_name_translation t ON p.product_category_name = t.product_category_name
INNER JOIN olist_orders_dataset o ON oi.order_id = o.order_id
LEFT JOIN olist_order_reviews_dataset r ON oi.order_id = r.order_id
WHERE o.order_status NOT IN ('canceled', 'unavailable')
  AND p.product_category_name IS NOT NULL
GROUP BY category
ORDER BY total_revenue DESC
LIMIT 15;
