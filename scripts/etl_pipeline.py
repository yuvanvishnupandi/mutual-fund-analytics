"""
ETL Pipeline for Bluestock Mutual Fund Analytics Platform.

This module extracts raw mutual fund data from CSV sources, cleans and validates
the records, applies business rules (e.g., transaction type normalization, expense
ratio clamping, NAV forward-filling), and loads the star schema into a SQLite
data warehouse (data/db/bluestock_mf.db).
"""

import os
import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text


def clean_data_and_load_db():
    """
    Executes the end-to-end data cleansing and warehouse ingestion pipeline.

    1. Cleans historical NAV data by sorting, forward-filling gaps, removing duplicates,
       and filtering out non-positive NAV values.
    2. Standardizes investor transactions by normalizing transaction type strings,
       verifying positive amounts, and formatting dates.
    3. Normalizes scheme performance metrics by constraining expense ratios
       to regulatory ranges (0.1% - 2.5%).
    4. Generates a comprehensive date dimension table spanning 2022 to 2025.
    5. Re-creates the SQLite database star schema and loads dimension and fact tables.
    """
    print("[ETL] Starting data cleansing and database ingestion pipeline...")
    os.makedirs('data/processed', exist_ok=True)
    os.makedirs('data/db', exist_ok=True)

    db_path = 'data/db/bluestock_mf.db'
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"[ETL] Reset existing database at {db_path} for clean rebuild.")
        except Exception as e:
            print(f"[ETL] Note: Could not remove existing DB file directly: {e}")

    engine = create_engine(f'sqlite:///{db_path}')

    # 1. Clean nav_history.csv
    print("[ETL] Cleaning historical NAV data (nav_history.csv)...")
    df_nav = pd.read_csv('data/raw/nav_history.csv')
    df_nav['date'] = pd.to_datetime(df_nav['date'])
    df_nav = df_nav.sort_values(by=['amfi_code', 'date'])
    
    # Forward-fill missing NAVs per fund and remove duplicates
    df_nav['nav'] = df_nav.groupby('amfi_code')['nav'].ffill()
    df_nav = df_nav.dropna(subset=['nav'])
    df_nav = df_nav.drop_duplicates(subset=['amfi_code', 'date'])
    df_nav = df_nav[df_nav['nav'] > 0]
    
    # Rename date column to date_id for star schema foreign key alignment
    df_nav.rename(columns={'date': 'date_id'}, inplace=True)
    df_nav['date_id'] = df_nav['date_id'].dt.strftime('%Y-%m-%d')
    df_nav.to_csv('data/processed/nav_history.csv', index=False)
    
    # 2. Clean investor_transactions.csv
    print("[ETL] Standardizing investor transactions (investor_transactions.csv)...")
    df_trans = pd.read_csv('data/raw/investor_transactions.csv')
    df_trans['transaction_type'] = df_trans['transaction_type'].astype(str).str.strip().str.upper()
    df_trans['transaction_type'] = df_trans['transaction_type'].replace({
        'LUMP': 'LUMPSUM',
        'SIP ': 'SIP'
    })
    df_trans = df_trans[df_trans['amount'] > 0]
    df_trans['transaction_date'] = pd.to_datetime(df_trans['transaction_date']).dt.strftime('%Y-%m-%d')
    df_trans.to_csv('data/processed/investor_transactions.csv', index=False)

    # 3. Clean scheme_performance.csv
    print("[ETL] Filtering and clamping expense ratios (scheme_performance.csv)...")
    df_perf = pd.read_csv('data/raw/scheme_performance.csv')
    df_perf['expense_ratio'] = df_perf['expense_ratio'].clip(lower=0.1, upper=2.5)
    df_perf.to_csv('data/processed/scheme_performance.csv', index=False)
    
    # 4. Load fund master and AUM datasets
    print("[ETL] Processing fund dimension and AUM facts...")
    df_fund = pd.read_csv('data/raw/fund_master.csv')
    df_aum = pd.read_csv('data/raw/aum_by_fund_house.csv')
    df_fund.to_csv('data/processed/fund_master.csv', index=False)
    df_aum.to_csv('data/processed/aum_by_fund_house.csv', index=False)

    # 5. Create dim_date
    print("[ETL] Building Date Dimension table (dim_date)...")
    dates = pd.date_range(start='2022-01-01', end='2025-12-31')
    df_date = pd.DataFrame({'date_id': dates.strftime('%Y-%m-%d')})
    df_date['year'] = dates.year
    df_date['month'] = dates.month
    df_date['day'] = dates.day
    df_date['quarter'] = dates.quarter
    df_date['is_weekend'] = dates.dayofweek >= 5
    df_date.to_csv('data/processed/dim_date.csv', index=False)

    # 6. Initialize schema and ingest into SQLite
    print("[ETL] Initializing SQLite schema from sql/schema.sql...")
    with engine.begin() as connection:
        with open('sql/schema.sql', 'r') as f:
            for statement in f.read().split(';'):
                if statement.strip():
                    connection.execute(text(statement))

    print("[ETL] Ingesting dimension and fact tables into SQLite warehouse...")
    df_fund.to_sql('dim_fund', con=engine, if_exists='append', index=False)
    df_date.to_sql('dim_date', con=engine, if_exists='append', index=False)
    df_nav.to_sql('fact_nav', con=engine, if_exists='append', index=False)
    df_trans.to_sql('fact_transactions', con=engine, if_exists='append', index=False)
    df_perf.to_sql('fact_performance', con=engine, if_exists='append', index=False)
    df_aum.to_sql('fact_aum', con=engine, if_exists='append', index=False)

    print("[ETL] ETL pipeline completed successfully. Star schema warehouse is fully populated.")


if __name__ == "__main__":
    clean_data_and_load_db()
