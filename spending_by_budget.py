import pandas as pd
import matplotlib.pyplot as plt

def general_visualization():
    # Create DataFrame
    df = pd.read_csv('path_to_file.csv')

    # Replace missing values ('#Missing') with NaN and convert to numeric
    df = df.replace('#Missing', pd.NA).apply(pd.to_numeric, errors='ignore')

    # Aggregate total spending for each program (across all years and categories)
    program_totals = df.groupby('Program')[['FY22 Actual Expense', 'FY23 Actual Expense', 
                                            'FY24 Appropriation', 'FY25 Budget']].sum().sum(axis=1)

    # Create a pie chart for total spending by program
    plt.figure(figsize=(8, 6))
    program_totals.plot(kind='pie', autopct='%1.1f%%', startangle=90, wedgeprops={'edgecolor': 'black'})
    plt.title('Total Spending by Program')
    plt.ylabel('')  # Hide the y-axis label
    plt.show()

    # Reshape data for line plot (spending over time by program)
    spending_over_time = df.melt(id_vars=['Program'], 
                                value_vars=['FY22 Actual Expense', 'FY23 Actual Expense', 
                                            'FY24 Appropriation', 'FY25 Budget'],
                                var_name='Year', value_name='Amount')

    # Drop rows with missing values
    spending_over_time.dropna(subset=['Amount'], inplace=True)

    # Create a line plot to show spending trends over time
    plt.figure(figsize=(10, 6))
    for program, data in spending_over_time.groupby('Program'):
        plt.plot(data['Year'], data['Amount'], marker='o', label=program)

    plt.title('Spending by Program Over Time')
    plt.xlabel('Year')
    plt.ylabel('Amount ($)')
    plt.legend(title='Program')
    plt.grid(True)
    plt.show()
    return