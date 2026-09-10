import pandas as pd
import sqlite3
from sqlalchemy import create_engine, text
import os

def clean_data_and_load_db():
    print("Starting ETL process...")
    engine = create_engine('sqlite:///data/db/bluestock_mf.db')
    
    # 1. Clean nav_history.csv
    print("Cleaning nav_history...")
    df_nav = pd.read_csv('data/raw/nav_history.csv')
    df_nav['date'] = pd.to_datetime(df_nav['date'])
    df_nav = df_nav.sort_values(by=['amfi_code', 'date'])
    # ffill and drop duplicates
    df_nav['nav'] = df_nav.groupby('amfi_code')['nav'].ffill()
    df_nav = df_nav.dropna(subset=['nav'])
    df_nav = df_nav.drop_duplicates(subset=['amfi_code', 'date'])
    df_nav = df_nav[df_nav['nav'] > 0]
    
    # rename for db
    df_nav.rename(columns={'date': 'date_id'}, inplace=True)
    df_nav['date_id'] = df_nav['date_id'].dt.strftime('%Y-%m-%d')
    df_nav.to_csv('data/processed/nav_history.csv', index=False)
    
    # 2. Clean investor_transactions.csv
    print("Cleaning investor_transactions...")
    df_trans = pd.read_csv('data/raw/investor_transactions.csv')
    df_trans['transaction_type'] = df_trans['transaction_type'].str.strip().str.upper()
    df_trans['transaction_type'] = df_trans['transaction_type'].replace({'LUMP': 'LUMPSUM'})
    df_trans = df_trans[df_trans['amount'] > 0]
    df_trans['transaction_date'] = pd.to_datetime(df_trans['transaction_date']).dt.strftime('%Y-%m-%d')
    df_trans.to_csv('data/processed/investor_transactions.csv', index=False)

    # 3. Clean scheme_performance.csv
    print("Cleaning scheme_performance...")
    df_perf = pd.read_csv('data/raw/scheme_performance.csv')
    # Filter expense ratio
    df_perf['expense_ratio'] = df_perf['expense_ratio'].clip(lower=0.1, upper=2.5)
    df_perf.to_csv('data/processed/scheme_performance.csv', index=False)
    
    # 4. Load other dims/facts
    print("Loading other files...")
    df_fund = pd.read_csv('data/raw/fund_master.csv')
    df_aum = pd.read_csv('data/raw/aum_by_fund_house.csv')
    
    # Save processed versions just to be safe
    df_fund.to_csv('data/processed/fund_master.csv', index=False)
    df_aum.to_csv('data/processed/aum_by_fund_house.csv', index=False)

    # Create dim_date
    dates = pd.date_range(start='2022-01-01', end='2025-12-31')
    df_date = pd.DataFrame({'date_id': dates.strftime('%Y-%m-%d')})
    df_date['year'] = dates.year
    df_date['month'] = dates.month
    df_date['day'] = dates.day
    df_date['quarter'] = dates.quarter
    df_date['is_weekend'] = dates.dayofweek >= 5
    df_date.to_csv('data/processed/dim_date.csv', index=False)

    # Load to SQL
    print("Loading to SQLite DB...")
    with engine.begin() as connection:
        # Load schema
        with open('sql/schema.sql', 'r') as f:
            for statement in f.read().split(';'):
                if statement.strip():
                    connection.execute(text(statement))

    df_fund.to_sql('dim_fund', con=engine, if_exists='append', index=False)
    df_date.to_sql('dim_date', con=engine, if_exists='append', index=False)
    df_nav.to_sql('fact_nav', con=engine, if_exists='append', index=False)
    df_trans.to_sql('fact_transactions', con=engine, if_exists='append', index=False)
    df_perf.to_sql('fact_performance', con=engine, if_exists='append', index=False)
    df_aum.to_sql('fact_aum', con=engine, if_exists='append', index=False)

    print("ETL pipeline complete. DB loaded successfully.")

if __name__ == "__main__":
    clean_data_and_load_db()
