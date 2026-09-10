-- sql/queries.sql

-- 1. Top 5 AMCs by AUM in 2025
SELECT amc, aum_lakh_cr 
FROM fact_aum 
WHERE year = 2025 
ORDER BY aum_lakh_cr DESC 
LIMIT 5;

-- 2. Average NAV per month for a specific fund (e.g., amfi_code 119551)
SELECT d.year, d.month, AVG(n.nav) as avg_nav
FROM fact_nav n
JOIN dim_date d ON n.date_id = d.date_id
GROUP BY n.amfi_code, d.year, d.month
ORDER BY d.year, d.month;

-- 3. Total SIP inflows by state
SELECT state, SUM(amount) as total_sip_amount
FROM fact_transactions
WHERE transaction_type = 'SIP'
GROUP BY state
ORDER BY total_sip_amount DESC;

-- 4. Count of unique schemes per category
SELECT category, COUNT(amfi_code) as scheme_count
FROM dim_fund
GROUP BY category;

-- 5. Top 10 funds with highest 3-year return
SELECT f.scheme_name, p."3y_return"
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
ORDER BY p."3y_return" DESC
LIMIT 10;

-- 6. Funds with expense ratio less than 1.0%
SELECT scheme_name, category, expense_ratio
FROM dim_fund
WHERE expense_ratio < 1.0
ORDER BY expense_ratio ASC;

-- 7. Monthly transaction volume (count of transactions)
SELECT substr(transaction_date, 1, 7) as txn_month, COUNT(*) as txn_count
FROM fact_transactions
GROUP BY txn_month
ORDER BY txn_month;

-- 8. Lumpsum vs SIP distribution (Total Amount)
SELECT transaction_type, SUM(amount) as total_amount
FROM fact_transactions
GROUP BY transaction_type;

-- 9. Daily Average NAV across all Equity funds in 2025
SELECT n.date_id, AVG(n.nav) as avg_equity_nav
FROM fact_nav n
JOIN dim_fund f ON n.amfi_code = f.amfi_code
WHERE f.category = 'Equity' AND n.date_id LIKE '2025-%'
GROUP BY n.date_id
ORDER BY n.date_id;

-- 10. Max Drawdown proxy: highest vs lowest NAV in a year for a fund
SELECT amfi_code, substr(date_id, 1, 4) as year, MAX(nav) as highest_nav, MIN(nav) as lowest_nav
FROM fact_nav
GROUP BY amfi_code, year;
