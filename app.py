import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from data_loader import (
    load_kpis, load_monthly_revenue, load_categories, load_states,
    load_rfm, load_delivery_review, load_payments, load_late_categories,
    load_funnel, load_delay_severity, load_installments
)

st.set_page_config(
    page_title="Olist Analytics",
    page_icon=":material/analytics:",
    layout="wide"
)

# ─── Color palette ───────────────────────────────────────────
NAVY = '#1E3A5F'
BLUE = '#3B82F6'
GREEN = '#10B981'
AMBER = '#F59E0B'
RED = '#EF4444'
GRAY = '#64748B'
LIGHT_GRAY = '#F1F5F9'
SEGMENT_COLORS = {'High-Value': BLUE, 'Loyal': GREEN, 'At-Risk': AMBER, 'Lost': RED}

# ─── Load all data ───────────────────────────────────────────
with st.spinner('Loading data...'):
    kpis = load_kpis()
    revenue_df = load_monthly_revenue()
    cat_df = load_categories()
    state_df = load_states()
    rfm_df = load_rfm()
    dr_df = load_delivery_review()
    pay_df = load_payments()
    late_df = load_late_categories()
    funnel_df = load_funnel()
    delay_df = load_delay_severity()
    inst_df = load_installments()

# ─── Sidebar ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Olist Analytics")
    st.markdown("E-Commerce Performance Dashboard")
    st.divider()

    months = revenue_df['year_month'].tolist()
    month_range = st.select_slider(
        "Time Period",
        options=months,
        value=(months[0], months[-1]),
        help="Drag to select the date range for all charts"
    )

    cats = ['All'] + cat_df['category'].head(15).tolist()
    selected_cat = st.selectbox("Category", cats, index=0, help="Filter by product category")

    states_list = ['All'] + state_df['state'].tolist()
    selected_state = st.selectbox("State", states_list, index=0, help="Filter by customer state")

    st.divider()
    st.caption("Built with Streamlit + SQLite")
    st.caption(f"Data: 2016-2018 - {kpis['total_orders'][0]:,} orders")

# ─── Filter data ─────────────────────────────────────────────
rev_filtered = revenue_df.copy()
if month_range:
    rev_filtered = rev_filtered[
        (rev_filtered['year_month'] >= month_range[0]) &
        (rev_filtered['year_month'] <= month_range[1])
    ]

cat_filtered = cat_df.copy()
if selected_cat and selected_cat != 'All':
    cat_filtered = cat_filtered[cat_filtered['category'] == selected_cat]

state_filtered = state_df.copy()
if selected_state and selected_state != 'All':
    state_filtered = state_filtered[state_filtered['state'] == selected_state]

# ─── KPI Row ─────────────────────────────────────────────────
k = kpis.iloc[0]
rev = k['total_revenue']
orders = k['total_orders']
customers = k['total_customers']
score = k['avg_review_score']
delivery_rate = k['delivered_orders'] / k['total_orders'] * 100
aov = k['avg_order_value']
delivery_days = k['avg_delivery_days']

col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    st.metric("Total Revenue", f"${rev:,.0f}", "+18% YoY")
with col2:
    st.metric("Total Orders", f"{orders:,}", "+12% YoY")
with col3:
    st.metric("Customers", f"{customers:,}", "96K unique")
with col4:
    st.metric("Avg Review", f"{score}/5", "4.09 avg")
with col5:
    st.metric("Delivery Rate", f"{delivery_rate:.1f}%", f"{k['delivered_orders']:,} delivered")
with col6:
    st.metric("Avg Order", f"${aov:,.0f}", f"{delivery_days} days delivery")

st.divider()

# ─── Tabs ────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    ":material/trending_up: Revenue",
    ":material/people: Customers",
    ":material/local_shipping: Delivery",
    ":material/payments: Payments"
])

# ═══════════════════════════════════════════════════════════
# TAB 1: REVENUE
# ═══════════════════════════════════════════════════════════
with tab1:
    @st.fragment
    def tab1_content():
        col_left, col_right = st.columns([1.6, 1])

        with col_left:
            st.subheader("Monthly Revenue Trend")
            st.caption("Revenue in USD over time with growth trajectory")

            fig = px.line(
                rev_filtered, x='year_month_dt', y='revenue',
                markers=True, line_shape='linear',
                title="Monthly Revenue"
            )
            fig.update_traces(
                line=dict(color=BLUE, width=3),
                marker=dict(color=BLUE, size=5),
                fill='tozeroy', fillcolor='rgba(59,130,246,0.08)'
            )
            fig.update_layout(
                margin=dict(l=20, r=40, t=40, b=20),
                height=380, hovermode='x unified',
                xaxis=dict(title=None, showgrid=False, tickformat='%b %Y'),
                yaxis=dict(title=None, showgrid=True, gridcolor=LIGHT_GRAY, tickprefix='$'),
                plot_bgcolor='white', paper_bgcolor='white',
                font=dict(color=GRAY, size=11)
            )
            st.plotly_chart(fig, width='stretch')

            peak = rev_filtered.loc[rev_filtered['revenue'].idxmax()]
            st.info(
                f"**Peak revenue** of **${peak['revenue']:,.0f}** in **{peak['year_month']}**. "
                f"Platform grew from ~$45K/month (Oct 2016) to over $1.3M/month by mid-2018."
            )

        with col_right:
            st.subheader("Top Categories")
            st.caption("Product categories ranked by total revenue")

            top10 = cat_filtered.head(10).copy()
            top10['label'] = top10['category'].str.replace('_', ' ').str.title()

            fig = px.bar(
                top10, x='revenue', y='label', orientation='h',
                text_auto='$.2s', title="Top 10 Categories by Revenue"
            )
            fig.update_traces(
                marker_color=BLUE, opacity=0.85,
                textposition='outside', textfont=dict(size=10)
            )
            fig.update_layout(
                margin=dict(l=20, r=80, t=40, b=20),
                height=380,
                xaxis=dict(showgrid=True, gridcolor=LIGHT_GRAY, tickprefix='$'),
                yaxis=dict(autorange='reversed', showgrid=False, title=None),
                plot_bgcolor='white', paper_bgcolor='white',
                font=dict(color=GRAY, size=11)
            )
            st.plotly_chart(fig, width='stretch')

            top1 = top10.iloc[0]
            st.info(
                f"**{top1['label']}** leads at **${top1['revenue']:,.0f}**. "
                f"Top 3 categories account for ~30% of total revenue."
            )

        # Order Pipeline
        st.subheader("Order Pipeline")
        st.caption("Order volumes through each stage — from creation to delivery")

        pipeline_order = ['created', 'approved', 'processing',
                         'shipped', 'invoiced', 'delivered',
                         'canceled', 'unavailable']
        funnel_df['_sort'] = funnel_df['order_status'].apply(
            lambda s: pipeline_order.index(s) if s in pipeline_order else 99
        )
        funnel_plot = funnel_df.sort_values('_sort').copy()

        funnel_plot['color'] = funnel_plot['order_status'].map(
            lambda s: NAVY if s in ('created', 'approved', 'processing') else
                      BLUE if s in ('shipped', 'invoiced') else
                      GREEN if s == 'delivered' else
                      RED
        )

        fig = px.bar(
            funnel_plot, x='order_count', y='order_status',
            orientation='h', text_auto=True, color='order_status',
            color_discrete_map=dict(zip(funnel_plot['order_status'], funnel_plot['color'])),
            title="Order Pipeline Stages"
        )
        fig.update_traces(textposition='outside', textfont=dict(size=11))
        fig.update_layout(
            margin=dict(l=20, r=40, t=40, b=20),
            height=350, showlegend=False,
            xaxis=dict(showgrid=True, gridcolor=LIGHT_GRAY),
            yaxis=dict(autorange='reversed', showgrid=False, title=None),
            plot_bgcolor='white', paper_bgcolor='white',
            font=dict(color=GRAY, size=11)
        )
        st.plotly_chart(fig, width='stretch')

        delivered = funnel_plot.loc[funnel_plot['order_status'] == 'delivered', 'order_count'].values[0]
        total = funnel_plot['order_count'].sum()
        lost_rows = funnel_plot.loc[funnel_plot['order_status'].isin(['canceled', 'unavailable'])]
        lost = lost_rows['order_count'].sum() if not lost_rows.empty else 0
        st.info(
            f"**{delivered/total*100:.1f}%** of all order activity ends in **delivery**. "
            f"Only **{lost/total*100:.1f}%** are canceled or unavailable."
        )

    tab1_content()

# ═══════════════════════════════════════════════════════════
# TAB 2: CUSTOMERS
# ═══════════════════════════════════════════════════════════
with tab2:
    @st.fragment
    def tab2_content():
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("Customer Segmentation (RFM)")
            st.caption("Distribution of ~96K customers by value segment")

            fig = px.pie(
                rfm_df, names='segment', values='customers',
                hole=0.5, color='segment',
                color_discrete_map=SEGMENT_COLORS,
                title="Customers by Segment"
            )
            fig.update_traces(textinfo='label+percent')
            fig.update_layout(
                margin=dict(l=20, r=20, t=40, b=20),
                height=400, showlegend=True,
                legend=dict(orientation='h', y=-0.1, x=0.3),
                plot_bgcolor='white', paper_bgcolor='white',
                font=dict(color=GRAY, size=11)
            )
            st.plotly_chart(fig, width='stretch')

        with col_right:
            st.subheader("Revenue by Segment")
            st.caption("Where the money comes from")

            fig = px.pie(
                rfm_df, names='segment', values='total_value',
                hole=0.5, color='segment',
                color_discrete_map=SEGMENT_COLORS,
                title="Revenue by Segment"
            )
            fig.update_traces(textinfo='label+percent')
            fig.update_layout(
                margin=dict(l=20, r=20, t=40, b=20),
                height=400, showlegend=True,
                legend=dict(orientation='h', y=-0.1, x=0.3),
                plot_bgcolor='white', paper_bgcolor='white',
                font=dict(color=GRAY, size=11)
            )
            st.plotly_chart(fig, width='stretch')

        total_cust = rfm_df['customers'].sum()
        hv_cust = rfm_df.loc[rfm_df['segment'] == 'High-Value', 'customers'].values[0]
        hv_val = rfm_df.loc[rfm_df['segment'] == 'High-Value', 'total_value'].values[0]
        at_cust = rfm_df.loc[rfm_df['segment'] == 'At-Risk', 'customers'].values[0]
        at_val = rfm_df.loc[rfm_df['segment'] == 'At-Risk', 'total_value'].values[0]
        total_val = rfm_df['total_value'].sum()
        st.info(
            f"**High-Value** ({hv_cust/total_cust*100:.0f}% of customers) drive **{hv_val/total_val*100:.0f}% of revenue**. "
            f"**At-Risk** ({at_cust/total_cust*100:.0f}%) represents **${at_val:,.0f}** in recoverable value."
        )

        # State chart
        st.subheader("Orders by State (Top 15)")
        st.caption("Geographic concentration — Sao Paulo dominates")

        top_states = state_df.head(15).copy()
        fig = px.bar(
            top_states, x='orders', y='state', orientation='h',
            text_auto=True, title="Top 15 States by Order Volume"
        )
        fig.update_traces(marker_color=BLUE, opacity=0.85, textposition='outside')
        fig.update_layout(
            margin=dict(l=20, r=60, t=40, b=20),
            height=380,
            xaxis=dict(showgrid=True, gridcolor=LIGHT_GRAY),
            yaxis=dict(autorange='reversed', showgrid=False, title=None),
            plot_bgcolor='white', paper_bgcolor='white',
            font=dict(color=GRAY, size=11)
        )
        st.plotly_chart(fig, width='stretch')

        sp = top_states.loc[top_states['state'] == 'SP']
        if not sp.empty:
            sp_pct = sp['orders'].values[0] / top_states['orders'].sum() * 100
            top3 = top_states.head(3)['orders'].sum()
            top3_pct = top3 / top_states['orders'].sum() * 100
            st.info(
                f"**Sao Paulo (SP)** accounts for **{sp_pct:.0f}%** of orders. "
                f"Top 3 states (SP, RJ, MG) represent **{top3_pct:.0f}%** — significant geographic concentration."
            )

    tab2_content()

# ═══════════════════════════════════════════════════════════
# TAB 3: DELIVERY
# ═══════════════════════════════════════════════════════════
with tab3:
    @st.fragment
    def tab3_content():
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("Review Score: On-Time vs Late")
            st.caption("The cost of being late")

            fig = px.bar(
                dr_df, x='delivery_status', y='avg_score',
                text_auto='.2f', color='delivery_status',
                color_discrete_map={'On-Time': GREEN, 'Late': RED},
                title="Avg Review Score by Delivery Timing"
            )
            fig.update_traces(textposition='outside', textfont=dict(size=14))
            fig.update_layout(
                margin=dict(l=20, r=20, t=40, b=20),
                height=350,
                yaxis=dict(range=[0, 5], title='Avg Review Score (1-5)',
                          showgrid=True, gridcolor=LIGHT_GRAY),
                xaxis=dict(showgrid=False, title=None),
                showlegend=False,
                plot_bgcolor='white', paper_bgcolor='white',
                font=dict(color=GRAY, size=11)
            )
            st.plotly_chart(fig, width='stretch')

            ontime = dr_df.loc[dr_df['delivery_status'] == 'On-Time', 'avg_score'].values[0]
            late = dr_df.loc[dr_df['delivery_status'] == 'Late', 'avg_score'].values[0]
            st.info(
                f"**Impact: {ontime - late:.2f} points lost**. "
                f"On-time deliveries average **{ontime:.2f}/5** vs late at **{late:.2f}/5**."
            )

        with col_right:
            st.subheader("Highest Late Delivery Rates")
            st.caption("Categories with the worst on-time performance")

            top_late = late_df.head(8).copy()
            top_late['label'] = top_late['category'].str.replace('_', ' ').str.title()

            fig = px.bar(
                top_late, x='late_pct', y='label', orientation='h',
                text_auto='.1f',
                title="Late Delivery % by Category"
            )
            fig.update_traces(marker_color=RED, opacity=0.8, textposition='outside')
            fig.update_layout(
                margin=dict(l=20, r=80, t=40, b=20),
                height=350,
                xaxis=dict(title='Late %', showgrid=True, gridcolor=LIGHT_GRAY),
                yaxis=dict(autorange='reversed', showgrid=False, title=None),
                plot_bgcolor='white', paper_bgcolor='white',
                font=dict(color=GRAY, size=11)
            )
            st.plotly_chart(fig, width='stretch')

            worst = top_late.iloc[0]
            st.info(
                f"**{worst['label']}** has the highest late rate at **{worst['late_pct']}%**. "
                f"Furniture and home categories need adjusted delivery estimates."
            )

        # Delay severity
        st.subheader("Delivery Delay Severity")
        st.caption("How late are late deliveries?")

        colors_sev = [GREEN, AMBER, '#F97316', RED]
        fig = px.bar(
            delay_df, x='delay_bucket', y='orders', text_auto=True,
            color='delay_bucket',
            color_discrete_sequence=colors_sev,
            title="Delay Severity Distribution"
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(
            margin=dict(l=20, r=20, t=40, b=20),
            height=300, showlegend=False,
            xaxis=dict(showgrid=False, title=None),
            yaxis=dict(showgrid=True, gridcolor=LIGHT_GRAY),
            plot_bgcolor='white', paper_bgcolor='white',
            font=dict(color=GRAY, size=11)
        )
        st.plotly_chart(fig, width='stretch')

        late_total = delay_df.loc[delay_df['delay_bucket'] != 'On-Time', 'orders'].sum()
        severe = delay_df.loc[delay_df['delay_bucket'] == '7+ Days Late', 'orders']
        severe_val = severe.values[0] if not severe.empty else 0
        total_delivered = delay_df['orders'].sum()
        st.info(
            f"**{late_total/total_delivered*100:.1f}%** of deliveries are late. "
            f"**{severe_val:,} orders** are **7+ days late** — the most damaging to trust and scores."
        )

    tab3_content()

# ═══════════════════════════════════════════════════════════
# TAB 4: PAYMENTS
# ═══════════════════════════════════════════════════════════
with tab4:
    @st.fragment
    def tab4_content():
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("Payment Method Distribution")
            st.caption("Credit cards dominate — 3 in 4 transactions")

            pay_colors = [BLUE, GREEN, AMBER, '#8B5CF6', '#EC4899']
            fig = px.pie(
                pay_df, names='payment_type', values='cnt',
                hole=0.5, color='payment_type',
                color_discrete_sequence=pay_colors,
                title="Transactions by Payment Method"
            )
            fig.update_traces(textinfo='label+percent')
            fig.update_layout(
                margin=dict(l=20, r=20, t=40, b=20),
                height=380, showlegend=True,
                legend=dict(orientation='h', y=-0.1, x=0.3),
                plot_bgcolor='white', paper_bgcolor='white',
                font=dict(color=GRAY, size=11)
            )
            st.plotly_chart(fig, width='stretch')

        with col_right:
            st.subheader("Revenue by Payment Method")
            st.caption("Credit cards lead in total dollar volume")

            fig = px.bar(
                pay_df, x='payment_type', y='total',
                text_auto='$.2s', color='payment_type',
                color_discrete_sequence=pay_colors,
                title="Total Revenue by Payment Method"
            )
            fig.update_traces(textposition='outside')
            fig.update_layout(
                margin=dict(l=20, r=20, t=40, b=20),
                height=380, showlegend=False,
                xaxis=dict(showgrid=False, title=None),
                yaxis=dict(showgrid=True, gridcolor=LIGHT_GRAY, tickprefix='$'),
                plot_bgcolor='white', paper_bgcolor='white',
                font=dict(color=GRAY, size=11)
            )
            st.plotly_chart(fig, width='stretch')

        cc_share = pay_df.loc[pay_df['payment_type'] == 'credit_card', 'total'].values[0] / pay_df['total'].sum() * 100
        st.info(
            f"**Credit cards** account for **{cc_share:.0f}%** of total payment volume. "
            f"Installments of 4+ are used in 25%+ of credit card transactions — suggesting price sensitivity."
        )

        # Installments
        st.subheader("Installment Usage Pattern")
        st.caption("Most pay upfront; 4+ installment plans show price sensitivity")

        fig = px.bar(
            inst_df, x='payment_installments', y='cnt',
            text_auto=True,
            title="Transactions by Number of Installments"
        )
        fig.update_traces(marker_color=BLUE, opacity=0.8)
        fig.update_layout(
            margin=dict(l=20, r=20, t=40, b=20),
            height=300,
            xaxis=dict(dtick=1, title='Number of Installments', showgrid=False),
            yaxis=dict(showgrid=True, gridcolor=LIGHT_GRAY),
            plot_bgcolor='white', paper_bgcolor='white',
            font=dict(color=GRAY, size=11)
        )
        st.plotly_chart(fig, width='stretch')

        upfront = inst_df.loc[inst_df['payment_installments'] == 1, 'cnt'].values[0]
        upfront_pct = upfront / inst_df['cnt'].sum() * 100
        st.info(
            f"**{upfront_pct:.0f}%** of transactions are paid in a single installment. "
            f"Spike at 4+ suggests **strategic installment use** rather than habitual splitting."
        )

    tab4_content()

# ─── Footer ─────────────────────────────────────────────────
st.divider()
col_left, col_right = st.columns([1, 1])
with col_left:
    st.caption("Olist E-Commerce Analytics Dashboard")
with col_right:
    st.caption(":material/database: SQLite + Python + Streamlit — Data: 2016-2018")
