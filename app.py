"""
ComplianceGuard AI - Real-Time AML Transaction Monitor
Built by Nakul Shriman Karthikeyan | Fintech Analyst
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_generator import generate_transactions
from aml_rules import run_all_rules
from risk_scorer import compute_risk_scores, generate_sar_narrative

# Page config
st.set_page_config(
    page_title="ComplianceGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom dark styling
st.markdown("""
<style>
    .stApp { background-color: #0a0e1a; color: #e8eaed; }
    .main .block-container { padding-top: 2rem; padding-bottom: 1rem; max-width: 1400px; }
    h1, h2, h3 { color: #e8eaed; }
    .stMetric { background-color: #1a1f2e; padding: 1rem; border-radius: 8px; border: 1px solid #2a3142; }
    .stMetric label { color: #8b95a8 !important; }
    div[data-testid="stMetricValue"] { color: #00d9a3 !important; font-size: 1.8rem !important; }
    .stDataFrame { background-color: #1a1f2e; }
    [data-testid="stHeader"] { background-color: rgba(0,0,0,0); }
    .stTabs [data-baseweb="tab-list"] { background-color: #1a1f2e; }
    .stTabs [aria-selected="true"] { background-color: #00d9a3; color: #0a0e1a; }
    .footer { position: fixed; bottom: 0; left: 0; right: 0; background: #0a0e1a; padding: 0.5rem; border-top: 1px solid #2a3142; text-align: center; color: #8b95a8; font-size: 0.85rem; z-index: 999; }
    .footer a { color: #00d9a3; text-decoration: none; margin: 0 0.5rem; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style='padding: 1rem 0; border-bottom: 1px solid #2a3142; margin-bottom: 1.5rem;'>
    <h1 style='margin: 0; color: #00d9a3;'>🛡️ ComplianceGuard AI</h1>
    <p style='margin: 0.25rem 0 0 0; color: #8b95a8; font-size: 1rem;'>
        Real-Time AML Transaction Monitor · Built by Nakul Shriman Karthikeyan | Fintech Analyst
    </p>
</div>
""", unsafe_allow_html=True)


# Cache data generation (slow operation)
@st.cache_data(show_spinner="Generating 100K transactions and running 12 AML rules...")
def load_data():
    transactions, customers = generate_transactions(n_total=50000, fraud_rate=0.025)
    flags = run_all_rules(transactions)
    scored = compute_risk_scores(transactions, flags, customers)
    return transactions, customers, flags, scored


transactions, customers, flags, scored = load_data()

# Filter flagged transactions for main view
flagged = scored[scored['rule_count'] > 0].copy()

# ===========================
# SECTION 1: KPI HERO
# ===========================
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Total Transactions", f"{len(scored):,}")
with col2:
    st.metric("Flagged Transactions", f"{len(flagged):,}",
              delta=f"{len(flagged)/len(scored)*100:.2f}%", delta_color="off")
with col3:
    st.metric("$ At Risk", f"${flagged['amount'].sum()/1e6:.2f}M")
with col4:
    st.metric("Avg Risk Score", f"{flagged['risk_score'].mean():.1f}")
with col5:
    high_risk_count = (flagged['risk_score'] >= 60).sum()
    st.metric("High-Risk Cases", f"{high_risk_count:,}")

st.markdown("<br>", unsafe_allow_html=True)

# ===========================
# Tabs for main sections
# ===========================
tab1, tab2, tab3 = st.tabs(["📋 Transaction Monitoring", "📊 Pattern Analytics", "🔍 Case Investigation"])

# ===========================
# TAB 1: Transaction Monitoring
# ===========================
with tab1:
    st.subheader("Flagged Transactions")

    # Filters
    fcol1, fcol2, fcol3, fcol4 = st.columns(4)
    with fcol1:
        min_severity = st.slider("Min Risk Score", 0, 100, 30)
    with fcol2:
        txn_types = ['All'] + sorted(flagged['txn_type'].unique().tolist())
        sel_type = st.selectbox("Transaction Type", txn_types)
    with fcol3:
        countries = ['All'] + sorted(flagged['receiver_country'].unique().tolist())
        sel_country = st.selectbox("Receiver Country", countries)
    with fcol4:
        min_amount = st.number_input("Min Amount ($)", min_value=0, value=0, step=1000)

    # Apply filters
    filtered = flagged[flagged['risk_score'] >= min_severity].copy()
    if sel_type != 'All':
        filtered = filtered[filtered['txn_type'] == sel_type]
    if sel_country != 'All':
        filtered = filtered[filtered['receiver_country'] == sel_country]
    if min_amount > 0:
        filtered = filtered[filtered['amount'] >= min_amount]

    st.caption(f"Showing {len(filtered):,} flagged transactions")

    # Display table
    display = filtered[['txn_id', 'timestamp', 'customer_name', 'amount',
                        'sender_country', 'receiver_country', 'txn_type',
                        'risk_score', 'risk_tier_label']].copy()
    display['amount'] = display['amount'].apply(lambda x: f"${x:,.2f}")
    display['risk_score'] = display['risk_score'].round(1)
    display = display.sort_values('risk_score', ascending=False).head(200)

    st.dataframe(display, use_container_width=True, height=400, hide_index=True)

    # Expandable details
    st.subheader("Drill Down: Select a Transaction")
    if len(filtered) > 0:
        sel_txn_id = st.selectbox("Transaction ID", filtered.sort_values('risk_score', ascending=False)['txn_id'].head(50).tolist())
        if sel_txn_id:
            txn = filtered[filtered['txn_id'] == sel_txn_id].iloc[0]
            dcol1, dcol2 = st.columns([1, 1])
            with dcol1:
                st.markdown(f"""
                **Transaction:** {txn['txn_id']}
                **Customer:** {txn['customer_name']} ({txn['customer_id']})
                **Amount:** ${txn['amount']:,.2f}
                **Route:** {txn['sender_country']} → {txn['receiver_country']}
                **Type:** {txn['txn_type']} · {txn['merchant_category']}
                **Timestamp:** {txn['timestamp']}
                """)
            with dcol2:
                st.markdown(f"""
                **Risk Score Breakdown:**
                - Rule trigger: {txn['rule_score']:.0f} pts
                - Multi-rule bonus: {txn['multi_rule_bonus']:.0f} pts
                - Amount factor: {txn['amount_score']*0.4:.1f} pts
                - Customer history: {txn['customer_history_score']:.0f} pts
                - Sanctioned: {txn['sanctioned_score']:.0f} pts

                **Total Risk Score: {txn['risk_score']:.1f}/100**
                """)

            # Triggered rules
            txn_flags = flags[flags['txn_id'] == sel_txn_id]
            if len(txn_flags) > 0:
                st.markdown("**Triggered AML Rules:**")
                for _, f in txn_flags.iterrows():
                    severity_color = "🔴" if f['severity'] >= 8 else "🟡" if f['severity'] >= 5 else "🟢"
                    st.markdown(f"{severity_color} **{f['rule']}** (Severity: {f['severity']}/10)")
                    st.caption(f"_{f['explanation']}_")
                    st.caption(f"📜 {f['regulation']}")

# ===========================
# TAB 2: Pattern Analytics
# ===========================
with tab2:
    st.subheader("Pattern Analytics")

    pcol1, pcol2 = st.columns(2)

    with pcol1:
        # Time series of flagged txns
        st.markdown("**Flagged Transactions Over Time**")
        time_series = flagged.copy()
        time_series['hour'] = time_series['timestamp'].dt.floor('h')
        hourly = time_series.groupby('hour').size().reset_index(name='count')
        fig = px.line(hourly, x='hour', y='count', template='plotly_dark')
        fig.update_traces(line_color='#00d9a3', line_width=2)
        fig.update_layout(plot_bgcolor='#0a0e1a', paper_bgcolor='#0a0e1a', height=320,
                          xaxis_title="", yaxis_title="Flagged Count", margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with pcol2:
        # Top countries
        st.markdown("**Top 10 Receiver Countries (Flagged)**")
        country_counts = flagged['receiver_country'].value_counts().head(10).reset_index()
        country_counts.columns = ['country', 'count']
        fig = px.bar(country_counts, x='count', y='country', orientation='h',
                     template='plotly_dark', color='count', color_continuous_scale='YlOrRd')
        fig.update_layout(plot_bgcolor='#0a0e1a', paper_bgcolor='#0a0e1a', height=320,
                          showlegend=False, margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    pcol3, pcol4 = st.columns(2)

    with pcol3:
        # Rule frequency
        st.markdown("**AML Rule Trigger Frequency**")
        if len(flags) > 0:
            rule_counts = flags['rule'].value_counts().reset_index()
            rule_counts.columns = ['rule', 'count']
            fig = px.bar(rule_counts, x='count', y='rule', orientation='h',
                         template='plotly_dark', color='count', color_continuous_scale='Reds')
            fig.update_layout(plot_bgcolor='#0a0e1a', paper_bgcolor='#0a0e1a', height=400,
                              showlegend=False, margin=dict(t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)

    with pcol4:
        # Top risky customers
        st.markdown("**Top 10 Customers by Aggregate Risk**")
        top_customers = flagged.groupby('customer_name').agg(
            txn_count=('txn_id', 'count'),
            total_amount=('amount', 'sum'),
            avg_risk=('risk_score', 'mean'),
        ).sort_values('avg_risk', ascending=False).head(10).reset_index()
        top_customers['total_amount'] = top_customers['total_amount'].apply(lambda x: f"${x:,.0f}")
        top_customers['avg_risk'] = top_customers['avg_risk'].round(1)
        st.dataframe(top_customers, use_container_width=True, height=400, hide_index=True)

# ===========================
# TAB 3: Case Investigation
# ===========================
with tab3:
    st.subheader("Case Investigation & SAR Drafting")
    st.caption("Select a high-risk transaction to generate a draft Suspicious Activity Report (SAR).")

    high_risk_txns = flagged[flagged['risk_score'] >= 60].sort_values('risk_score', ascending=False)
    if len(high_risk_txns) == 0:
        st.warning("No high-risk transactions found.")
    else:
        case_txn_id = st.selectbox(
            "High-Risk Case",
            high_risk_txns['txn_id'].head(30).tolist(),
            format_func=lambda x: f"{x} - {high_risk_txns[high_risk_txns['txn_id']==x]['customer_name'].iloc[0]} - ${high_risk_txns[high_risk_txns['txn_id']==x]['amount'].iloc[0]:,.0f} - Risk: {high_risk_txns[high_risk_txns['txn_id']==x]['risk_score'].iloc[0]:.0f}"
        )
        case_txn = high_risk_txns[high_risk_txns['txn_id'] == case_txn_id].iloc[0]

        # Customer activity (last 30 days)
        related = scored[scored['customer_id'] == case_txn['customer_id']]

        st.markdown(f"### Customer Profile: {case_txn['customer_name']}")
        cc1, cc2, cc3 = st.columns(3)
        with cc1:
            st.metric("Total Transactions", f"{len(related):,}")
        with cc2:
            st.metric("Total Volume", f"${related['amount'].sum():,.0f}")
        with cc3:
            st.metric("Flagged Count", f"{(related['rule_count']>0).sum():,}")

        # Customer transaction history chart
        st.markdown("**Customer Transaction History**")
        cust_history = related.sort_values('timestamp').copy()
        cust_history['color'] = cust_history['risk_score'].apply(
            lambda x: '#ff4757' if x >= 60 else '#ffaa00' if x >= 30 else '#00d9a3'
        )
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=cust_history['timestamp'], y=cust_history['amount'],
            mode='markers',
            marker=dict(color=cust_history['color'], size=10),
            text=cust_history['txn_id'],
            hovertemplate='<b>%{text}</b><br>Amount: $%{y:,.2f}<br>Time: %{x}<extra></extra>',
        ))
        fig.update_layout(template='plotly_dark', plot_bgcolor='#0a0e1a', paper_bgcolor='#0a0e1a',
                          height=300, xaxis_title="", yaxis_title="Amount ($)",
                          margin=dict(t=20, b=20), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        # SAR Narrative
        st.markdown("### 📄 Draft SAR Narrative")
        narrative = generate_sar_narrative(case_txn, related)
        st.text_area("Auto-generated narrative (editable):", narrative, height=400)

        sar_col1, sar_col2 = st.columns([1, 5])
        with sar_col1:
            st.button("📥 Download SAR Draft", type="primary")
        with sar_col2:
            st.caption("In production, this would integrate with FinCEN BSA E-Filing system.")

# Footer
st.markdown("""
<div class='footer'>
    🛡️ ComplianceGuard AI · Built by Nakul Shriman Karthikeyan · 
    <a href='https://linkedin.com/in/shriman-nakul' target='_blank'>LinkedIn</a> · 
    <a href='https://nakul532.github.io' target='_blank'>Portfolio</a>
</div>
""", unsafe_allow_html=True)
