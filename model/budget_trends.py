import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Step 1: Load and Preprocess the Data
def preprocess_data(data):
    # Reshape data to long format
    data_long = data.melt(
        id_vars=['Cabinet', 'Dept', 'Program', 'Expense Category'],
        var_name='year',
        value_name='expense'
    )

    # Extract year and clean column names
    data_long['year'] = data_long['year'].str.extract(r'(FY\d{2})').apply(lambda x: '20' + x[0][2:], axis=1)
    data_long['year'] = pd.to_datetime(data_long['year'], format='%Y')
    
    # Create the 'year_numeric' column as the year integer
    data_long['year_numeric'] = data_long['year'].dt.year

    # Handle non-numeric values in the expense column
    data_long['expense'] = pd.to_numeric(data_long['expense'], errors='coerce')

    # Fill missing values with interpolation
    data_long = data_long.sort_values(by=['Expense Category', 'year']).groupby('Expense Category').apply(
        lambda group: group.interpolate(method='linear')
    ).reset_index(drop=True)

    return data_long

# Step 2: Analyze Trends with Prophet and Add Context
def analyze_trends(data, category):
    category_data = data[data['Expense Category'] == category]
    
    # Prepare the data for Prophet
    prophet_data = category_data[['year', 'expense']].rename(columns={'year': 'ds', 'expense': 'y'})

    # Initialize and fit the Prophet model
    model = Prophet()
    model.fit(prophet_data)

    # Create a future dataframe to predict the next 5 years
    future = model.make_future_dataframe(periods=5, freq='Y')  
    forecast = model.predict(future)

    # Plot the results
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot the actual data
    ax.plot(prophet_data['ds'], prophet_data['y'], label='Actual Data', color='blue', marker='o')

    # Plot the forecasted data (future)
    ax.plot(forecast['ds'], forecast['yhat'], label='Predicted Data', linestyle='--', color='red')
    ax.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color='red', alpha=0.2, label='Confidence Interval')

    # Set the title and labels
    ax.set_title(f"Expense Trend Analysis for {category}", fontsize=16)
    ax.set_xlabel('Year', fontsize=14)
    ax.set_ylabel('Expense', fontsize=14)

    # Add a legend
    ax.legend()

    # Display grid for better readability
    ax.grid(True)

    # Show the plot
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    return forecast

# Step 3: Prepare Data for Gradient Boosting Model
def prepare_data_for_gbm(data, category):
    category_data = data[data['Expense Category'] == category]
    category_data = category_data.sort_values(by='year').reset_index(drop=True)

    for i in range(1, 4):
        category_data[f'lag_{i}'] = category_data['expense'].shift(i)

    category_data.dropna(inplace=True)

    X = category_data[['year'] + [f'lag_{i}' for i in range(1, 4)]].copy()
    X['year_numeric'] = X['year'].dt.year
    X.drop(columns='year', inplace=True)
    y = category_data['expense']

    return train_test_split(X, y, test_size=0.2, random_state=42)

# Step 4: Train Gradient Boosting Model
def train_gbm(X_train, X_test, y_train, y_test):
    model = GradientBoostingRegressor(random_state=42)
    model.fit(X_train, y_train)
    
    # Store feature names for validation
    model.feature_names_in_ = X_train.columns.to_list()

    y_pred = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    print(f"RMSE: {rmse}")

    return model

# Step 5: Visualization with Interactive Plotly
def visualize_predictions_interactive(data, model, category):
    category_data = data[data['Expense Category'] == category].sort_values(by='year').reset_index(drop=True)

    # Generate lag features as before
    for i in range(1, 4):
        category_data[f'lag_{i}'] = category_data['expense'].shift(i)
    category_data.dropna(inplace=True)
    
    X = category_data[['lag_1', 'lag_2', 'lag_3', 'year_numeric']]

    # Validate feature names match
    if list(X.columns) != model.feature_names_in_:
        raise ValueError("Feature names during prediction do not match those during training.")
    
    # Add predictions to the DataFrame
    category_data['predicted'] = model.predict(X)

    # Create the interactive plot using Plotly
    fig = px.line(category_data,
                  x='year_numeric',  # Use the 'year_numeric' column
                  y=['expense', 'predicted'],  # Plot actual vs predicted expense
                  labels={'expense': 'Actual Expense', 'predicted': 'Predicted Expense'},
                  title=f'Actual vs Predicted Expenses for {category}',
                  line_shape='linear')

    # Add interactivity: highlight a point when clicked
    fig.update_traces(mode='lines+markers', marker=dict(size=6))
    fig.update_layout(title=f'Interactive Expense Trend Analysis for {category}',
                      xaxis_title='Year',
                      yaxis_title='Expense',
                      template='plotly_dark')  # Optional, for a dark theme

    # Show the plot
    fig.show()

# Main Workflow
def main_workflow(data):
    # Preprocess data
    data = preprocess_data(data)

    categories = data['Expense Category'].unique()

    for category in categories:
        print(f"Processing category: {category}")

        # Analyze trends using Prophet
        analyze_trends(data, category)

        # Prepare data for Gradient Boosting Model
        X_train, X_test, y_train, y_test = prepare_data_for_gbm(data, category)

        # Train the Gradient Boosting Model
        model = train_gbm(X_train, X_test, y_train, y_test)

        # Visualize predictions
        visualize_predictions_interactive(data, model, category)

# Example usage (replace 'data.csv' with your file)
data = pd.read_csv('data/fy25-adopted-operating-budget.csv')
main_workflow(data)
