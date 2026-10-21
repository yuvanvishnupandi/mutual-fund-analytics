"""
Mock Data Generator for Bluestock Mutual Fund Analytics.

Synthesizes realistic multi-year datasets mimicking Indian mutual fund market
structures (AMFI codes, AMC groupings, NAV time-series, investor transactions,
and benchmark indices) for testing data pipelines and quantitative engines.
"""

import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np


def generate_mock_data():
    """
    Generates 10 simulated CSV datasets representing Indian mutual fund market
    activity and stores them in data/raw/.

    Generated Datasets:
    1. fund_master.csv: 40 mutual fund schemes across 10 top AMCs.
    2. nav_history.csv: Daily NAV time series (2022-2025) with simulated anomalies.
    3. investor_transactions.csv: 1,000 retail investment and redemption trades.
    4. scheme_performance.csv: Trailing 1Y, 3Y, 5Y returns and reported TERs.
    5. aum_by_fund_house.csv: Annual AUM trajectory across AMCs.
    6. monthly_sip.csv: Monthly retail SIP inflow progression.
    7. category_inflows.csv: Net inflows partitioned across Equity, Debt, and Hybrid.
    8. folio_count.csv: Monthly active investor folio totals.
    9. portfolio_holdings.csv: Sectoral asset allocations for each fund.
    10. benchmark.csv: Daily closing values for Nifty 50 and Nifty 100 indices.
    """
    print("[DataGen] Generating synthetic mutual fund datasets in data/raw/...")
    os.makedirs("data/raw", exist_ok=True)
    
    # 1. fund_master.csv
    amc_list = ['SBI', 'HDFC', 'ICICI', 'Nippon', 'Kotak', 'Axis', 'ABSL', 'UTI', 'Mirae', 'DSP']
    categories = ['Equity', 'Debt', 'Hybrid']
    np.random.seed(42)
    
    funds = []
    for amc in amc_list:
        for i in range(4):  # 4 schemes per AMC = 40 schemes
            funds.append({
                'amfi_code': int(np.random.randint(100000, 150000)),
                'amc': amc,
                'scheme_name': f"{amc} {np.random.choice(categories)} Fund {i+1}",
                'category': np.random.choice(categories),
                'risk_grade': np.random.choice(['Low', 'Moderate', 'High', 'Very High']),
                'expense_ratio': round(float(np.random.uniform(0.1, 2.5)), 2)
            })
    df_funds = pd.DataFrame(funds)
    df_funds.to_csv("data/raw/fund_master.csv", index=False)
    
    # 2. nav_history.csv
    dates = pd.date_range(start='2022-01-01', end='2025-12-31', freq='B')
    nav_records = []
    for amfi in df_funds['amfi_code']:
        base_nav = np.random.uniform(10, 100)
        navs = [base_nav]
        for _ in range(1, len(dates)):
            change = np.random.normal(0, 0.01)  # daily return
            new_nav = navs[-1] * (1 + change)
            navs.append(max(new_nav, 0.1))  # ensure NAV > 0
        
        for date, nav in zip(dates, navs):
            nav_records.append({
                'amfi_code': amfi,
                'date': date.strftime('%Y-%m-%d'),
                'nav': round(float(nav), 4)
            })
    
    # Add minor noise and duplicate instances for ETL validation testing
    nav_df = pd.DataFrame(nav_records)
    nav_df.loc[np.random.choice(nav_df.index, 50, replace=False), 'nav'] = np.nan 
    nav_df = pd.concat([nav_df, nav_df.sample(20)]).sample(frac=1, random_state=42).reset_index(drop=True)
    nav_df.to_csv("data/raw/nav_history.csv", index=False)
    
    # 3. investor_transactions.csv
    transactions = []
    for _ in range(1000):
        transactions.append({
            'investor_id': int(np.random.randint(1000, 6000)),
            'amfi_code': int(np.random.choice(df_funds['amfi_code'])),
            'transaction_date': pd.Timestamp(np.random.choice(dates)).strftime('%Y-%m-%d'),
            'transaction_type': np.random.choice(['SIP', 'Lumpsum', 'Redemption', ' sip ', 'LUMP']),
            'amount': round(float(np.random.uniform(500, 50000)), 2),
            'kyc_status': np.random.choice(['Verified', 'Pending', 'Rejected'], p=[0.82, 0.12, 0.06]),
            'state': np.random.choice(['MH', 'KA', 'TN', 'DL', 'GJ', 'UP', 'WB', 'RJ', 'AP', 'TS'])
        })
    df_trans = pd.DataFrame(transactions)
    df_trans.to_csv("data/raw/investor_transactions.csv", index=False)
    
    # 4. scheme_performance.csv
    perf_records = []
    for amfi in df_funds['amfi_code']:
        perf_records.append({
            'amfi_code': amfi,
            '1y_return': round(float(np.random.normal(12, 5)), 2),
            '3y_return': round(float(np.random.normal(10, 4)), 2),
            '5y_return': round(float(np.random.normal(11, 3)), 2),
            'expense_ratio': round(float(np.random.uniform(0.1, 2.5)), 2)
        })
    pd.DataFrame(perf_records).to_csv("data/raw/scheme_performance.csv", index=False)

    # 5. aum_by_fund_house.csv
    aum_records = []
    for amc in amc_list:
        base_aum = np.random.uniform(2.0, 8.0)
        for year in range(2022, 2026):
            base_aum *= np.random.uniform(1.10, 1.25)
            aum_records.append({
                'amc': amc,
                'year': year,
                'aum_lakh_cr': round(float(base_aum), 2)
            })
    pd.DataFrame(aum_records).to_csv("data/raw/aum_by_fund_house.csv", index=False)

    # 6. monthly_sip.csv
    sip_records = []
    base_sip = 11000.0
    for month in pd.date_range(start='2022-01-01', end='2025-12-31', freq='ME'):
        base_sip += np.random.uniform(200, 650)
        sip_records.append({
            'month': month.strftime('%Y-%m'),
            'sip_amount_cr': round(float(base_sip), 2)
        })
    pd.DataFrame(sip_records).to_csv("data/raw/monthly_sip.csv", index=False)

    # 7. category_inflows.csv
    cat_inflows = []
    for month in pd.date_range(start='2022-01-01', end='2025-12-31', freq='ME'):
        for cat in categories:
            cat_inflows.append({
                'month': month.strftime('%Y-%m'),
                'category': cat,
                'net_inflow_cr': round(float(np.random.uniform(1000, 15000)), 2)
            })
    pd.DataFrame(cat_inflows).to_csv("data/raw/category_inflows.csv", index=False)

    # 8. folio_count.csv
    folio_records = []
    base_folios = 12.0
    for month in pd.date_range(start='2022-01-01', end='2025-12-31', freq='ME'):
        base_folios += np.random.uniform(0.15, 0.40)
        folio_records.append({
            'month': month.strftime('%Y-%m'),
            'total_folios_cr': round(float(base_folios), 2)
        })
    pd.DataFrame(folio_records).to_csv("data/raw/folio_count.csv", index=False)

    # 9. portfolio_holdings.csv
    holdings = []
    for amfi in df_funds['amfi_code']:
        for sector in ['IT', 'Financials', 'Energy', 'Healthcare', 'Auto']:
            holdings.append({
                'amfi_code': amfi,
                'sector': sector,
                'weight_pct': round(float(np.random.uniform(5, 30)), 2)
            })
    pd.DataFrame(holdings).to_csv("data/raw/portfolio_holdings.csv", index=False)

    # 10. benchmark.csv
    bench_records = []
    base_val = 15000.0
    for date in dates:
        change = np.random.normal(0.0004, 0.009)
        base_val = base_val * (1 + change)
        bench_records.append({
            'date': date.strftime('%Y-%m-%d'),
            'nifty_50': round(float(base_val), 2),
            'nifty_100': round(float(base_val * 0.9), 2)
        })
    pd.DataFrame(bench_records).to_csv("data/raw/benchmark.csv", index=False)

    print("[DataGen] Synthetic dataset generation completed successfully.")


if __name__ == "__main__":
    generate_mock_data()
