import pandas as pd
import matplotlib.pyplot as plt
import os

def run_week_1_foundation():
    print("Loading raw dataset for Week 1 foundation...")
    # Load dataset
    df = pd.read_csv('data/raw/fund_master.csv')
    
    # Clean dataset (handle any nulls in expense ratio)
    df['expense_ratio'] = df['expense_ratio'].fillna(df['expense_ratio'].mean())
    
    # Calculate Mean/Median/Standard Deviation
    mean_er = df['expense_ratio'].mean()
    median_er = df['expense_ratio'].median()
    std_er = df['expense_ratio'].std()
    
    print(f"Expense Ratio Stats - Mean: {mean_er:.2f}, Median: {median_er:.2f}, Std Dev: {std_er:.2f}")
    
    # Export basic Matplotlib business chart as PNG
    plt.figure(figsize=(10, 6))
    category_counts = df['category'].value_counts()
    category_counts.plot(kind='bar', color='skyblue', edgecolor='black')
    plt.title('Mutual Fund Schemes by Category')
    plt.xlabel('Category')
    plt.ylabel('Number of Schemes')
    plt.tight_layout()
    
    os.makedirs('reports', exist_ok=True)
    plt.savefig('reports/week_1_chart.png')
    print("Saved basic business chart to reports/week_1_chart.png")

if __name__ == "__main__":
    run_week_1_foundation()
