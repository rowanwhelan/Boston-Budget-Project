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


def main():
    # Provide the path to the CSV file
    path = "./data/fy25-adopted-operating-budget.csv"
    generate_interactive_pie(path)


main()