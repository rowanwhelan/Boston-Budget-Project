import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

def generate_visualization(path):
    # Create DataFrame
    df = pd.read_csv(path)

    # Handle missing values
    df = df.replace('#Missing', pd.NA).apply(pd.to_numeric, errors='ignore')

    # Aggregate FY25 budget by program
    fy25_budget = df.groupby('Program')['FY25 Budget'].sum()

    # Sort the programs by their FY25 budget in descending order
    fy25_budget = fy25_budget.sort_values(ascending=False)

    # Define a threshold for labeling (e.g., only label if > 5%)
    threshold = 0.025  # 5%
    total_budget = fy25_budget.sum()

    # Create a color list: essential slices get unique colors, others get black
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
        autopct=lambda p: f'{p:.1f}%' if p > threshold * 100 else '',  # Only large portions get labels
    )

    # Suppress text for smaller slices
    for i, (text, wedge) in enumerate(zip(texts, wedges)):
        if fy25_budget.iloc[i] / total_budget <= threshold:
            text.set_text('')  # Remove label for non-essential slices

    # Create the legend using the wedge handles
    legend_handles = [
        wedge for i, wedge in enumerate(wedges)
        if fy25_budget.iloc[i] / total_budget > threshold
    ]

    legend_labels = [
        program for i, program in enumerate(fy25_budget.index)
        if fy25_budget.iloc[i] / total_budget > threshold
    ]

    ax.legend(legend_handles, legend_labels, title="Programs", loc="best", frameon=False)

    plt.title('FY25 Budget Projections by Program')
    plt.show()
    return

def generate_changes(path):
    # Create DataFrame
    df = pd.read_csv(path)
    df['FY25 Budget'] = pd.to_numeric(df['FY25 Budget'], errors='coerce')
    df['FY24 Appropriation'] = pd.to_numeric(df['FY24 Appropriation'], errors='coerce')
    df['FY23 Actual Expense'] = pd.to_numeric(df['FY23 Actual Expense'], errors='coerce')
    df['FY22 Actual Expense'] = pd.to_numeric(df['FY22 Actual Expense'], errors='coerce')

    # Drop rows with NaN values in 'FY25 Budget'
    df = df.dropna(subset=['FY25 Budget','FY24 Appropriation', 'FY23 Actual Expense', 'FY22 Actual Expense'])
    # Aggregate total spending for FY25 to highlight top programs
      # Aggregate FY25 spending to find the top 10 programs
    top_programs = df.groupby('Program')['FY25 Budget'].sum().nlargest(10).index

    # Reshape data for line plot (spending over time by program)
    spending_over_time = df.melt(
        id_vars=['Program'], 
        value_vars=['FY22 Actual Expense', 'FY23 Actual Expense', 
                    'FY24 Appropriation', 'FY25 Budget'],
        var_name='Year', value_name='Amount'
    )

    # Drop rows with missing values
    spending_over_time.dropna(subset=['Amount'], inplace=True)

    # Group by program and year to sum amounts
    spending_over_time = spending_over_time.groupby(
        ['Program', 'Year'], as_index=False
    ).sum()

    # Ensure 'Year' is treated as an ordered categorical variable
    spending_over_time['Year'] = pd.Categorical(
        spending_over_time['Year'], 
        categories=['FY22 Actual Expense', 'FY23 Actual Expense', 
                    'FY24 Appropriation', 'FY25 Budget'], 
        ordered=True
    )

    # Filter to only include the top 10 programs
    filtered_data = spending_over_time[spending_over_time['Program'].isin(top_programs)]

    # Plot configuration
    plt.figure(figsize=(12, 8))
    for program, data in filtered_data.groupby('Program'):
        plt.plot(data['Year'], data['Amount'], marker='o', label=program)

    # Use integer formatting on y-axis to avoid scientific notation
    def int_formatter(x, _):
        return f'{int(x):,}'  # Adds commas for readability

    plt.gca().yaxis.set_major_formatter(FuncFormatter(int_formatter))

    # Adjust y-axis to give extra space (10% padding)
    y_max = filtered_data['Amount'].max() * 1.1
    plt.ylim(0, y_max)

    # Rotate x-axis labels for readability
    plt.xticks(rotation=45)

    # Add title and labels
    plt.title('Top 10 Programs: Spending Over Time', fontsize=16)
    plt.xlabel('Year', fontsize=14)
    plt.ylabel('Amount ($)', fontsize=14)

    # Move the legend outside the plot
    plt.legend(title='Program', bbox_to_anchor=(1.05, 1), loc='upper left')

    # Add grid for better visualization
    plt.grid(True, linestyle='--', alpha=0.7)

    # Display the plot with tight layout
    plt.tight_layout()
    plt.show()

def main():
    generate_visualization("./data/fy25-adopted-operating-budget.csv")
    #generate_changes("./data/fy25-adopted-operating-budget.csv")
    

main()