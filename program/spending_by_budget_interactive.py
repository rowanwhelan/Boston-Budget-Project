import pandas as pd
import plotly.express as px
import os

# Ensure the output directory exists
output_dir = './program/visualizations/'
os.makedirs(output_dir, exist_ok=True)

def generate_interactive_pie(path):
    # Load data
    df = pd.read_csv(path)

    # Handle missing values
    df = df.replace('#Missing', pd.NA).apply(pd.to_numeric, errors='ignore')

    # Aggregate FY25 budget by program
    fy25_budget = df.groupby('Program')['FY25 Budget'].sum()

    # Sort the programs by their FY25 budget in descending order
    fy25_budget = fy25_budget.sort_values(ascending=False)

    # Define a threshold for labeling (e.g., only label if > 2.5%)
    threshold = 0.025
    total_budget = fy25_budget.sum()

    # Add a column for budget percentage
    budget_data = fy25_budget.reset_index()
    budget_data['Percentage'] = budget_data['FY25 Budget'] / total_budget * 100

    # Filter labels based on the threshold
    budget_data['Label'] = budget_data.apply(
        lambda row: row['Program'] if row['Percentage'] > threshold * 100 else 'Other', axis=1
    )

    # Create the interactive pie chart
    fig = px.pie(
        budget_data,
        names='Label',
        values='FY25 Budget',
        title='FY25 Budget Projections by Program',
        color_discrete_sequence=px.colors.qualitative.Set3,
        hover_data={'Percentage': ':.2f'}
    )


    # Save as HTML
    fig.write_html(os.path.join(output_dir, 'budget_by_program_interactive_pie.html'))

    # Save as static image
    fig.write_image(os.path.join(output_dir, 'budget_by_program_interactive_pie.png'))

    # Show the figure in the notebook
    fig.show()

def generate_interactive_changes(path):
    # Load Data
    df = pd.read_csv(path)
    df['FY25 Budget'] = pd.to_numeric(df['FY25 Budget'], errors='coerce')
    df['FY24 Appropriation'] = pd.to_numeric(df['FY24 Appropriation'], errors='coerce')
    df['FY23 Actual Expense'] = pd.to_numeric(df['FY23 Actual Expense'], errors='coerce')
    df['FY22 Actual Expense'] = pd.to_numeric(df['FY22 Actual Expense'], errors='coerce')
    df = df.dropna(subset=['FY25 Budget', 'FY24 Appropriation', 'FY23 Actual Expense', 'FY22 Actual Expense'])

    # Aggregate Data for Top Programs
    top_programs = df.groupby('Program')['FY25 Budget'].sum().nlargest(10).index
    spending_over_time = df.melt(
        id_vars=['Program'], 
        value_vars=['FY22 Actual Expense', 'FY23 Actual Expense', 'FY24 Appropriation', 'FY25 Budget'],
        var_name='Year', value_name='Amount'
    )
    spending_over_time = spending_over_time[spending_over_time['Program'].isin(top_programs)]

    # Create Line Chart
    fig = px.line(
        spending_over_time, 
        x='Year', 
        y='Amount', 
        color='Program', 
        title="Top 10 Programs: Spending Over Time",
        markers=True,
        hover_data={'Amount': ':$,.2f'}
    )
    fig.update_yaxes(tickprefix="$", title="Spending Amount")
    fig.update_xaxes(title="Fiscal Year")

    # Save as HTML
    fig.write_html(os.path.join(output_dir, 'budget_by_program_over_time_interactive.html'))

    # Save as static image
    fig.write_image(os.path.join(output_dir, 'budget_by_program_over_time_interactive.png'))

    # Show the figure in the notebook
    fig.show()

def generate_interactive_volatile_changes(path):
    df = pd.read_csv(path)

    # Ensure spending columns are numeric
    for col in ['FY22 Actual Expense', 'FY23 Actual Expense', 'FY24 Appropriation', 'FY25 Budget']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df.dropna(subset=['FY22 Actual Expense', 'FY23 Actual Expense', 'FY24 Appropriation', 'FY25 Budget'], inplace=True)

    # Calculate Changes
    df_grouped = df.groupby('Program', as_index=False).sum()
    df_grouped['Change_22_23'] = df_grouped['FY23 Actual Expense'] - df_grouped['FY22 Actual Expense']
    df_grouped['Change_23_24'] = df_grouped['FY24 Appropriation'] - df_grouped['FY23 Actual Expense']
    df_grouped['Change_24_25'] = df_grouped['FY25 Budget'] - df_grouped['FY24 Appropriation']
    df_grouped['Total_Change'] = df_grouped[['Change_22_23', 'Change_23_24', 'Change_24_25']].abs().sum(axis=1)
    top_programs = df_grouped.nlargest(10, 'Total_Change')['Program']

    # Reshape Data
    change_data = df_grouped.melt(
        id_vars=['Program'], 
        value_vars=['Change_22_23', 'Change_23_24', 'Change_24_25'], 
        var_name='Change_Year', value_name='Change_Amount'
    )
    change_data = change_data[change_data['Program'].isin(top_programs)]

    # Create Line Chart
    fig = px.line(
        change_data, 
        x='Change_Year', 
        y='Change_Amount', 
        color='Program', 
        title="Top 10 Programs: Spending Change Over Time",
        markers=True,
        hover_data={'Change_Amount': ':$,.2f'}
    )
    fig.update_yaxes(tickprefix="$", title="Change Amount")
    fig.update_xaxes(title="Year-to-Year Change")

    # Save as HTML
    fig.write_html(os.path.join(output_dir, 'program_budget_by_volatile_changes_interactive.html'))

    # Save as static image
    fig.write_image(os.path.join(output_dir, 'program_budget_by_volatile_changes_interactive.png'))

    # Show the figure in the notebook
    fig.show()



def main():
    # Provide the path to the CSV file
    path = "./data/fy25-adopted-operating-budget.csv"
    generate_interactive_pie(path)
    generate_interactive_changes(path)
    generate_interactive_volatile_changes(path)


main()