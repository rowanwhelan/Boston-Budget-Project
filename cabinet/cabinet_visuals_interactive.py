import pandas as pd
import plotly 
import plotly.express as px
import os

# Ensure the output directory exists
output_dir = './cabinet/visualizations/'
os.makedirs(output_dir, exist_ok=True)

def generate_visualization(path):
    # Load the data
    df = pd.read_csv(path)

    # Ensure spending columns are numeric
    df = df.replace('#Missing', pd.NA).apply(pd.to_numeric, errors='ignore')

    # Aggregate FY25 budget by cabinet
    fy25_budget = df.groupby('Cabinet')['FY25 Budget'].sum()

    # Sort the cabinets by their FY25 budget in descending order
    fy25_budget = fy25_budget.sort_values(ascending=False)

    # Create the interactive pie chart
    fig = px.pie(
        values=fy25_budget,
        names=fy25_budget.index,
        title='FY25 Budget Projections by Cabinet',
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    fig.update_traces(textinfo='label+percent', hoverinfo='label+value+percent')

    # save as html too
    fig.write_html(os.path.join(output_dir, 'fy25_budget_projections_by_cabinet_interactive.html'))
    # Save the chart as a PNG file
    fig.write_image(os.path.join(output_dir, 'fy25_budget_projections_by_cabinet_interactive.png'))

    fig.show()

def generate_changes(path):
    # Load data
    df = pd.read_csv(path)
    spending_cols = ['FY22 Actual Expense', 'FY23 Actual Expense', 'FY24 Appropriation', 'FY25 Budget']

    # Ensure columns are numeric
    for col in spending_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop rows with missing values in spending columns
    df.dropna(subset=spending_cols, inplace=True)

    # Aggregate total spending over time by cabinet
    spending_over_time = df.groupby('Cabinet')[spending_cols].sum().reset_index()

    # Reshape data for line plot (spending over time by cabinet)
    spending_over_time = spending_over_time.melt(
        id_vars=['Cabinet'], 
        value_vars=spending_cols,
        var_name='Year', value_name='Amount'
    )

    # Create the interactive line chart
    fig = px.line(
        spending_over_time,
        x='Year',
        y='Amount',
        color='Cabinet',
        title='Spending Over Time by Cabinet',
        labels={'Amount': 'Amount ($)', 'Year': 'Year'}
    )
    fig.update_traces(mode='lines+markers', hovertemplate='%{x}: $%{y:,}')

    # save as html too
    fig.write_html(os.path.join(output_dir, 'spending_over_time_by_cabinet_interactive.html'))
    # Save the chart as a PNG file
    fig.write_image(os.path.join(output_dir, 'spending_over_time_by_cabinet_interactive.png'))

    fig.show()

def main():
    # Provide the path to the CSV file
    path = "./data/fy25-adopted-operating-budget.csv"
    generate_visualization(path)
    generate_changes(path)

main()