## mutual-fund-analytics

Implementation of the Mutual Fund Analytics Capstone for Bluestock Fintech.

## Install

```bash
$ pip install -r requirements.txt
```

## Usage

```bash
$ python scripts/etl_pipeline.py
$ python scripts/make_notebooks.py
$ python scripts/week_1_foundation.py
$ python scripts/generate_reports.py
$ streamlit run dashboard/app.py
```

## Structure

* `data/` - Raw datasets and SQLite database
* `scripts/` - ETL and data generation pipelines
* `notebooks/` - EDA and performance analytics
* `sql/` - Star schema and queries
* `dashboard/` - Streamlit application
* `reports/` - Generated PDF and PPTX reports
