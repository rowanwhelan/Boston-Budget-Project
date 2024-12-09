import pandas as pd
import plotly.express as px
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

    # Convert to DataFrame for Plotly
    fy25_budget_df = fy25_budget.reset_index()
    fy25_budget_df.columns = ['Expense Category', 'FY25 Budget']

    # Create pie chart
    fig = px.pie(
        fy25_budget_df,
        values='FY25 Budget',
        names='Expense Category',
        title='FY25 Budget Projections by Expense Category',
        color_discrete_sequence=px.colors.qualitative.Plotly,
        hole=0.4  # Optional for a donut chart
    )

    # Save as HTML
    fig.write_html(os.path.join(output_dir, 'interactive_fy25_budget_pie_chart.html'))

    # Save as static image
    fig.write_image(os.path.join(output_dir, 'fy25_budget_pie_chart.png'))

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

    # Create line plot
    fig = px.line(
        spending_over_time,
        x='Year',
        y='Amount',
        color='Expense Category',
        title='Spending Over Time by Expense Category',
        markers=True
    )
    fig.update_yaxes(title='Amount ($)', tickformat=',')
    fig.update_xaxes(title='Year')

    # Save as HTML
    fig.write_html(os.path.join(output_dir, 'interactive_spending_over_time.html'))

    # Save as static image
    fig.write_image(os.path.join(output_dir, 'spending_over_time.png'))

def main():
    # Provide the path to the CSV file
    path = "./data/fy25-adopted-operating-budget.csv"
    generate_visualization(path)
    generate_changes(path)

main()