"""
Notebook Generator Module for EDA and Performance Analytics.

Constructs production Jupyter Notebooks (03_eda_analysis.ipynb and 04_performance_analytics.ipynb)
in the notebooks/ directory with reproducible Python cells, narrative analysis, and visualization logic.
"""

import os
import nbformat as nbf


def create_performance_notebook():
    """Constructs notebooks/04_performance_analytics.ipynb containing quantitative modeling code."""
    os.makedirs('notebooks', exist_ok=True)
    nb = nbf.v4.new_notebook()

    intro_md = """# Bluestock Mutual Fund Analytics — Performance & Risk Modeling
This notebook computes quantitative risk-adjusted performance metrics across Indian mutual fund schemes:
- Compound Annual Growth Rate (CAGR)
- Annualized Sharpe Ratio ($R_f = 6.50\\%$)
- Sortino Ratio (Downside Deviation)
- Maximum Drawdown ($MDD$)
- Benchmark Regression (CAPM Beta $\\beta$ and Annualized Alpha $\\alpha$ vs Nifty 50)
- Multi-Factor Composite Fund Scorecard
"""

    code = """import os
import sqlite3
import pandas as pd
import numpy as np
from scipy import stats

print("[Notebook] Initializing Performance Analytics routine...")
conn = sqlite3.connect('../data/db/bluestock_mf.db')
df_nav = pd.read_sql('SELECT * FROM fact_nav', conn)
df_fund = pd.read_sql('SELECT * FROM dim_fund', conn)
df_bench = pd.read_csv('../data/raw/benchmark.csv')
conn.close()

# Preprocess dates
df_nav['date_id'] = pd.to_datetime(df_nav['date_id'])
df_bench['date'] = pd.to_datetime(df_bench['date'])
df_nav = df_nav.sort_values(['amfi_code', 'date_id'])

# 1. Daily Returns
df_nav['daily_return'] = df_nav.groupby('amfi_code')['nav'].pct_change()

# 2. Overall CAGR calculation
cagr_data = []
for amfi, grp in df_nav.groupby('amfi_code'):
    if len(grp) >= 2:
        start_val = grp['nav'].iloc[0]
        end_val = grp['nav'].iloc[-1]
        years = (grp['date_id'].iloc[-1] - grp['date_id'].iloc[0]).days / 365.25
        cagr = (end_val / start_val) ** (1 / years) - 1 if years > 0 else 0.0
    else:
        cagr = 0.0
    cagr_data.append({'amfi_code': amfi, 'overall_cagr': round(cagr * 100, 2)})
df_cagr = pd.DataFrame(cagr_data)

# 3. Sharpe & Sortino (Rf = 6.5% annual)
rf_annual = 0.065
rf_daily = rf_annual / 252.0

risk_metrics = []
for amfi, grp in df_nav.groupby('amfi_code'):
    ret = grp['daily_return'].dropna()
    excess = ret - rf_daily
    
    std_dev = ret.std()
    sharpe = (excess.mean() / std_dev) * np.sqrt(252) if std_dev > 0 else 0.0
    
    neg = ret[ret < 0]
    downside_std = neg.std()
    sortino = (excess.mean() / downside_std) * np.sqrt(252) if downside_std > 0 else 0.0
    
    cum_max = grp['nav'].cummax()
    dd = (grp['nav'] / cum_max) - 1
    mdd = dd.min() * 100
    
    risk_metrics.append({
        'amfi_code': amfi,
        'sharpe_ratio': round(float(sharpe), 2),
        'sortino_ratio': round(float(sortino), 2),
        'max_drawdown_pct': round(float(mdd), 2)
    })
df_risk = pd.DataFrame(risk_metrics)

# 4. CAPM Alpha & Beta vs Nifty 50
df_nav_bench = pd.merge(df_nav, df_bench, left_on='date_id', right_on='date', how='inner')
df_nav_bench['bench_return'] = df_nav_bench['nifty_50'].pct_change()

capm_list = []
for amfi, grp in df_nav_bench.groupby('amfi_code'):
    clean = grp.dropna(subset=['daily_return', 'bench_return'])
    if len(clean) > 10:
        slope, intercept, r_val, p_val, std_err = stats.linregress(clean['bench_return'], clean['daily_return'])
        beta = slope
        alpha = intercept * 252 * 100
    else:
        beta = 1.0
        alpha = 0.0
    capm_list.append({'amfi_code': amfi, 'alpha_pct': round(float(alpha), 2), 'beta': round(float(beta), 2)})
df_capm = pd.DataFrame(capm_list)

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

os.makedirs('../data/processed', exist_ok=True)
df_final.to_csv('../data/processed/fund_scorecard.csv', index=False)
print("[Notebook] Top 5 Ranked Schemes by Scorecard:")
print(df_final[['scheme_name', 'category', 'overall_cagr', 'sharpe_ratio', 'fund_scorecard']].sort_values('fund_scorecard', ascending=False).head(5))
"""
    nb['cells'] = [
        nbf.v4.new_markdown_cell(intro_md),
        nbf.v4.new_code_cell(code)
    ]

    with open('notebooks/04_performance_analytics.ipynb', 'w') as f:
        nbf.write(nb, f)
    print("[Notebook] Successfully created notebooks/04_performance_analytics.ipynb")


def create_eda_notebook():
    """Constructs notebooks/03_eda_analysis.ipynb containing exploratory visual analysis code."""
    os.makedirs('notebooks', exist_ok=True)
    nb = nbf.v4.new_notebook()

    intro_md = """# Bluestock Mutual Fund Analytics — Exploratory Data Analysis (EDA)
This notebook performs statistical and visual exploration of:
- AMC Market Share and AUM Growth (2022-2025)
- Category Allocations (Equity, Debt, Hybrid)
- Retail Monthly SIP Inflow Trajectories
- Scheme Return Correlations
"""

    code = """import os
import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

print("[Notebook] Executing Exploratory Data Analysis...")
conn = sqlite3.connect('../data/db/bluestock_mf.db')
df_nav = pd.read_sql('SELECT * FROM fact_nav', conn)
df_fund = pd.read_sql('SELECT * FROM dim_fund', conn)
df_aum = pd.read_sql('SELECT * FROM fact_aum', conn)
df_sip = pd.read_csv('../data/raw/monthly_sip.csv')
conn.close()

# 1. Scheme Category Breakdown
print("[EDA] Scheme Category Count:")
print(df_fund['category'].value_counts())

# 2. AUM Concentration
print("[EDA] Total AUM by Fund House (2025):")
print(df_aum[df_aum['year'] == 2025].sort_values('aum_lakh_cr', ascending=False).head(5))

# 3. Correlation Heatmap
df_merged = df_nav.merge(df_fund, on='amfi_code')
pivot_nav = df_merged.pivot(index='date_id', columns='scheme_name', values='nav').pct_change().dropna()
top_schemes = df_fund['scheme_name'].iloc[:8]
corr_matrix = pivot_nav[top_schemes].corr()

plt.figure(figsize=(9, 7))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
plt.title('Return Correlation Matrix (Selected Mutual Fund Schemes)', fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig('../reports/correlation_heatmap.png', dpi=300)
print("[EDA] Saved correlation heatmap to ../reports/correlation_heatmap.png")
"""
    nb['cells'] = [
        nbf.v4.new_markdown_cell(intro_md),
        nbf.v4.new_code_cell(code)
    ]

    with open('notebooks/03_eda_analysis.ipynb', 'w') as f:
        nbf.write(nb, f)
    print("[Notebook] Successfully created notebooks/03_eda_analysis.ipynb")


if __name__ == "__main__":
    create_performance_notebook()
    create_eda_notebook()
