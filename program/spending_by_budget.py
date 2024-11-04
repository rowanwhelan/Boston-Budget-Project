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
    return
    
def generate_volatile_changes(path):
     # Create DataFrame
    df = pd.read_csv(path)

    # Ensure spending columns are numeric
    for col in ['FY22 Actual Expense', 'FY23 Actual Expense', 'FY24 Appropriation', 'FY25 Budget']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop rows with missing values in critical columns
    df.dropna(subset=['FY22 Actual Expense', 'FY23 Actual Expense', 'FY24 Appropriation', 'FY25 Budget'], inplace=True)

    # Aggregate spending by program (sum amounts for programs with multiple entries)
    df_grouped = df.groupby('Program', as_index=False).sum()

    # Calculate year-over-year changes for each program
    df_grouped['Change_22_23'] = df_grouped['FY23 Actual Expense'] - df_grouped['FY22 Actual Expense']
    df_grouped['Change_23_24'] = df_grouped['FY24 Appropriation'] - df_grouped['FY23 Actual Expense']
    df_grouped['Change_24_25'] = df_grouped['FY25 Budget'] - df_grouped['FY24 Appropriation']

    # Sum the absolute changes for each program to determine total change
    df_grouped['Total_Change'] = df_grouped[
        ['Change_22_23', 'Change_23_24', 'Change_24_25']
    ].abs().sum(axis=1)

    # Get the top 10 programs by total change
    top_programs = df_grouped.nlargest(10, 'Total_Change')['Program']

    # Reshape data for plotting
    change_data = df_grouped.melt(
        id_vars=['Program'], 
        value_vars=['Change_22_23', 'Change_23_24', 'Change_24_25'], 
        var_name='Change_Year', value_name='Change_Amount'
    )

    # Filter to include only the top 10 programs
    change_data = change_data[change_data['Program'].isin(top_programs)]

    # Ensure 'Change_Year' is ordered correctly
    change_data['Change_Year'] = pd.Categorical(
        change_data['Change_Year'], 
        categories=['Change_22_23', 'Change_23_24', 'Change_24_25'], 
        ordered=True
    )

    # Plot the data
    plt.figure(figsize=(12, 8))
    for program, data in change_data.groupby('Program'):
        plt.plot(data['Change_Year'], data['Change_Amount'], marker='o', label=program)

    # Use integer formatting for y-axis
    def int_formatter(x, _):
        return f'{int(x):,}'  # Adds commas for readability

    plt.gca().yaxis.set_major_formatter(FuncFormatter(int_formatter))

    # Adjust y-axis for better readability
    y_min, y_max = change_data['Change_Amount'].min(), change_data['Change_Amount'].max()
    plt.ylim(y_min * 1.1, y_max * 1.1)  # Add padding to the range

    # Rotate x-axis labels for readability
    plt.xticks(rotation=45)

    # Add title and axis labels
    plt.title('Top 10 Programs: Spending Change Over Time', fontsize=16)
    plt.xlabel('Year-to-Year Change', fontsize=14)
    plt.ylabel('Change Amount ($)', fontsize=14)

    # Move the legend outside the plot for better readability
    plt.legend(title='Program', bbox_to_anchor=(1.05, 1), loc='upper left')

    # Add grid for better visualization
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Find the top 10 most volatile programs (by absolute change)
    #top_volatile = df_grouped.iloc[df_grouped['Total_Change'].abs().nlargest(10).index]

    # Print the most volatile programs and their change values
    #print("\nTop 10 Most Volatile Programs (by absolute change):")
    p#rint(top_volatile[['Program', 'Total_Change']])

    # Display the plot with a tight layout
    plt.tight_layout()
    plt.show()
    return

def generate_stable_changes(path):
    # Create DataFrame
    df = pd.read_csv(path)

    # Ensure spending columns are numeric
    for col in ['FY22 Actual Expense', 'FY23 Actual Expense', 'FY24 Appropriation', 'FY25 Budget']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop rows with missing values in critical columns
    df.dropna(subset=['FY22 Actual Expense', 'FY23 Actual Expense', 'FY24 Appropriation', 'FY25 Budget'], inplace=True)

    # Aggregate spending by program (sum amounts for programs with multiple entries)
    df_grouped = df.groupby('Program', as_index=False).sum()

    # Calculate year-over-year changes for each program
    df_grouped['Change_22_23'] = df_grouped['FY23 Actual Expense'] - df_grouped['FY22 Actual Expense']
    df_grouped['Change_23_24'] = df_grouped['FY24 Appropriation'] - df_grouped['FY23 Actual Expense']
    df_grouped['Change_24_25'] = df_grouped['FY25 Budget'] - df_grouped['FY24 Appropriation']

    # Sum the absolute changes for each program to determine total change
    df_grouped['Total_Change'] = df_grouped[
        ['Change_22_23', 'Change_23_24', 'Change_24_25']
    ].abs().sum(axis=1)

    # Get the 10 least volatile programs (smallest total change)
    least_volatile_programs = df_grouped.nsmallest(10, 'Total_Change')['Program']

    # Reshape data for plotting
    change_data = df_grouped.melt(
        id_vars=['Program'], 
        value_vars=['Change_22_23', 'Change_23_24', 'Change_24_25'], 
        var_name='Change_Year', value_name='Change_Amount'
    )

    # Filter to include only the least volatile programs
    change_data = change_data[change_data['Program'].isin(least_volatile_programs)]

    # Ensure 'Change_Year' is ordered correctly
    change_data['Change_Year'] = pd.Categorical(
        change_data['Change_Year'], 
        categories=['Change_22_23', 'Change_23_24', 'Change_24_25'], 
        ordered=True
    )

    # Plot the data
    plt.figure(figsize=(12, 8))
    for program, data in change_data.groupby('Program'):
        plt.plot(data['Change_Year'], data['Change_Amount'], marker='o', label=program)

    # Use integer formatting for y-axis
    def int_formatter(x, _):
        return f'{int(x):,}'  # Adds commas for readability

    plt.gca().yaxis.set_major_formatter(FuncFormatter(int_formatter))

    # Adjust y-axis for better readability
    y_min, y_max = change_data['Change_Amount'].min(), change_data['Change_Amount'].max()
    plt.ylim(y_min * 1.1, y_max * 1.1)  # Add padding to the range

    # Rotate x-axis labels for readability
    plt.xticks(rotation=45)

    # Add title and axis labels
    plt.title('10 Least Volatile Programs: Spending Change Over Time', fontsize=16)
    plt.xlabel('Year-to-Year Change', fontsize=14)
    plt.ylabel('Change Amount ($)', fontsize=14)

    # Move the legend outside the plot for better readability
    plt.legend(title='Program', bbox_to_anchor=(1.05, 1), loc='upper left')

    # Add grid for better visualization
    plt.grid(True, linestyle='--', alpha=0.7)
    
     # Find the top 10 least volatile programs (changes closest to zero)
    #least_volatile = df_grouped.iloc[df_grouped['Total_Change'].abs().nsmallest(10).index]

    # Print the least volatile programs and their change values
    #print("\nTop 10 Least Volatile Programs (by change closest to zero):")
    #print(least_volatile[['Program', 'Total_Change']])

    # Display the plot with a tight layout
    plt.tight_layout()
    plt.show()
    
def generate_combined_changes(path):
    # Create DataFrame
    df = pd.read_csv(path)

    # Ensure spending columns are numeric
    for col in ['FY22 Actual Expense', 'FY23 Actual Expense', 'FY24 Appropriation', 'FY25 Budget']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop rows with missing values in critical columns
    df.dropna(subset=['FY22 Actual Expense', 'FY23 Actual Expense', 'FY24 Appropriation', 'FY25 Budget'], inplace=True)

    # Aggregate spending by program (sum amounts for programs with multiple entries)
    df_grouped = df.groupby('Program', as_index=False).sum()

    # Calculate year-over-year changes for each program
    df_grouped['Change_22_23'] = df_grouped['FY23 Actual Expense'] - df_grouped['FY22 Actual Expense']
    df_grouped['Change_23_24'] = df_grouped['FY24 Appropriation'] - df_grouped['FY23 Actual Expense']
    df_grouped['Change_24_25'] = df_grouped['FY25 Budget'] - df_grouped['FY24 Appropriation']

    # Sum the absolute changes for each program to determine total change
    df_grouped['Total_Change'] = df_grouped[
        ['Change_22_23', 'Change_23_24', 'Change_24_25']
    ].abs().sum(axis=1)

    # Get the 10 least and most volatile programs
    least_volatile_programs = df_grouped.nsmallest(10, 'Total_Change')['Program']
    most_volatile_programs = df_grouped.nlargest(10, 'Total_Change')['Program']

    # Reshape data for plotting
    change_data = df_grouped.melt(
        id_vars=['Program'], 
        value_vars=['Change_22_23', 'Change_23_24', 'Change_24_25'], 
        var_name='Change_Year', value_name='Change_Amount'
    )

    # Filter data for least and most volatile programs
    least_volatile_data = change_data[change_data['Program'].isin(least_volatile_programs)]
    most_volatile_data = change_data[change_data['Program'].isin(most_volatile_programs)]

    # Ensure 'Change_Year' is ordered correctly
    change_data['Change_Year'] = pd.Categorical(
        change_data['Change_Year'], 
        categories=['Change_22_23', 'Change_23_24', 'Change_24_25'], 
        ordered=True
    )

    # Plot the data
    plt.figure(figsize=(12, 8))

    # Plot least volatile programs with one style
    for program, data in least_volatile_data.groupby('Program'):
        plt.plot(data['Change_Year'], data['Change_Amount'], marker='o', linestyle='-', label=f'{program} (Stable)')

    # Plot most volatile programs with a different style
    for program, data in most_volatile_data.groupby('Program'):
        plt.plot(data['Change_Year'], data['Change_Amount'], marker='x', linestyle='--', label=f'{program} (Volatile)')

    # Use integer formatting for y-axis
    def int_formatter(x, _):
        return f'{int(x):,}'  # Adds commas for readability

    plt.gca().yaxis.set_major_formatter(FuncFormatter(int_formatter))

    # Adjust y-axis for better readability
    y_min, y_max = change_data['Change_Amount'].min(), change_data['Change_Amount'].max()
    plt.ylim(y_min * 1.1, y_max * 1.1)  # Add padding to the range

    # Rotate x-axis labels for readability
    plt.xticks(rotation=45)

    # Add title and axis labels
    plt.title('Comparison of Volatile vs Stable Programs: Spending Change Over Time', fontsize=16)
    plt.xlabel('Year-to-Year Change', fontsize=14)
    plt.ylabel('Change Amount ($)', fontsize=14)

    # Move the legend outside the plot for better readability
    plt.legend(title='Program', bbox_to_anchor=(1.05, 1), loc='upper left')

    # Add grid for better visualization
    plt.grid(True, linestyle='--', alpha=0.7)

    # Display the plot with a tight layout
    plt.tight_layout()
    plt.show()
    return

def main():
    #generate_visualization("./data/fy25-adopted-operating-budget.csv")
    #generate_changes("./data/fy25-adopted-operating-budget.csv")
    #generate_volatile_changes("./data/fy25-adopted-operating-budget.csv")
    #generate_stable_changes("./data/fy25-adopted-operating-budget.csv")
    #generate_combined_changes("./data/fy25-adopted-operating-budget.csv")
    pass

main()