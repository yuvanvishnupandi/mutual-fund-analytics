-- sql/schema.sql
-- Star schema design for Bluestock Mutual Fund Analytics

CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code INTEGER PRIMARY KEY,
    amc TEXT,
    scheme_name TEXT,
    category TEXT,
    risk_grade TEXT,
    expense_ratio REAL
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_id TEXT PRIMARY KEY, -- 'YYYY-MM-DD'
    year INTEGER,
    month INTEGER,
    day INTEGER,
    quarter INTEGER,
    is_weekend BOOLEAN
);

CREATE TABLE IF NOT EXISTS fact_nav (
    nav_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code INTEGER,
    date_id TEXT,
    nav REAL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id)
);

CREATE TABLE IF NOT EXISTS fact_transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id INTEGER,
    amfi_code INTEGER,
    transaction_date TEXT,
    transaction_type TEXT,
    amount REAL,
    kyc_status TEXT,
    state TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (transaction_date) REFERENCES dim_date(date_id)
);

CREATE TABLE IF NOT EXISTS fact_performance (
    amfi_code INTEGER PRIMARY KEY,
    "1y_return" REAL,
    "3y_return" REAL,
    "5y_return" REAL,
    expense_ratio REAL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE IF NOT EXISTS fact_aum (
    aum_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amc TEXT,
    year INTEGER,
    aum_lakh_cr REAL
);
