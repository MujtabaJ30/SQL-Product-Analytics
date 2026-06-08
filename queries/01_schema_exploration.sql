-- Schema Exploration: Olist E-Commerce Dataset
-- Purpose: Document all 9 tables, their columns, row counts, and sample data.
-- This serves as a data dictionary — understanding what data we have before analysis.

-- 1. Table overview with row counts
SELECT 'olist_orders_dataset' AS table_name, COUNT(*) AS row_count FROM olist_orders_dataset
UNION ALL
SELECT 'olist_customers_dataset', COUNT(*) FROM olist_customers_dataset
UNION ALL
SELECT 'olist_order_items_dataset', COUNT(*) FROM olist_order_items_dataset
UNION ALL
SELECT 'olist_products_dataset', COUNT(*) FROM olist_products_dataset
UNION ALL
SELECT 'olist_order_payments_dataset', COUNT(*) FROM olist_order_payments_dataset
UNION ALL
SELECT 'olist_order_reviews_dataset', COUNT(*) FROM olist_order_reviews_dataset
UNION ALL
SELECT 'olist_sellers_dataset', COUNT(*) FROM olist_sellers_dataset
UNION ALL
SELECT 'product_category_name_translation', COUNT(*) FROM product_category_name_translation
UNION ALL
SELECT 'olist_geolocation_dataset', COUNT(*) FROM olist_geolocation_dataset;

-- 2. Column details per table (using PRAGMA table_info)
-- Run these individually in DB Browser or use PRAGMA

-- PRAGMA table_info(olist_orders_dataset);
-- PRAGMA table_info(olist_customers_dataset);
-- PRAGMA table_info(olist_order_items_dataset);
-- PRAGMA table_info(olist_products_dataset);
-- PRAGMA table_info(olist_order_payments_dataset);
-- PRAGMA table_info(olist_order_reviews_dataset);
-- PRAGMA table_info(olist_sellers_dataset);
-- PRAGMA table_info(product_category_name_translation);
-- PRAGMA table_info(olist_geolocation_dataset);

-- 3. Time range of data
SELECT
  DATE(MIN(order_purchase_timestamp)) AS first_order_date,
  DATE(MAX(order_purchase_timestamp)) AS last_order_date,
  ROUND((JULIANDAY(MAX(order_purchase_timestamp)) - JULIANDAY(MIN(order_purchase_timestamp))) / 365.0, 1) AS years_of_data
FROM olist_orders_dataset;

-- 4. Unique customers
SELECT COUNT(DISTINCT customer_unique_id) AS unique_customers FROM olist_customers_dataset;

-- 5. Order status distribution
SELECT order_status, COUNT(*) AS order_count, ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 2) AS pct
FROM olist_orders_dataset
GROUP BY order_status
ORDER BY order_count DESC;
