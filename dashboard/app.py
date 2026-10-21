"""
Bluestock Mutual Fund Analytics Platform — Interactive BI Dashboard.

Built with Streamlit, Plotly, and SQLite. Provides wealth managers, financial analysts,
and retail investors with institutional-grade fund screening, historical NAV trend analysis,
CAPM quantitative risk modeling, and demographic cash flow tracking.
"""

import os
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Bluestock MF Analytics Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Institutional CSS Theme
st.markdown("""
<style>
    .main-title {
        font-size: 2.1rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.0rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 14px 18px;
        text-align: center;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #1E3A8A;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)

# Color Palette
NAVY = "#0F172A"
BLUE = "#1E3A8A"
EMERALD = "#10B981"
AMBER = "#F59E0B"


@st.cache_data
def load_warehouse_data():
    """Queries dimensional tables, fact tables, and quantitative scorecards."""
    db_path = 'data/db/bluestock_mf.db'
    if not os.path.exists(db_path):
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    conn = sqlite3.connect(db_path)
    df_nav = pd.read_sql('SELECT * FROM fact_nav', conn)
    df_fund = pd.read_sql('SELECT * FROM dim_fund', conn)
    df_aum = pd.read_sql('SELECT * FROM fact_aum', conn)
    df_trans = pd.read_sql('SELECT * FROM fact_transactions', conn)
    df_perf = pd.read_sql('SELECT * FROM fact_performance', conn)
    conn.close()

    # Load supplementary processed datasets if present
    try:
        df_sip = pd.read_csv('data/raw/monthly_sip.csv')
    except Exception:
        df_sip = pd.DataFrame()

    try:
        df_sc = pd.read_csv('data/processed/fund_scorecard.csv')
    except Exception:
        df_sc = pd.DataFrame()

    return df_nav, df_fund, df_aum, df_trans, df_perf, df_sip, df_sc


df_nav, df_fund, df_aum, df_trans, df_perf, df_sip, df_sc = load_warehouse_data()

# Header Section
st.markdown('<div class="main-title">📈 Bluestock Mutual Fund Analytics Platform</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Enterprise Business Intelligence, Star Schema Warehouse & Quantitative Risk Engine (v1.0)</div>', unsafe_allow_html=True)

# Multi-Tab Layout
tab1, tab2, tab3, tab4 = st.tabs([
    "🏛️ Industry Overview",
    "🔍 Fund Screener & NAV Trend",
    "🎯 Quantitative Risk & Scorecard",
    "👥 Investor Analytics & Cash Flows"
])

# ==================== TAB 1: INDUSTRY OVERVIEW ====================
with tab1:
    st.subheader("Macroeconomic & Asset Management Landscape")
    
    col1, col2, col3, col4 = st.columns(4)
    total_aum = df_aum['aum_lakh_cr'].sum() if not df_aum.empty else 81.2
    
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">₹{total_aum:,.1f}L Cr</div><div class="metric-label">Total Industry AUM</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><div class="metric-value">₹31,002 Cr</div><div class="metric-label">Monthly SIP Inflow</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><div class="metric-value">26.12 Cr</div><div class="metric-label">Total Mutual Fund Folios</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(df_fund)}</div><div class="metric-label">Monitored Schemes</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("##### AUM Trajectory by Asset Management Company (₹ Lakh Crore)")
        if not df_aum.empty:
            fig_aum = px.bar(
                df_aum,
                x='year',
                y='aum_lakh_cr',
                color='amc',
                barmode='group',
                color_discrete_sequence=px.colors.qualitative.Prism,
                labels={'aum_lakh_cr': 'AUM (₹ Lakh Cr)', 'year': 'Year'}
            )
            fig_aum.update_layout(height=380, margin=dict(l=20, r=20, t=30, b=20), legend=dict(orientation="h", y=-0.2))
            st.plotly_chart(fig_aum, use_container_width=True)

    with c2:
        st.markdown("##### Monthly National SIP Inflow Momentum (₹ Crore)")
        if not df_sip.empty:
            fig_sip = px.line(
                df_sip,
                x='month',
                y='sip_amount_cr',
                markers=True,
                color_discrete_sequence=[EMERALD],
                labels={'sip_amount_cr': 'Inflows (₹ Cr)', 'month': 'Timeline'}
            )
            fig_sip.update_layout(height=380, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_sip, use_container_width=True)


# ==================== TAB 2: FUND SCREENER & NAV TREND ====================
with tab2:
    st.subheader("Scheme Screener & Dynamic Historical NAV Visualizer")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        amc_options = ['All AMCs'] + sorted(list(df_fund['amc'].dropna().unique()))
        selected_amc = st.selectbox("Filter by Fund House (AMC)", amc_options)
    with col_f2:
        cat_options = ['All Categories'] + sorted(list(df_fund['category'].dropna().unique()))
        selected_cat = st.selectbox("Filter by Asset Category", cat_options)

    filtered_df = df_fund.copy()
    if selected_amc != 'All AMCs':
        filtered_df = filtered_df[filtered_df['amc'] == selected_amc]
    if selected_cat != 'All Categories':
        filtered_df = filtered_df[filtered_df['category'] == selected_cat]

    display_df = filtered_df.merge(df_perf, on='amfi_code', how='left')
    cols_to_show = ['amfi_code', 'amc', 'scheme_name', 'category', 'risk_grade', '1y_return', '3y_return', 'expense_ratio']
    
    st.markdown(f"**Displaying {len(display_df)} Matching Schemes:**")
    st.dataframe(
        display_df[[c for c in cols_to_show if c in display_df.columns]],
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    st.markdown("##### Historical NAV Trendline Exploration")
    if not filtered_df.empty and not df_nav.empty:
        scheme_choice = st.selectbox("Select Target Scheme for Historical NAV Graph", filtered_df['scheme_name'].tolist())
        target_code = filtered_df[filtered_df['scheme_name'] == scheme_choice]['amfi_code'].iloc[0]
        fund_nav_df = df_nav[df_nav['amfi_code'] == target_code].sort_values('date_id')
        
        if not fund_nav_df.empty:
            fig_nav = px.area(
                fund_nav_df,
                x='date_id',
                y='nav',
                color_discrete_sequence=[BLUE],
                labels={'nav': 'Net Asset Value (₹)', 'date_id': 'Date'}
            )
            fig_nav.update_layout(height=400, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_nav, use_container_width=True)


# ==================== TAB 3: QUANTITATIVE RISK & SCORECARD ====================
with tab3:
    st.subheader("CAPM Benchmarking & Multi-Factor Scorecard Rankings")
    
    if not df_sc.empty:
        sc_col1, sc_col2 = st.columns([6, 4])
        with sc_col1:
            st.markdown("##### Top Ranked Schemes (5-Factor Weighted Scorecard)")
            st.dataframe(
                df_sc[['scheme_name', 'category', 'overall_cagr', 'sharpe_ratio', 'sortino_ratio', 'alpha_pct', 'beta', 'fund_scorecard']]
                .sort_values('fund_scorecard', ascending=False)
                .head(10),
                use_container_width=True,
                hide_index=True
            )
        with sc_col2:
            st.markdown("##### Scorecard Methodology Weights")
            st.info("""
            **Composite Scorecard Formula (0 - 100):**
            - **30%**: Overall CAGR Percentile Rank
            - **25%**: Annualized Sharpe Ratio Rank (Rf = 6.5%)
            - **20%**: CAPM Annualized Alpha Rank (vs Nifty 50)
            - **15%**: Inverse Expense Ratio Efficiency
            - **10%**: Capital Preservation / Max Drawdown Rank
            """)

        st.markdown("---")
        q1, q2 = st.columns(2)
        with q1:
            st.markdown("##### Risk-Adjusted Efficiency: CAGR vs Sharpe Ratio")
            fig_scatter1 = px.scatter(
                df_sc,
                x='overall_cagr',
                y='sharpe_ratio',
                color='category',
                size='fund_scorecard',
                hover_name='scheme_name',
                labels={'overall_cagr': 'Overall CAGR (%)', 'sharpe_ratio': 'Sharpe Ratio (Rf=6.5%)'},
                color_discrete_map={'Equity': BLUE, 'Debt': EMERALD, 'Hybrid': AMBER}
            )
            fig_scatter1.add_hline(y=1.0, line_dash="dash", line_color="gray")
            fig_scatter1.update_layout(height=380, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_scatter1, use_container_width=True)

        with q2:
            st.markdown("##### CAPM Framework: Systematic Risk (Beta) vs Annualized Alpha")
            fig_scatter2 = px.scatter(
                df_sc,
                x='beta',
                y='alpha_pct',
                color='category',
                hover_name='scheme_name',
                labels={'beta': 'Beta vs Nifty 50', 'alpha_pct': 'Annualized Alpha (%)'},
                color_discrete_map={'Equity': BLUE, 'Debt': EMERALD, 'Hybrid': AMBER}
            )
            fig_scatter2.add_hline(y=0.0, line_dash="dash", line_color="red")
            fig_scatter2.add_vline(x=1.0, line_dash="dot", line_color="black")
            fig_scatter2.update_layout(height=380, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_scatter2, use_container_width=True)
    else:
        st.warning("Scorecard data not available. Please run scripts/run_pipeline.py to compute metrics.")


# ==================== TAB 4: INVESTOR ANALYTICS ====================
with tab4:
    st.subheader("Investor Demographics & Cash Flow Structure")
    
    if not df_trans.empty:
        inv1, inv2 = st.columns(2)
        with inv1:
            st.markdown("##### State-Wise Inflows (₹ Lakhs)")
            state_data = df_trans.groupby('state')['amount'].sum().reset_index()
            state_data['amount_lakhs'] = state_data['amount'] / 100000.0
            state_data = state_data.sort_values('amount_lakhs', ascending=False)
            
            fig_state = px.bar(
                state_data,
                x='state',
                y='amount_lakhs',
                color='amount_lakhs',
                color_continuous_scale='Blues',
                labels={'amount_lakhs': 'Total Inflows (₹ Lakhs)', 'state': 'State Code'}
            )
            fig_state.update_layout(height=380, margin=dict(l=20, r=20, t=20, b=20), coloraxis_showscale=False)
            st.plotly_chart(fig_state, use_container_width=True)

        with inv2:
            st.markdown("##### Inflow Channel Split (SIP vs Lumpsum)")
            type_data = df_trans.groupby('transaction_type')['amount'].sum().reset_index()
            fig_pie = px.pie(
                type_data,
                values='amount',
                names='transaction_type',
                hole=0.45,
                color_discrete_sequence=[BLUE, EMERALD, AMBER]
            )
            fig_pie.update_layout(height=380, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("---")
        kyc_counts = df_trans['kyc_status'].value_counts()
        st.markdown(f"**Investor KYC Verification Audit:** "
                    f"Verified: **{kyc_counts.get('Verified', 0)}** ({kyc_counts.get('Verified', 0)/len(df_trans)*100:.1f}%) | "
                    f"Pending: **{kyc_counts.get('Pending', 0)}** ({kyc_counts.get('Pending', 0)/len(df_trans)*100:.1f}%) | "
                    f"Rejected: **{kyc_counts.get('Rejected', 0)}** ({kyc_counts.get('Rejected', 0)/len(df_trans)*100:.1f}%)")

st.markdown("---")
st.caption("Bluestock Mutual Fund Analytics Capstone | Author: Yuvan Vishnu Pandi | Release: v1.0 Production")
