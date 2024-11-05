import os
import pandas as pd

def generate_report(path):
    # Load the data
    df = pd.read_csv(path)

    # Ensure spending columns are numeric
    spending_cols = ['FY22 Actual Expense', 'FY23 Actual Expense', 
                     'FY24 Appropriation', 'FY25 Budget']
    for col in spending_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop rows with missing values in spending columns
    df.dropna(subset=spending_cols, inplace=True)

    # Aggregate spending by expense category (sum amounts for categories with multiple entries)
    df_grouped = df.groupby('Expense Category', as_index=False).sum()

    # General Statistics
    num_categories = df_grouped['Expense Category'].nunique()
    total_spending = df_grouped[spending_cols].sum().sum()
    avg_spending = df_grouped[spending_cols].mean().mean()
    std_spending = df_grouped[spending_cols].std().mean()

    # Per-category statistics
    category_sums = df_grouped.set_index('Expense Category')[spending_cols].sum(axis=1)
    highest_spending_category = category_sums.idxmax()
    highest_spending_amount = category_sums.max()
    lowest_spending_category = category_sums.idxmin()
    lowest_spending_amount = category_sums.min()

    # Extract basic spending stats for each year
    year_stats = {}
    for col in spending_cols:
        year_stats[col] = {
            'total': df_grouped[col].sum(),
            'mean': df_grouped[col].mean(),
            'std': df_grouped[col].std(),
            'min': df_grouped[col].min(),
            'max': df_grouped[col].max()
        }

    # List all expense categories
    all_categories = df_grouped['Expense Category'].tolist()

    # Write Results to a Text File
    with open('./expenseCategory/expenseCategory_report.txt', 'w') as file:
        file.write("===== General Expense Category Statistics =====\n")
        file.write(f"Total Number of Categories: {num_categories}\n")
        file.write(f"Total Spending (All Years): ${total_spending:,.2f}\n")
        file.write(f"Average Spending per Category: ${avg_spending:,.2f}\n")
        file.write(f"Standard Deviation in Spending: ${std_spending:,.2f}\n")

        file.write("\n===== Highest and Lowest Spending Categories =====\n")
        file.write(f"Highest Spending Category: {highest_spending_category} (${highest_spending_amount:,.2f})\n")
        file.write(f"Lowest Spending Category: {lowest_spending_category} (${lowest_spending_amount:,.2f})\n")

        file.write("\n===== Year-wise Spending Statistics =====\n")
        for year, stats in year_stats.items():
            file.write(f"\n{year}:\n")
            file.write(f"  Total: ${stats['total']:,.2f}\n")
            file.write(f"  Mean: ${stats['mean']:,.2f}\n")
            file.write(f"  Std Dev: ${stats['std']:,.2f}\n")
            file.write(f"  Min: ${stats['min']:,.2f}\n")
            file.write(f"  Max: ${stats['max']:,.2f}\n")

        file.write("\n===== List of All Expense Categories =====\n")
        for category in all_categories:
            file.write(f"- {category}\n")

        file.write("\n===== End of Report =====\n")
    return 1

def main():
    generate_report("./data/fy25-adopted-operating-budget.csv")

def test_expenseCategory():
    # Path to the data file
    path = "./data/fy25-adopted-operating-budget.csv"
    
    # Run the report generation
    result = generate_report(path)  # Directly calling generate_report if it returns something

    # Example assertion if generate_report returns a result like a DataFrame
    assert result is not None, "Expected generate_report to return a non-None result"
    
    # If generate_report creates an output file, check for its existence
    output_path = "./expenseCategory/expenseCategory_report.txt"  # Replace with the actual output path if known
    assert os.path.exists(output_path), f"Expected output file at {output_path}"
    
    # Clean up: Optionally, remove the output file after the test if necessary
    if os.path.exists(output_path):
        os.remove(output_path)