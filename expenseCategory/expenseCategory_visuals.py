import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import os

# Ensure the output directory exists
output_dir = './expenseCategory/visualizations/'
os.makedirs(output_dir, exist_ok=True)

def generate_visualization(path):
    # Load the data
    df = pd.read_csv(path)

    # Ensure spending columns are numeric
    df = df.replace('#Missing', pd.NA).apply(pd.to_numeric, errors='ignore')

    # Aggregate FY25 budget by expense category
    fy25_budget = df.groupby('Expense Category')['FY25 Budget'].sum()

    # Sort the categories by their FY25 budget in descending order
    fy25_budget = fy25_budget.sort_values(ascending=False)

    # Define a threshold for labeling (e.g., only label if > 5%)
    threshold = 0.025  # 2.5%
    total_budget = fy25_budget.sum()

    # Create a color list for significant categories; others get black
    colors = [
        plt.cm.tab20(i) if value / total_budget > threshold else 'black'
        for i, value in enumerate(fy25_budget)
    ]

    # Create the pie chart
    fig, ax = plt.subplots(figsize=(16, 12))
    wedges, texts, autotexts = ax.pie(
        fy25_budget,
        colors=colors,
        startangle=90,
        wedgeprops={'edgecolor': 'black'},
        autopct=lambda p: f'{p:.1f}%' if p > threshold * 100 else '',  # Only label large portions
    )

    # Remove text for smaller slices
    for i, (text, wedge) in enumerate(zip(texts, wedges)):
        if fy25_budget.iloc[i] / total_budget <= threshold:
            text.set_text('')

    # Create the legend with only significant slices
    legend_handles = [wedge for i, wedge in enumerate(wedges) if fy25_budget.iloc[i] / total_budget > threshold]
    legend_labels = [category for i, category in enumerate(fy25_budget.index) if fy25_budget.iloc[i] / total_budget > threshold]

    ax.legend(legend_handles, legend_labels, title="Expense Categories", loc="best", frameon=False)

    plt.title('FY25 Budget Projections by Expense Category')

    # Save the figure as a PNG file
    plt.savefig(os.path.join(output_dir, 'fy25_budget_projections_by_expense_category.png'))
    plt.close(fig)

def generate_changes(path):
    # Load data
    df = pd.read_csv(path)
    spending_cols = ['FY22 Actual Expense', 'FY23 Actual Expense', 'FY24 Appropriation', 'FY25 Budget']

    # Ensure columns are numeric
    for col in spending_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop rows with missing values in spending columns
    df.dropna(subset=spending_cols, inplace=True)

    # Aggregate total spending over time by expense category
    spending_over_time = df.groupby('Expense Category')[spending_cols].sum().reset_index()

    # Reshape data for line plot (spending over time by category)
    spending_over_time = spending_over_time.melt(
        id_vars=['Expense Category'], 
        value_vars=spending_cols,
        var_name='Year', value_name='Amount'
    )

    # Plot configuration
    fig, ax = plt.subplots(figsize=(12, 8))
    for category, data in spending_over_time.groupby('Expense Category'):
        ax.plot(data['Year'], data['Amount'], marker='o', label=category)

    # Formatting for y-axis
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x):,}'))

    # Rotate x-axis labels
    plt.xticks(rotation=45)
    plt.title('Spending Over Time by Expense Category', fontsize=16)
    plt.xlabel('Year', fontsize=14)
    plt.ylabel('Amount ($)', fontsize=14)

    plt.legend(title='Expense Category', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Save the figure as a PNG file
    plt.savefig(os.path.join(output_dir, 'spending_over_time_by_expense_category.png'))
    plt.close(fig)

def main():
    # Provide the path to the CSV file
    path = "./data/fy25-adopted-operating-budget.csv"
    generate_visualization(path)
    generate_changes(path)

main()
