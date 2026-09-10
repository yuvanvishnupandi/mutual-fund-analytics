import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os

st.set_page_config(page_title="MF Analytics Dashboard", page_icon="📈", layout="wide")

# Theme colours: Fintech blue + emerald
BLUE = "#1E3A8A"
EMERALD = "#10B981"

@st.cache_data
def load_data():
    engine = sqlite3.connect('data/db/bluestock_mf.db')
    df_nav = pd.read_sql('SELECT * FROM fact_nav', engine)
    df_fund = pd.read_sql('SELECT * FROM dim_fund', engine)
    df_aum = pd.read_sql('SELECT * FROM fact_aum', engine)
    df_trans = pd.read_sql('SELECT * FROM fact_transactions', engine)
    df_perf = pd.read_sql('SELECT * FROM fact_performance', engine)
    try:
        df_sip = pd.read_csv('data/raw/monthly_sip.csv')
    except:
        df_sip = pd.DataFrame()
    return df_nav, df_fund, df_aum, df_trans, df_perf, df_sip

df_nav, df_fund, df_aum, df_trans, df_perf, df_sip = load_data()

st.title("📊 Bluestock Mutual Fund Analytics Platform")

# Tabs
tab1, tab2, tab3 = st.tabs(["Industry Overview", "Fund Performance", "Investor Analytics"])

with tab1:
    st.header("Industry Overview")
    col1, col2, col3, col4 = st.columns(4)
    total_aum = df_aum['aum_lakh_cr'].sum() if not df_aum.empty else 81.0
    col1.metric("Total AUM", f"₹{total_aum:,.1f}L Cr")
    col2.metric("SIP Inflows (Dec 25)", "₹31,002 Cr")
    col3.metric("Folios", "26.12 Cr")
    col4.metric("Total Schemes", len(df_fund))
    
    st.subheader("AUM Growth by AMC")
    if not df_aum.empty:
        fig = px.bar(df_aum, x='year', y='aum_lakh_cr', color='amc', barmode='group', color_discrete_sequence=px.colors.sequential.Teal)
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("Fund Performance")
    amc_filter = st.selectbox("Select AMC", options=['All'] + list(df_fund['amc'].unique()))
    cat_filter = st.selectbox("Select Category", options=['All'] + list(df_fund['category'].unique()))
    
    filtered_funds = df_fund
    if amc_filter != 'All':
        filtered_funds = filtered_funds[filtered_funds['amc'] == amc_filter]
    if cat_filter != 'All':
        filtered_funds = filtered_funds[filtered_funds['category'] == cat_filter]
        
    st.dataframe(filtered_funds.merge(df_perf, on='amfi_code')[['scheme_name', 'category', '1y_return', '3y_return', 'expense_ratio']])
    
    if not df_nav.empty:
        selected_fund = st.selectbox("Select Fund for NAV Trend", options=filtered_funds['scheme_name'])
        fund_code = df_fund[df_fund['scheme_name'] == selected_fund]['amfi_code'].iloc[0]
        fund_nav = df_nav[df_nav['amfi_code'] == fund_code]
        fig = px.line(fund_nav, x='date_id', y='nav', title=f"{selected_fund} NAV Trend", color_discrete_sequence=[BLUE])
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header("Investor Analytics")
    if not df_trans.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Transactions by State")
            state_data = df_trans.groupby('state')['amount'].sum().reset_index()
            fig = px.bar(state_data, x='state', y='amount', color_discrete_sequence=[EMERALD])
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.subheader("Transaction Type Split")
            type_data = df_trans.groupby('transaction_type')['amount'].sum().reset_index()
            fig = px.pie(type_data, values='amount', names='transaction_type', hole=0.4, color_discrete_sequence=px.colors.sequential.Blues)
            st.plotly_chart(fig, use_container_width=True)
