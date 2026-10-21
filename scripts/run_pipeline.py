"""
Master Execution Pipeline for Bluestock Mutual Fund Analytics Platform.

Orchestrates the complete data engineering, quantitative analytics,
notebook generation, institutional reporting, and system verification pipeline.

Usage:
    python scripts/run_pipeline.py
"""

import sys
import os
import time

# Ensure workspace root is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from scripts.generate_mock_data import generate_mock_data
from scripts.live_nav_fetch import fetch_live_nav
from scripts.etl_pipeline import clean_data_and_load_db
from scripts.calculate_metrics import compute_performance_metrics
from scripts.week_1_foundation import run_week_1_foundation
from scripts.make_notebooks import create_performance_notebook, create_eda_notebook
from scripts.generate_reports import generate_pdf_report, generate_presentation


def run_master_pipeline():
    """
    Executes all stages of the Bluestock Mutual Fund Analytics Capstone sequentially:
    Stage 1: Raw Data Verification & Generation
    Stage 2: Live AMFI REST API Ingestion
    Stage 3: ETL Cleansing & Star Schema Warehouse Loading
    Stage 4: Quantitative Risk Modeling & Scorecard Generation
    Stage 5: Foundational Statistics & Jupyter Notebook Generation
    Stage 6: Institutional PDF Report (18 Pages) & Presentation Deck (12 Slides)
    Stage 7: System Verification & Deliverables Audit
    """
    start_time = time.time()
    print("=" * 75)
    print("  BLUESTOCK FINTECH — MUTUAL FUND ANALYTICS MASTER PIPELINE (v1.0)")
    print("=" * 75)

    # Stage 1: Raw Data Check & Ingestion
    print("\n[STAGE 1/6] Checking Raw Data Requirements...")
    raw_files = [
        'fund_master.csv', 'nav_history.csv', 'investor_transactions.csv',
        'scheme_performance.csv', 'aum_by_fund_house.csv', 'monthly_sip.csv',
        'category_inflows.csv', 'folio_count.csv', 'portfolio_holdings.csv',
        'benchmark.csv'
    ]
    missing = [f for f in raw_files if not os.path.exists(os.path.join('data/raw', f))]
    if missing:
        print(f"[STAGE 1/6] Generating {len(missing)} missing raw datasets...")
        generate_mock_data()
    else:
        print(f"[STAGE 1/6] All {len(raw_files)} core raw datasets verified.")

    # Stage 2: Live API Sync
    print("\n[STAGE 2/6] Syncing Live NAV via mfapi.in REST API...")
    fetch_live_nav(125497)

    # Stage 3: ETL Pipeline & Star Schema DB
    print("\n[STAGE 3/6] Running ETL Cleansing & Star Schema Ingestion...")
    clean_data_and_load_db()

    # Stage 4: Quantitative Analytics & Risk Engine
    print("\n[STAGE 4/6] Executing Quantitative Risk Modeling & Scorecards...")
    compute_performance_metrics()

    # Stage 5: Foundations & Notebook Generation
    print("\n[STAGE 5/6] Generating Foundational Charts & Jupyter Notebooks...")
    run_week_1_foundation()
    create_performance_notebook()
    create_eda_notebook()

    # Stage 6: Institutional Reports & Presentation
    print("\n[STAGE 6/6] Compiling Publication PDF Report & Corporate Deck...")
    generate_pdf_report()
    generate_presentation()

    # Stage 7: Deliverables Audit
    elapsed = time.time() - start_time
    print("\n" + "=" * 75)
    print(f"  PIPELINE EXECUTION COMPLETE — Total Duration: {elapsed:.2f}s")
    print("=" * 75)

    deliverables = [
        ("SQLite Database", "data/db/bluestock_mf.db"),
        ("Processed Fund Master", "data/processed/fund_master.csv"),
        ("Processed NAV History", "data/processed/nav_history.csv"),
        ("Fund Scorecard", "data/processed/fund_scorecard.csv"),
        ("EDA Notebook", "notebooks/03_eda_analysis.ipynb"),
        ("Quant Notebook", "notebooks/04_performance_analytics.ipynb"),
        ("Final PDF Report (18 Pages)", "reports/Final_Report.pdf"),
        ("Executive Deck (12 Slides)", "reports/Bluestock_MF_Presentation.pptx"),
        ("Streamlit BI App", "dashboard/app.py"),
    ]

    print("\n[AUDIT] Deliverables Verification Checklist:")
    all_ok = True
    for name, path in deliverables:
        exists = os.path.exists(path)
        status = "PASSED (OK)" if exists else "FAILED (MISSING)"
        if not exists:
            all_ok = False
        size_kb = os.path.getsize(path) / 1024 if exists else 0
        print(f"  • {name:<30} [{path}]: {status} ({size_kb:.1f} KB)")

    if all_ok:
        print("\n>>> ALL CAPSTONE DELIVERABLES SUCCESSFULLY VERIFIED (100% READY) <<<")
        print("To launch the interactive Business Intelligence dashboard, run:")
        print("    streamlit run dashboard/app.py")
    else:
        print("\n>>> WARNING: One or more deliverables could not be verified. <<<")


if __name__ == "__main__":
    run_master_pipeline()
