# Project: Olist E-Commerce SQL Product Analytics

## Dataset Source
This dataset is publicly available on Kaggle: [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

It contains 100K orders from 2016–2018 made at Olist Store, the largest department store in Brazilian marketplaces.

## Tables (9 total)

| Table | Rows | Description |
|---|---|---|
| `olist_orders_dataset` | 99,441 | Order-level data: status, timestamps throughout the delivery lifecycle |
| `olist_customers_dataset` | 99,441 | Customer info: unique ID, zip code, city, state |
| `olist_order_items_dataset` | 112,650 | Item-level data: product, seller, price, freight per order item |
| `olist_products_dataset` | 32,951 | Product attributes: category, weight, dimensions, photo count |
| `olist_order_payments_dataset` | 103,886 | Payment info: type, installments, value per order |
| `olist_order_reviews_dataset` | 99,224 | Customer reviews: score (1-5), comments, timestamps |
| `olist_sellers_dataset` | 3,095 | Seller info: ID, zip code, city, state |
| `product_category_name_translation` | 71 | Maps Portuguese category names to English |
| `olist_geolocation_dataset` | 1,000,163 | Brazilian zip code to lat/lng coordinates |

## Key Relationships
- **orders → customers:** Many-to-One via `customer_id`
- **orders → order_items:** One-to-Many via `order_id`
- **order_items → products:** Many-to-One via `product_id`
- **order_items → sellers:** Many-to-One via `seller_id`
- **orders → payments:** One-to-Many via `order_id`
- **orders → reviews:** One-to-One via `order_id`
- **products → category_translation:** Many-to-One via `product_category_name`
- **customers/geolocation:** via `customer_zip_code_prefix`

## Column Details

### olist_orders_dataset
| Column | Type | Description |
|---|---|---|
| order_id | TEXT (PK) | Unique order identifier |
| customer_id | TEXT (FK) | References olist_customers_dataset |
| order_status | TEXT | delivered, shipped, canceled, unavailable, invoiced, processing, created, approved |
| order_purchase_timestamp | DATETIME | When order was placed |
| order_approved_at | DATETIME | When payment was approved |
| order_delivered_carrier_date | DATETIME | When handed to logistics carrier |
| order_delivered_customer_date | DATETIME | When customer received the order |
| order_estimated_delivery_date | DATETIME | Estimated delivery date set at purchase |

### olist_customers_dataset
| Column | Type | Description |
|---|---|---|
| customer_id | TEXT (PK) | Unique customer identifier |
| customer_unique_id | TEXT | Unique across customers (for deduplication) |
| customer_zip_code_prefix | INT | First 5 digits of zip code |
| customer_city | TEXT | City name |
| customer_state | TEXT | State abbreviation (e.g., SP, RJ, MG) |

### olist_order_items_dataset
| Column | Type | Description |
|---|---|---|
| order_id | TEXT (FK) | References olist_orders_dataset |
| order_item_id | INT | Item sequence within order (starts at 1) |
| product_id | TEXT (FK) | References olist_products_dataset |
| seller_id | TEXT (FK) | References olist_sellers_dataset |
| shipping_limit_date | DATETIME | Seller must ship by this date |
| price | REAL | Item price |
| freight_value | REAL | Shipping cost |

### olist_products_dataset
| Column | Type | Description |
|---|---|---|
| product_id | TEXT (PK) | Unique product identifier |
| product_category_name | TEXT | Portuguese category name (nullable) |
| product_name_lenght | INT | Character count of product name |
| product_description_lenght | INT | Character count of product description |
| product_photos_qty | INT | Number of product photos |
| product_weight_g | INT | Weight in grams |
| product_length_cm | INT | Length in cm |
| product_height_cm | INT | Height in cm |
| product_width_cm | INT | Width in cm |

### olist_order_payments_dataset
| Column | Type | Description |
|---|---|---|
| order_id | TEXT (FK) | References olist_orders_dataset |
| payment_sequential | INT | Sequence of payment methods used for this order |
| payment_type | TEXT | credit_card, boleto, voucher, debit_card, not_defined |
| payment_installments | INT | Number of installments (0 = upfront, 1+ = installments) |
| payment_value | REAL | Transaction value |

### olist_order_reviews_dataset
| Column | Type | Description |
|---|---|---|
| review_id | TEXT (PK) | Unique review identifier |
| order_id | TEXT (FK) | References olist_orders_dataset |
| review_score | INT | 1-5 rating |
| review_comment_title | TEXT | Short title (often empty) |
| review_comment_message | TEXT | Full review text (often empty — only 41% filled) |
| review_creation_date | DATETIME | When review was submitted |
| review_answer_timestamp | DATETIME | When seller responded (if applicable) |

### olist_sellers_dataset
| Column | Type | Description |
|---|---|---|
| seller_id | TEXT (PK) | Unique seller identifier |
| seller_zip_code_prefix | INT | First 5 digits of zip code |
| seller_city | TEXT | City name |
| seller_state | TEXT | State abbreviation |

### product_category_name_translation
| Column | Type | Description |
|---|---|---|
| product_category_name | TEXT (PK) | Portuguese category name |
| product_category_name_english | TEXT | English translation |

### olist_geolocation_dataset
| Column | Type | Description |
|---|---|---|
| geolocation_zip_code_prefix | INT | First 5 digits of zip code (join key) |
| geolocation_lat | REAL | Latitude |
| geolocation_lng | REAL | Longitude |
| geolocation_city | TEXT | City name |
| geolocation_state | TEXT | State abbreviation |
