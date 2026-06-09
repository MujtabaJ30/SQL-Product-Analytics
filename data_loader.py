import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = r'C:\Users\Mujtaba Jafri\Downloads\Product resume Project\Olist SQL\olist.db'


@st.cache_resource
def get_connection():
    return sqlite3.connect(DB_PATH)


@st.cache_data(ttl=600)
def load_kpis():
    query = """
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
             WHERE o.order_status NOT IN ('canceled', 'unavailable')) AS avg_order_value
    """
    conn = get_connection()
    return pd.read_sql(query, conn)


@st.cache_data(ttl=600)
def load_monthly_revenue():
    query = """
        SELECT STRFTIME('%Y-%m', o.order_purchase_timestamp) AS year_month,
               ROUND(SUM(oi.price), 2) AS revenue,
               COUNT(DISTINCT o.order_id) AS order_count
        FROM olist_orders_dataset o
        INNER JOIN olist_order_items_dataset oi ON o.order_id = oi.order_id
        WHERE o.order_status NOT IN ('canceled', 'unavailable')
        GROUP BY year_month ORDER BY year_month
    """
    conn = get_connection()
    df = pd.read_sql(query, conn)
    df['year_month_dt'] = pd.to_datetime(df['year_month'] + '-01')
    return df


@st.cache_data(ttl=600)
def load_categories():
    query = """
        SELECT COALESCE(t.product_category_name_english, p.product_category_name) AS category,
               ROUND(SUM(oi.price), 2) AS revenue,
               COUNT(DISTINCT oi.order_id) AS order_count,
               ROUND(AVG(r.review_score), 2) AS avg_score,
               ROUND(AVG(oi.price), 2) AS avg_price
        FROM olist_order_items_dataset oi
        INNER JOIN olist_products_dataset p ON oi.product_id = p.product_id
        LEFT JOIN product_category_name_translation t ON p.product_category_name = t.product_category_name
        INNER JOIN olist_orders_dataset o ON oi.order_id = o.order_id
        LEFT JOIN olist_order_reviews_dataset r ON oi.order_id = r.order_id
        WHERE o.order_status NOT IN ('canceled', 'unavailable') AND p.product_category_name IS NOT NULL
        GROUP BY category ORDER BY revenue DESC
    """
    conn = get_connection()
    return pd.read_sql(query, conn)


@st.cache_data(ttl=600)
def load_states():
    query = """
        SELECT c.customer_state AS state, COUNT(DISTINCT o.order_id) AS orders,
               ROUND(SUM(oi.price), 2) AS revenue,
               ROUND(AVG(oi.price), 2) AS avg_order_value
        FROM olist_orders_dataset o
        INNER JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
        INNER JOIN olist_order_items_dataset oi ON o.order_id = oi.order_id
        WHERE o.order_status NOT IN ('canceled', 'unavailable')
        GROUP BY state ORDER BY orders DESC
    """
    conn = get_connection()
    return pd.read_sql(query, conn)


@st.cache_data(ttl=600)
def load_rfm():
    query = """
        WITH rfm AS (
            SELECT c.customer_unique_id,
                   ROUND(JULIANDAY('2018-10-17') - JULIANDAY(MAX(o.order_purchase_timestamp)), 1) AS recency,
                   COUNT(DISTINCT o.order_id) AS frequency,
                   ROUND(SUM(oi.price) + SUM(oi.freight_value), 2) AS monetary
            FROM olist_customers_dataset c
            INNER JOIN olist_orders_dataset o ON c.customer_id = o.customer_id
            INNER JOIN olist_order_items_dataset oi ON o.order_id = oi.order_id
            WHERE o.order_status NOT IN ('canceled', 'unavailable')
            GROUP BY c.customer_unique_id
        ), scores AS (
            SELECT *, NTILE(4) OVER (ORDER BY recency DESC) AS r_score,
                      NTILE(4) OVER (ORDER BY frequency ASC) AS f_score,
                      NTILE(4) OVER (ORDER BY monetary ASC) AS m_score
            FROM rfm
        )
        SELECT CASE WHEN (r_score + f_score + m_score) >= 10 THEN 'High-Value'
                    WHEN (r_score + f_score + m_score) BETWEEN 7 AND 9 THEN 'Loyal'
                    WHEN (r_score + f_score + m_score) BETWEEN 5 AND 6 THEN 'At-Risk'
                    ELSE 'Lost' END AS segment,
               COUNT(*) AS customers, ROUND(SUM(monetary), 2) AS total_value,
               ROUND(AVG(monetary), 2) AS avg_value
        FROM scores GROUP BY segment
    """
    conn = get_connection()
    return pd.read_sql(query, conn)


@st.cache_data(ttl=600)
def load_delivery_review():
    query = """
        SELECT CASE
                    WHEN o.order_delivered_customer_date <= o.order_estimated_delivery_date THEN 'On-Time'
                    ELSE 'Late' END AS delivery_status,
               ROUND(AVG(r.review_score), 2) AS avg_score,
               COUNT(*) AS orders
        FROM olist_orders_dataset o
        INNER JOIN olist_order_reviews_dataset r ON o.order_id = r.order_id
        WHERE o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL
        GROUP BY delivery_status
    """
    conn = get_connection()
    return pd.read_sql(query, conn)


@st.cache_data(ttl=600)
def load_payments():
    query = """
        SELECT payment_type, COUNT(*) AS cnt,
               ROUND(SUM(payment_value), 2) AS total,
               ROUND(AVG(payment_value), 2) AS avg_value
        FROM olist_order_payments_dataset
        GROUP BY payment_type ORDER BY cnt DESC
    """
    conn = get_connection()
    return pd.read_sql(query, conn)


@st.cache_data(ttl=600)
def load_late_categories():
    query = """
        SELECT COALESCE(t.product_category_name_english, p.product_category_name) AS category,
               ROUND(100.0 * SUM(CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1 ELSE 0 END) / COUNT(*), 1) AS late_pct,
               COUNT(*) AS total_orders
        FROM olist_orders_dataset o
        INNER JOIN olist_order_items_dataset oi ON o.order_id = oi.order_id
        INNER JOIN olist_products_dataset p ON oi.product_id = p.product_id
        LEFT JOIN product_category_name_translation t ON p.product_category_name = t.product_category_name
        WHERE o.order_status = 'delivered' AND p.product_category_name IS NOT NULL
        GROUP BY category HAVING COUNT(*) > 100
        ORDER BY late_pct DESC LIMIT 10
    """
    conn = get_connection()
    return pd.read_sql(query, conn)


@st.cache_data(ttl=600)
def load_funnel():
    query = """
        SELECT order_status, COUNT(*) AS order_count
        FROM olist_orders_dataset
        GROUP BY order_status ORDER BY order_count DESC
    """
    conn = get_connection()
    return pd.read_sql(query, conn)


@st.cache_data(ttl=600)
def load_delay_severity():
    query = """
        SELECT CASE
                    WHEN JULIANDAY(order_delivered_customer_date) - JULIANDAY(order_estimated_delivery_date) <= 0 THEN 'On-Time'
                    WHEN JULIANDAY(order_delivered_customer_date) - JULIANDAY(order_estimated_delivery_date) <= 3 THEN '1-3 Days Late'
                    WHEN JULIANDAY(order_delivered_customer_date) - JULIANDAY(order_estimated_delivery_date) <= 7 THEN '4-7 Days Late'
                    ELSE '7+ Days Late' END AS delay_bucket,
               COUNT(*) AS orders
        FROM olist_orders_dataset
        WHERE order_status = 'delivered' AND order_delivered_customer_date IS NOT NULL
        GROUP BY delay_bucket
        ORDER BY CASE delay_bucket
                    WHEN 'On-Time' THEN 1 WHEN '1-3 Days Late' THEN 2
                    WHEN '4-7 Days Late' THEN 3 ELSE 4 END
    """
    conn = get_connection()
    return pd.read_sql(query, conn)


@st.cache_data(ttl=600)
def load_installments():
    query = """
        SELECT payment_installments, COUNT(*) AS cnt
        FROM olist_order_payments_dataset
        WHERE payment_installments BETWEEN 1 AND 12
        GROUP BY payment_installments ORDER BY payment_installments
    """
    conn = get_connection()
    return pd.read_sql(query, conn)
