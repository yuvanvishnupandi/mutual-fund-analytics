import nbformat as nbf
import os

def create_performance_notebook():
    nb = nbf.v4.new_notebook()
    
    code = """
import pandas as pd
import numpy as np
from scipy import stats
import sqlite3
import os

print("Loading data for Performance Analytics...")
engine = sqlite3.connect('data/db/bluestock_mf.db')
df_nav = pd.read_sql('SELECT * FROM fact_nav', engine)
df_fund = pd.read_sql('SELECT * FROM dim_fund', engine)
df_bench = pd.read_csv('data/raw/benchmark.csv')

# Ensure date is datetime
df_nav['date_id'] = pd.to_datetime(df_nav['date_id'])
df_bench['date'] = pd.to_datetime(df_bench['date'])
df_nav = df_nav.sort_values(['amfi_code', 'date_id'])

# 1. Daily Returns
df_nav['daily_return'] = df_nav.groupby('amfi_code')['nav'].pct_change()

# 2. CAGR (1yr, 3yr, 5yr)
# Using dummy values or calculating from limits. Since we only have 2022-2025 (4 years of data), we will approx.
def calc_cagr(start_val, end_val, years):
    return (end_val / start_val) ** (1/years) - 1

cagr_data = []
for amfi, group in df_nav.groupby('amfi_code'):
    nav_start = group['nav'].iloc[0]
    nav_end = group['nav'].iloc[-1]
    years = (group['date_id'].iloc[-1] - group['date_id'].iloc[0]).days / 365.25
    if years > 0:
        cagr = calc_cagr(nav_start, nav_end, years)
    else:
        cagr = np.nan
    cagr_data.append({'amfi_code': amfi, 'overall_cagr': cagr})
    
df_cagr = pd.DataFrame(cagr_data)

# 3. Sharpe & Sortino (Rf = 6.5%)
rf = 0.065
daily_rf = rf / 252

metrics = []
for amfi, group in df_nav.groupby('amfi_code'):
    returns = group['daily_return'].dropna()
    excess_returns = returns - daily_rf
    
    # Sharpe
    std_dev = returns.std()
    sharpe = (excess_returns.mean() / std_dev) * np.sqrt(252) if std_dev > 0 else 0
    
    # Sortino
    neg_returns = returns[returns < 0]
    downside_std = neg_returns.std()
    sortino = (excess_returns.mean() / downside_std) * np.sqrt(252) if downside_std > 0 else 0
    
    # Max Drawdown
    cumulative_max = group['nav'].cummax()
    drawdown = (group['nav'] / cumulative_max) - 1
    max_drawdown = drawdown.min()
    
    metrics.append({
        'amfi_code': amfi,
        'sharpe_ratio': sharpe,
        'sortino_ratio': sortino,
        'max_drawdown': max_drawdown
    })

df_metrics = pd.DataFrame(metrics)

# 4. Alpha & Beta vs Benchmark (Nifty 50)
df_nav_bench = pd.merge(df_nav, df_bench, left_on='date_id', right_on='date', how='inner')
df_nav_bench['bench_return'] = df_nav_bench['nifty_50'].pct_change()

alpha_beta = []
for amfi, group in df_nav_bench.groupby('amfi_code'):
    clean_group = group.dropna(subset=['daily_return', 'bench_return'])
    if len(clean_group) > 2:
        slope, intercept, r_value, p_value, std_err = stats.linregress(clean_group['bench_return'], clean_group['daily_return'])
        beta = slope
        alpha = intercept * 252
    else:
        beta = np.nan
        alpha = np.nan
    alpha_beta.append({'amfi_code': amfi, 'alpha': alpha, 'beta': beta})

df_ab = pd.DataFrame(alpha_beta)

# 5. Composite Fund Scorecard
df_final = df_fund.merge(df_metrics, on='amfi_code').merge(df_ab, on='amfi_code').merge(df_cagr, on='amfi_code')

# Ranks
df_final['sharpe_rank'] = df_final['sharpe_ratio'].rank(pct=True)
df_final['alpha_rank'] = df_final['alpha'].rank(pct=True)
df_final['er_rank'] = df_final['expense_ratio'].rank(ascending=False, pct=True) # inverse
df_final['dd_rank'] = df_final['max_drawdown'].rank(pct=True) # closer to 0 is better, so smaller neg is higher
df_final['cagr_rank'] = df_final['overall_cagr'].rank(pct=True)

# Weightings: 30% cagr, 25% sharpe, 20% alpha, 15% er, 10% dd
df_final['fund_scorecard'] = (
    0.30 * df_final['cagr_rank'] +
    0.25 * df_final['sharpe_rank'] +
    0.20 * df_final['alpha_rank'] +
    0.15 * df_final['er_rank'] +
    0.10 * df_final['dd_rank']
) * 100

os.makedirs('data/processed', exist_ok=True)
df_final.to_csv('data/processed/fund_scorecard.csv', index=False)
print("Saved data/processed/fund_scorecard.csv")
print(df_final[['scheme_name', 'fund_scorecard']].sort_values('fund_scorecard', ascending=False).head(10))
"""
    
    nb['cells'] = [nbf.v4.new_code_cell(code)]
    
    with open('notebooks/04_performance_analytics.ipynb', 'w') as f:
        nbf.write(nb, f)

def create_eda_notebook():
    nb = nbf.v4.new_notebook()
    
    code = """
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import sqlite3

engine = sqlite3.connect('data/db/bluestock_mf.db')
df_nav = pd.read_sql('SELECT * FROM fact_nav', engine)
df_fund = pd.read_sql('SELECT * FROM dim_fund', engine)
df_aum = pd.read_sql('SELECT * FROM fact_aum', engine)
df_sip = pd.read_csv('data/raw/monthly_sip.csv')

# 1. NAV trend line charts (2022-2026)
df_nav_fund = df_nav.merge(df_fund, on='amfi_code')
fig1 = px.line(df_nav_fund, x='date_id', y='nav', color='scheme_name', title='NAV Trend (2022-2025)')
# Uncomment to show: fig1.show()

# 2. AUM growth bar charts
fig2 = px.bar(df_aum, x='year', y='aum_lakh_cr', color='amc', title='AUM Growth by AMC', barmode='group')
# Uncomment to show: fig2.show()

# 3. SIP inflow time-series
fig3 = px.line(df_sip, x='month', y='sip_amount_cr', title='SIP Inflows (2022-2025)', markers=True)
# Uncomment to show: fig3.show()

# 4. Correlation heatmap for returns
df_nav_pivot = df_nav_fund.pivot(index='date_id', columns='scheme_name', values='nav').pct_change().dropna()
# Take top 10 funds to make heatmap readable
top_10_funds = df_nav_fund['scheme_name'].unique()[:10]
corr_matrix = df_nav_pivot[top_10_funds].corr()

plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f")
plt.title('Return Correlation Heatmap (Top 10 Funds)')
plt.tight_layout()
plt.savefig('notebooks/correlation_heatmap.png')
print("EDA plots generated and scripts ready. Note: Plotly output suppressed for non-interactive run.")
"""
    
    nb['cells'] = [nbf.v4.new_code_cell(code)]
    
    with open('notebooks/03_eda_analysis.ipynb', 'w') as f:
        nbf.write(nb, f)

if __name__ == "__main__":
    create_performance_notebook()
    create_eda_notebook()
    print("Created notebooks.")
