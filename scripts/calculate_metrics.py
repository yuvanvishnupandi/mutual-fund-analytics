"""
Performance Analytics and Scorecard Generation Module.

Computes quantitative risk-adjusted metrics (CAGR, Sharpe Ratio, Sortino Ratio,
Maximum Drawdown, Alpha, Beta vs Nifty 50 Benchmark) and compiles the composite
fund scorecard for all mutual fund schemes. Also exports high-resolution visual
charts to the reports directory for inclusion in institutional PDF and PPTX decks.
"""

import os
import sqlite3
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns


def compute_performance_metrics():
    """
    Computes financial ratios, risk metrics, and composite scorecard rankings,
    saving data/processed/fund_scorecard.csv and analytical charts to reports/.
    """
    print("[Analytics] Connecting to SQLite warehouse for performance computation...")
    conn = sqlite3.connect('data/db/bluestock_mf.db')
    df_nav = pd.read_sql('SELECT * FROM fact_nav', conn)
    df_fund = pd.read_sql('SELECT * FROM dim_fund', conn)
    df_bench = pd.read_csv('data/raw/benchmark.csv')
    df_aum = pd.read_sql('SELECT * FROM fact_aum', conn)
    df_trans = pd.read_sql('SELECT * FROM fact_transactions', conn)
    df_sip = pd.read_csv('data/raw/monthly_sip.csv')
    conn.close()

    # Preprocessing dates
    df_nav['date_id'] = pd.to_datetime(df_nav['date_id'])
    df_bench['date'] = pd.to_datetime(df_bench['date'])
    df_nav = df_nav.sort_values(['amfi_code', 'date_id'])

    # 1. Daily returns
    df_nav['daily_return'] = df_nav.groupby('amfi_code')['nav'].pct_change()

    # 2. Overall CAGR calculation
    cagr_records = []
    for amfi, grp in df_nav.groupby('amfi_code'):
        if len(grp) >= 2:
            start_val = grp['nav'].iloc[0]
            end_val = grp['nav'].iloc[-1]
            days = (grp['date_id'].iloc[-1] - grp['date_id'].iloc[0]).days
            years = days / 365.25
            cagr = ((end_val / start_val) ** (1 / years) - 1) if years > 0 else 0.0
        else:
            cagr = 0.0
        cagr_records.append({'amfi_code': amfi, 'overall_cagr': round(cagr * 100, 2)})
    df_cagr = pd.DataFrame(cagr_records)

    # 3. Sharpe, Sortino, Max Drawdown
    rf_annual = 0.065
    rf_daily = rf_annual / 252.0
    risk_records = []

    for amfi, grp in df_nav.groupby('amfi_code'):
        ret = grp['daily_return'].dropna()
        excess = ret - rf_daily

        std_dev = ret.std()
        sharpe = (excess.mean() / std_dev) * np.sqrt(252) if std_dev > 0 else 0.0

        downside = ret[ret < 0]
        downside_std = downside.std()
        sortino = (excess.mean() / downside_std) * np.sqrt(252) if downside_std > 0 else 0.0

        cum_max = grp['nav'].cummax()
        dd = (grp['nav'] / cum_max) - 1
        mdd = dd.min() * 100  # percentage

        risk_records.append({
            'amfi_code': amfi,
            'sharpe_ratio': round(float(sharpe), 2),
            'sortino_ratio': round(float(sortino), 2),
            'max_drawdown_pct': round(float(mdd), 2)
        })
    df_risk = pd.DataFrame(risk_records)

    # 4. Alpha & Beta vs Benchmark (Nifty 50)
    df_merged = pd.merge(df_nav, df_bench, left_on='date_id', right_on='date', how='inner')
    df_merged['bench_ret'] = df_merged['nifty_50'].pct_change()

    capm_records = []
    for amfi, grp in df_merged.groupby('amfi_code'):
        clean = grp.dropna(subset=['daily_return', 'bench_ret'])
        if len(clean) > 10:
            slope, intercept, r_val, p_val, std_err = stats.linregress(clean['bench_ret'], clean['daily_return'])
            beta = slope
            alpha = intercept * 252 * 100  # annualized alpha percentage
        else:
            beta = 1.0
            alpha = 0.0
        capm_records.append({
            'amfi_code': amfi,
            'beta': round(float(beta), 2),
            'alpha_pct': round(float(alpha), 2)
        })
    df_capm = pd.DataFrame(capm_records)

    # 5. Composite Scorecard
    df_final = df_fund.merge(df_risk, on='amfi_code').merge(df_capm, on='amfi_code').merge(df_cagr, on='amfi_code')

    df_final['cagr_rank'] = df_final['overall_cagr'].rank(pct=True)
    df_final['sharpe_rank'] = df_final['sharpe_ratio'].rank(pct=True)
    df_final['alpha_rank'] = df_final['alpha_pct'].rank(pct=True)
    df_final['er_rank'] = df_final['expense_ratio'].rank(ascending=False, pct=True)
    df_final['dd_rank'] = df_final['max_drawdown_pct'].rank(pct=True)

    df_final['fund_scorecard'] = (
        0.30 * df_final['cagr_rank'] +
        0.25 * df_final['sharpe_rank'] +
        0.20 * df_final['alpha_rank'] +
        0.15 * df_final['er_rank'] +
        0.10 * df_final['dd_rank']
    ) * 100
    df_final['fund_scorecard'] = df_final['fund_scorecard'].round(2)

    os.makedirs('data/processed', exist_ok=True)
    df_final.to_csv('data/processed/fund_scorecard.csv', index=False)
    print(f"[Analytics] Successfully calculated scorecard for {len(df_final)} funds -> data/processed/fund_scorecard.csv")

    # 6. Generate High-Res Charts for Reports
    os.makedirs('reports', exist_ok=True)
    sns.set_theme(style="whitegrid")

    # Chart 1: Category Distribution
    plt.figure(figsize=(8, 4.5))
    cat_counts = df_fund['category'].value_counts()
    bars = plt.bar(cat_counts.index, cat_counts.values, color=['#1E3A8A', '#10B981', '#3B82F6'], edgecolor='black')
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.3, int(yval), ha='center', va='bottom', fontweight='bold')
    plt.title('Mutual Fund Schemes by Category', fontsize=12, fontweight='bold', pad=12)
    plt.xlabel('Category', fontsize=10)
    plt.ylabel('Number of Schemes', fontsize=10)
    plt.tight_layout()
    plt.savefig('reports/week_1_chart.png', dpi=300)
    plt.close()

    # Chart 2: AUM Growth by AMC
    plt.figure(figsize=(9, 4.5))
    aum_pivot = df_aum.pivot(index='year', columns='amc', values='aum_lakh_cr')
    aum_pivot.plot(kind='bar', figsize=(9, 4.5), colormap='tab10', width=0.8, edgecolor='black')
    plt.title('AUM Growth by Fund House (2022-2025 in Lakh Cr)', fontsize=12, fontweight='bold', pad=12)
    plt.xlabel('Calendar Year', fontsize=10)
    plt.ylabel('AUM (₹ Lakh Crore)', fontsize=10)
    plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', frameon=True, fontsize=8)
    plt.tight_layout()
    plt.savefig('reports/aum_growth.png', dpi=300)
    plt.close()

    # Chart 3: Monthly SIP Inflow Trend
    plt.figure(figsize=(8.5, 4.2))
    plt.plot(range(len(df_sip)), df_sip['sip_amount_cr'], marker='o', markersize=3, color='#10B981', linewidth=2)
    plt.title('Monthly SIP Inflow Trajectory (₹ Crore)', fontsize=12, fontweight='bold', pad=12)
    plt.xlabel('Timeline (Months 2022-2025)', fontsize=10)
    plt.ylabel('SIP Inflow (₹ Cr)', fontsize=10)
    # Sample month ticks
    ticks_idx = list(range(0, len(df_sip), 6))
    plt.xticks(ticks_idx, [df_sip['month'].iloc[i] for i in ticks_idx], rotation=45)
    plt.tight_layout()
    plt.savefig('reports/sip_inflow_trend.png', dpi=300)
    plt.close()

    # Chart 4: Sharpe vs CAGR Scatter
    plt.figure(figsize=(8, 4.5))
    palette = {'Equity': '#1E3A8A', 'Debt': '#10B981', 'Hybrid': '#F59E0B'}
    sns.scatterplot(
        data=df_final,
        x='overall_cagr',
        y='sharpe_ratio',
        hue='category',
        palette=palette,
        s=80,
        alpha=0.9,
        edgecolor='black'
    )
    plt.axhline(0, color='gray', linestyle='--', linewidth=0.8)
    plt.axvline(0, color='gray', linestyle='--', linewidth=0.8)
    plt.title('Risk-Adjusted Efficiency: Overall CAGR vs Sharpe Ratio', fontsize=12, fontweight='bold', pad=12)
    plt.xlabel('Overall CAGR (%)', fontsize=10)
    plt.ylabel('Annualized Sharpe Ratio (Rf = 6.5%)', fontsize=10)
    plt.tight_layout()
    plt.savefig('reports/sharpe_vs_cagr.png', dpi=300)
    plt.close()

    # Chart 5: Alpha vs Beta Scatter
    plt.figure(figsize=(8, 4.5))
    sns.scatterplot(
        data=df_final,
        x='beta',
        y='alpha_pct',
        hue='category',
        palette=palette,
        s=80,
        alpha=0.9,
        edgecolor='black'
    )
    plt.axhline(0, color='red', linestyle='--', linewidth=0.8)
    plt.axvline(1.0, color='black', linestyle=':', linewidth=0.8)
    plt.title('CAPM Framework: Systematic Risk (Beta) vs Annualized Alpha', fontsize=12, fontweight='bold', pad=12)
    plt.xlabel('Beta (Market Sensitivity vs Nifty 50)', fontsize=10)
    plt.ylabel('Annualized Alpha (%)', fontsize=10)
    plt.tight_layout()
    plt.savefig('reports/alpha_beta_scatter.png', dpi=300)
    plt.close()

    # Chart 6: Transactions by State
    plt.figure(figsize=(8.5, 4.2))
    state_totals = df_trans.groupby('state')['amount'].sum().sort_values(ascending=False).head(10)
    bars = plt.bar(state_totals.index, state_totals.values / 1e5, color='#2563EB', edgecolor='black')
    plt.title('Top 10 States by Transaction Value (in ₹ Lakhs)', fontsize=12, fontweight='bold', pad=12)
    plt.xlabel('State Code', fontsize=10)
    plt.ylabel('Total Inflow (₹ Lakhs)', fontsize=10)
    plt.tight_layout()
    plt.savefig('reports/state_transactions.png', dpi=300)
    plt.close()

    # Chart 7: Correlation Heatmap
    df_nav_p = df_nav.merge(df_fund, on='amfi_code')
    df_pivot = df_nav_p.pivot(index='date_id', columns='scheme_name', values='nav').pct_change().dropna()
    top_schemes = df_fund['scheme_name'].iloc[:8]
    corr = df_pivot[top_schemes].corr()

    plt.figure(figsize=(8, 6))
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5, cbar=True)
    plt.title('Return Correlation Heatmap (Selected Schemes)', fontsize=12, fontweight='bold', pad=12)
    plt.tight_layout()
    plt.savefig('reports/correlation_heatmap.png', dpi=300)
    plt.close()

    print("[Analytics] All 7 institutional charts generated and saved in reports/")


if __name__ == "__main__":
    compute_performance_metrics()
