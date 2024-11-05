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

    # Aggregate spending by cabinet (sum amounts for cabinets with multiple entries)
    df_grouped = df.groupby('Cabinet', as_index=False).sum()

    # General Statistics
    num_cabinets = df_grouped['Cabinet'].nunique()
    total_spending = df_grouped[spending_cols].sum().sum()
    avg_spending = df_grouped[spending_cols].mean().mean()
    std_spending = df_grouped[spending_cols].std().mean()

    # Per-cabinet statistics
    cabinet_sums = df_grouped.set_index('Cabinet')[spending_cols].sum(axis=1)
    highest_spending_cabinet = cabinet_sums.idxmax()
    highest_spending_amount = cabinet_sums.max()
    lowest_spending_cabinet = cabinet_sums.idxmin()
    lowest_spending_amount = cabinet_sums.min()

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

    # List all cabinets
    all_cabinets = df_grouped['Cabinet'].tolist()

    # Write Results to a Text File
    with open('./cabinet/cabinet_report.txt', 'w') as file:
        file.write("===== General Cabinet Statistics =====\n")
        file.write(f"Total Number of Cabinets: {num_cabinets}\n")
        file.write(f"Total Spending (All Years): ${total_spending:,.2f}\n")
        file.write(f"Average Spending per Cabinet: ${avg_spending:,.2f}\n")
        file.write(f"Standard Deviation in Spending: ${std_spending:,.2f}\n")

        file.write("\n===== Highest and Lowest Spending Cabinets =====\n")
        file.write(f"Highest Spending Cabinet: {highest_spending_cabinet} (${highest_spending_amount:,.2f})\n")
        file.write(f"Lowest Spending Cabinet: {lowest_spending_cabinet} (${lowest_spending_amount:,.2f})\n")

        file.write("\n===== Year-wise Spending Statistics =====\n")
        for year, stats in year_stats.items():
            file.write(f"\n{year}:\n")
            file.write(f"  Total: ${stats['total']:,.2f}\n")
            file.write(f"  Mean: ${stats['mean']:,.2f}\n")
            file.write(f"  Std Dev: ${stats['std']:,.2f}\n")
            file.write(f"  Min: ${stats['min']:,.2f}\n")
            file.write(f"  Max: ${stats['max']:,.2f}\n")

        file.write("\n===== List of All Cabinets =====\n")
        for cabinet in all_cabinets:
            file.write(f"- {cabinet}\n")

        file.write("\n===== End of Report =====\n")
        return
    

def main():
    # Provide the path to the CSV file
    path = "./data/fy25-adopted-operating-budget.csv"
    generate_report(path)

def test_cabinet():
    main()
    