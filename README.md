# Olist E-Commerce SQL Product Analytics

**10 SQL queries analyzing 100K Brazilian e-commerce orders — from funnel conversion to customer segmentation.**

## Why Olist?

The Olist dataset is publicly available on Kaggle and contains **100K orders** from 2016–2018 across multiple Brazilian marketplaces. It was chosen because:

- **E-commerce domain** — directly relevant to marketplace/retail product roles
- **9 relational tables** — mimics real-world data complexity (orders, customers, products, payments, reviews, sellers, geolocation)
- **Rich business questions** — delivery performance, customer satisfaction, revenue trends, regional behavior — all common interview topics
- **Clean, documented schema** — allows focus on **product thinking** rather than data cleaning

## Techniques Used

`SELECT` | `WHERE` | `GROUP BY` | `HAVING` | `ORDER BY` | `INNER JOIN` | `LEFT JOIN` | `Subqueries` | `CTEs (WITH)` | `Window Functions (LAG, NTILE, COUNT OVER)` | `CASE` | `Date Functions (STRFTIME, JULIANDAY)` | `COALESCE` | `NULLIF` | `Aggregations (SUM, AVG, COUNT)`

## Entity Relationship Diagram (ERD)

```
┌─────────────────────┐       ┌──────────────────────┐
│  olist_customers    │       │   olist_orders       │
│─────────────────────│       │──────────────────────│
│ PK: customer_id     │◄──────│ FK: customer_id      │
│ customer_unique_id  │       │ order_id (PK)        │
│ customer_zip_code   │       │ order_status         │
│ customer_city       │       │ purchase_timestamp   │
│ customer_state      │       │ approved_at          │
└─────────────────────┘       │ delivered_carrier    │
                              │ delivered_customer   │
                              │ estimated_delivery   │
                              └──────────┬───────────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
         ┌──────────▼────────┐  ┌────────▼────────┐  ┌───────▼──────────────┐
         │ olist_order_items │  │ olist_payments  │  │ olist_order_reviews  │
         │───────────────────│  │─────────────────│  │──────────────────────│
         │ FK: order_id      │  │ FK: order_id    │  │ FK: order_id         │
         │ FK: product_id    │  │ payment_type    │  │ review_score         │
         │ FK: seller_id     │  │ installments    │  │ review_comment       │
         │ price             │  │ payment_value   │  │ creation_date        │
         │ freight_value     │  └─────────────────┘  └──────────────────────┘
         └──────────┬────────┘
                    │                    ┌──────────────────────────┐
         ┌──────────▼────────┐           │  olist_sellers           │
         │ olist_products    │           │──────────────────────────│
         │───────────────────│           │ PK: seller_id            │
         │ PK: product_id    │           │ seller_zip_code          │
         │ category_name ────┼────┐      │ seller_city, state       │
         │ weight, dims     │    │      └──────────────────────────┘
         └──────────────────┘    │
                    ┌────────────▼───────────┐
                    │ category_translation   │
                    │────────────────────────│
                    │ product_category_name  │
                    │ english_name           │
                    └────────────────────────┘

┌─────────────────────────────────────┐
│  olist_geolocation                  │
│─────────────────────────────────────│
│ geolocation_zip_code_prefix         │
│ lat, lng, city, state               │
│ (mapped to customer/seller zip)     │
└─────────────────────────────────────┘
```

### Core Relationships

| Relationship | Type | Key |
|---|---|---|
| customers → orders | One-to-Many | `customer_id` |
| orders → order_items | One-to-Many | `order_id` |
| order_items → products | Many-to-One | `product_id` |
| order_items → sellers | Many-to-One | `seller_id` |
| orders → payments | One-to-Many | `order_id` |
| orders → reviews | One-to-One | `order_id` |
| products → category_translation | Many-to-One | `product_category_name` |
| customers → geolocation | Many-to-One | `customer_zip_code_prefix` |

---

## Query Catalog

### 1. Schema Exploration
- **Business Question:** What data do we have? How are tables structured?
- **Output:** Row counts, column types, time range, unique customers, order status distribution
- **Techniques:** `UNION ALL`, `PRAGMA table_info`, `CASE`

### 2. Order Funnel
- **Business Question:** At which stage do we lose most orders?
- **Key Finding:** 97% of non-canceled orders are delivered. Main drop-off is between "invoiced" → "shipping" (carrier handover).
- **Techniques:** `CASE`, `GROUP BY`, `COUNT OVER` window for percentages

### 3. Monthly Revenue Trend
- **Business Question:** Is the platform growing month-over-month? Which are the peak months?
- **Key Finding:** Revenue grew from ~$45K in Oct 2016 to $1.3M+ by Aug 2018. Nov-Mar (Brazil summer) are peak months.
- **Techniques:** `STRFTIME`, `LAG` window function for MoM growth calculation

![Monthly Revenue Trend](visuals/01_monthly_revenue.png)

### 4. Category Performance
- **Business Question:** Which product categories drive the most revenue and satisfaction?
- **Key Finding:** Top categories: health_beauty, watches_gifts, bed_bath_table. Some high-revenue categories have below-average review scores — quality opportunity.
- **Techniques:** `INNER JOIN` across 4 tables, aggregation, `COALESCE` for null handling

![Top Categories by Revenue](visuals/04_top_categories.png)

### 5. Customer Geography
- **Business Question:** Which states and cities are our strongest markets?
- **Key Finding:** São Paulo (SP) dominates — 40%+ of orders. Rio de Janeiro (RJ) is second at ~13%. Significant geographic concentration risk.
- **Techniques:** `GROUP BY`, `ORDER BY`, percentage of total using window function

![Orders by State](visuals/06_orders_by_state.png)

### 6. Payment Analysis
- **Business Question:** How do customers pay? What's the preferred method and installment pattern?
- **Key Finding:** Credit cards dominate (74%). 25%+ of transactions use installments of 4+. Boleto is second at ~18%.
- **Techniques:** `GROUP BY`, percentage calculation, `HAVING` for multi-payment detection

![Payment Methods](visuals/05_payment_methods.png)

### 7. Delivery Performance
- **Business Question:** How reliable is delivery estimation? Which categories have worst delays?
- **Key Finding:** 8.1% of deliveries arrive late. Furniture/home categories have highest late rates (13-17%).
- **Techniques:** `JULIANDAY` for date difference, `CASE` for late flag, aggregation by category

![Late Delivery by Category](visuals/07_late_delivery_by_category.png)

### 8. Review Score vs Delivery Time
- **Business Question:** Does late delivery cause lower review scores? How much impact?
- **Key Finding:** On-time deliveries average 4.29 stars. Late deliveries drop to 2.57 stars — a **1.72 point penalty**. This is a massive impact on customer satisfaction.
- **Techniques:** `JULIANDAY`, `CASE` for delay severity buckets, aggregation

![Review Score vs Delivery](visuals/02_review_vs_delivery.png)

### 9. Customer Segmentation (RFM)
- **Business Question:** Which customers are high-value, at-risk, or lost? Where should we invest retention?
- **Key Finding:** High-value customers (25% of base) drive 48% of revenue. At-risk segment (25%) represents ~$1.5M in recoverable value.
- **Techniques:** `CTEs`, `NTILE(4)` window function, `CASE` for segment labels, multi-stage transformation

![RFM Segmentation](visuals/03_rfm_segmentation.png)

### 10. Executive Summary
- **Business Question:** "How is the business doing?" — single-query health dashboard
- **Key Finding:** Returns 8+ KPIs in one row: total customers, orders, delivered rate, revenue, avg review score, avg delivery time, avg order value, revenue per customer
- **Techniques:** Scalar subqueries, `COALESCE`, `NULLIF` for safe division

---

## Top 3 Product Recommendations

### 1. Fix Delivery Estimation for High-Late Categories
**Insight:** Furniture/home categories have 13-17% late delivery rates. Review scores drop by **1.72 points** (4.29 → 2.57) when deliveries are late.
**Recommendation:** Adjust estimated delivery dates by category — more conservative for furniture, tighter for health/beauty. This alone could improve avg review score by 0.3-0.5 points.

### 2. Focus Retention on At-Risk High-Value Customers
**Insight:** 25% of customers are "at-risk" (declining engagement) and represent ~$1.5M in recoverable annual value.
**Recommendation:** Launch a reactivation campaign targeting at-risk customers who previously spent >$200 with personalized offers and delivery guarantees.

### 3. Prioritize Checkout for Credit Card + Installment UX
**Insight:** 74% of payments are credit card, and 25%+ use 4+ installments. The current checkout likely treats these as equal.
**Recommendation:** Optimize the checkout flow to default to credit card, surface installment options prominently, and simplify boleto (18% of transactions) as an alternative. This could reduce checkout abandonment by streamlining the most common path.

---

## How to Run

### Interactive Dashboard (Streamlit)
```bash
# 1. Create virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the dashboard
streamlit run app.py
```
Opens at `http://localhost:8501` — 4 tabs (Revenue, Customers, Delivery, Payments) with live KPI cards and filterable Plotly charts. The database auto-decompresses from `olist.db.gz` on first run.

### DB Browser for SQLite
1. Download [DB Browser for SQLite](https://sqlitebrowser.org/dl/)
2. Open `olist.db` (auto-created on first dashboard run, or download CSVs from Kaggle)
3. Open any `.sql` file from `queries/` and execute

### Command Line (SQLite3)
```bash
sqlite3 olist.db < queries/01_schema_exploration.sql
```

### Batch Runner (all 10 queries at once)
```bash
python run_all_queries.py
```

---

## Deploy to Streamlit Cloud

1. Fork/push this repo to GitHub (the compressed `olist.db.gz` is already included)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → select this repo → set **Main file path** to `app.py`
4. Click **Deploy** — the app auto-decompresses the database on first run

No API keys, no external DB, no paid services. Works on Streamlit Cloud's free tier.

### Live Dashboard
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://olist-analytics.streamlit.app)
*(Replace URL with your deployed app link after Streamlit Cloud deployment)*

---

## Insights at a Glance

| Metric | Value |
|---|---|
| Total Customers | 96,096 unique |
| Total Orders | ~99K |
| Delivery Success Rate | 97% |
| Avg Review Score | 4.09 / 5 |
| Avg Delivery Time | ~12 days |
| Avg Order Value | ~$120 |
| Top State | São Paulo (SP) — 40%+ |
| Top Payment | Credit Card — 74% |
| Late Delivery Penalty | 1.72 star drop (4.29 → 2.57) |
| High-Value Customers | 25% drive 48% of revenue |

---

*Built as part of a Product Management portfolio. For questions: reach out via [LinkedIn](https://www.linkedin.com/in/mujtaba30/)*
