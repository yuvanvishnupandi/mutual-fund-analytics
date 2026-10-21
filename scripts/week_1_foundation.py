"""
Week 1 Core Analytics Foundation Script.

Implements baseline exploratory statistical routines on mutual fund expense ratios
(mean, median, standard deviation) and generates initial category distribution charts.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt


def run_week_1_foundation():
    """
    Executes foundational data analysis on mutual fund expense ratios
    and exports a business category distribution visualization to reports/week_1_chart.png.
    """
    print("[Week1] Executing foundational analytics on fund_master.csv...")
    if not os.path.exists('data/raw/fund_master.csv'):
        print("[Week1] Error: data/raw/fund_master.csv not found.")
        return

    df = pd.read_csv('data/raw/fund_master.csv')

    # Impute missing expense ratio with column mean if any exist
    df['expense_ratio'] = df['expense_ratio'].fillna(df['expense_ratio'].mean())

    mean_er = float(df['expense_ratio'].mean())
    median_er = float(df['expense_ratio'].median())
    std_er = float(df['expense_ratio'].std())

    print(f"[Week1] Expense Ratio Statistics — Mean: {mean_er:.2f}%, Median: {median_er:.2f}%, Std Dev: {std_er:.2f}%")

    os.makedirs('reports', exist_ok=True)
    plt.figure(figsize=(9, 4.8))
    category_counts = df['category'].value_counts()
    bars = category_counts.plot(kind='bar', color='#1E3A8A', edgecolor='black', width=0.6)
    
    plt.title('Mutual Fund Schemes by Category (Week 1 Foundation)', fontsize=12, fontweight='bold', pad=12)
    plt.xlabel('Category', fontsize=10)
    plt.ylabel('Number of Schemes', fontsize=10)
    plt.xticks(rotation=0)
    plt.tight_layout()

    plt.savefig('reports/week_1_chart.png', dpi=300)
    plt.close()
    print("[Week1] Successfully saved foundational chart to reports/week_1_chart.png")


if __name__ == "__main__":
    run_week_1_foundation()
