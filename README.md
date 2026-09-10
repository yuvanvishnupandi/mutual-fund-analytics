# Mutual Fund Analytics - Bluestock Fintech

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)

A complete end-to-end data pipeline, database design, exploratory data analysis, performance metrics calculation, and an interactive Streamlit dashboard for Mutual Fund Analytics, built as the Capstone Project for Bluestock Fintech.

## 📁 Project Structure

- `data/`: Raw downloaded CSVs, processed datasets, and the SQLite Database.
- `scripts/`: ETL pipelines, data generation, and metrics computation.
- `notebooks/`: Jupyter notebooks for EDA and Performance Analytics.
- `sql/`: Star schema design and analytical queries.
- `dashboard/`: Streamlit interactive dashboard application.
- `reports/`: Generated PDF reports, presentations, and PNG charts.

## 🚀 How to Run

### 1. Setup Environment
```bash
pip install -r requirements.txt
```

### 2. Run ETL Pipeline
To ingest data, clean it, and load it into the local SQLite DB (`data/db/bluestock_mf.db`):
```bash
python scripts/etl_pipeline.py
```

### 3. Generate Notebooks & Reports
```bash
python scripts/make_notebooks.py
python scripts/week_1_foundation.py
python scripts/generate_reports.py
```

### 4. Run the Streamlit Dashboard
```bash
streamlit run dashboard/app.py
```

## 📊 Features
- **Automated Data Pipeline**: Loads and cleans realistic MF datasets.
- **Star Schema Database**: Scalable SQLite design with dims and facts.
- **Risk Metrics**: Calculates Sharpe, Sortino, Alpha, Beta, and Max Drawdown.
- **Interactive UI**: Streamlit web app alternative to Power BI.
- **Data Visualizations**: Plotly and Seaborn visual insights into the Indian mutual fund landscape.

## 📜 Deliverables
All requirements specified in the Capstone documentation have been fulfilled, including the bonus challenges (Streamlit web app).
