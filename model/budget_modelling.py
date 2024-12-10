import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def preprocess_data(data):
    # Melt the wide-format DataFrame into long format for easier analysis
    data_long = data.melt(id_vars=["Variable", "Year"], 
                          var_name="City", 
                          value_name="Budget")
    
    # Remove commas from the Budget column and convert to numeric
    data_long["Budget"] = data_long["Budget"].replace(",", "", regex=True).astype(float)
    
    # Handle missing values by forward-filling or interpolation
    data_long["Budget"] = data_long["Budget"].fillna(method="ffill")
    data_long["Budget"] = data_long["Budget"].fillna(method="bfill")
    data_long.dropna(inplace=True)
    
    # Ensure Year is numeric for time-series modeling
    data_long["Year"] = pd.to_numeric(data_long["Year"])
    
    return data_long

# Step 2: Interactive Graph to Filter City Trends
def interactive_city_trends(data):
    # Create a Plotly interactive line chart
    fig = px.line(
        data,
        x="Year",
        y="Budget",
        color="Variable",
        facet_col="City",
        facet_col_wrap=3,  # Wrap after 3 columns
        labels={"Budget": "Budget (in USD)", "Variable": "Category", "Year": "Year"},
        title="City Budgets Over Time by Variable"
    )
    
    # Add interactivity
    fig.update_traces(mode="lines+markers")
    fig.update_layout(
        height=800,
        hovermode="closest",
        title_font_size=18
    )
    
    fig.show()

# Step 3: Analyze Trends with Prophet and Add Context
def analyze_trends(data, category):
    # Filter data for the selected category (City)
    city_data = data[data["City"] == category]
    
    # Prepare the data for Prophet
    prophet_data = city_data[["Year", "Budget"]].rename(columns={"Year": "ds", "Budget": "y"})
    
    # Fit the Prophet model
    model = Prophet()
    model.fit(prophet_data)
    
    # Create future DataFrame and forecast
    future = model.make_future_dataframe(periods=5, freq='Y')
    forecast = model.predict(future)
    
    # Plot forecast
    fig = model.plot(forecast)
    plt.title(f"Trend Analysis for {category}")
    plt.show()
    
    return forecast

# Step 4: Prepare Data for Gradient Boosting Model
def prepare_data_for_gbm(data, category):
    # Filter for the chosen city
    city_data = data[data["City"] == category].copy()  # Explicitly create a copy
    
    # Create lag features for budget values to use as predictors
    city_data.loc[:, "Lag1"] = city_data["Budget"].shift(1)
    city_data.loc[:, "Lag2"] = city_data["Budget"].shift(2)
    city_data.dropna(inplace=True)
    
    # Split into features and target
    X = city_data[["Lag1", "Lag2"]]
    y = city_data["Budget"]
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    return X_train, X_test, y_train, y_test

# Step 5: Train Gradient Boosting Model
# Important: The predictions from this model should be used to predict the budget for Boston MA in 2025. 
# This data is in a separate file and the comparison between machine predictions and actual data will be informative
def train_gbm(X_train, X_test, y_train, y_test):
    # Initialize and train the model
    model = GradientBoostingRegressor(random_state=42)
    model.fit(X_train, y_train)
    
    # Make predictions and evaluate
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f"Mean Squared Error: {mse}")
    
    return model

def visualize_predictions_interactive(data, model):
    # Ensure data includes predictions for all cities
    data = data.copy()
    data["Lag1"] = data.groupby("City")["Budget"].shift(1)
    data["Lag2"] = data.groupby("City")["Budget"].shift(2)
    data.dropna(inplace=True)
    data["Predicted"] = model.predict(data[["Lag1", "Lag2"]])

    # Initialize lists for city buttons, variable buttons
    unique_cities = data["City"].unique()
    unique_variables = data["Variable"].unique()

    # Create a subplot with 2 rows and 3 columns (6 cities)
    fig = make_subplots(
        rows=2, cols=3,
        subplot_titles=[f"City {city}" for city in unique_cities],
        shared_xaxes=True, shared_yaxes=True
    )

    # Variable to store the trace references
    traces = []

    # Create traces for each (city, variable) combination
    for variable in unique_variables:
        for city_idx, city in enumerate(unique_cities):
            filtered_data = data[(data["City"] == city) & (data["Variable"] == variable)]

            # Add actual and predicted traces to the figure
            row = city_idx // 3 + 1
            col = city_idx % 3 + 1

            actual_trace = go.Scatter(
                x=filtered_data["Year"],
                y=filtered_data["Budget"],
                mode="lines",
                name=f"Actual - {variable} ({city})",
                showlegend=True  # Ensure legend is shown
            )
            predicted_trace = go.Scatter(
                x=filtered_data["Year"],
                y=filtered_data["Predicted"],
                mode="lines",
                name=f"Predicted - {variable} ({city})",
                showlegend=True  # Ensure legend is shown
            )

            fig.add_trace(actual_trace, row=row, col=col)
            fig.add_trace(predicted_trace, row=row, col=col)

            # Store traces for later reference in the dropdown
            traces.append((actual_trace, predicted_trace))

    # Create dropdown buttons for variable selection
    variable_buttons = []
    for variable in unique_variables:
        visibility = [False] * len(fig.data)
        for i, (actual_trace, predicted_trace) in enumerate(traces):
            if variable in actual_trace.name:
                visibility[2*i] = True  # Show the actual trace for this variable
            if variable in predicted_trace.name:
                visibility[2*i+1] = True  # Show the predicted trace for this variable

        variable_buttons.append(
            dict(
                label=variable,
                method="update",
                args=[
                    {"visible": visibility},
                    {"title": f"Actual vs Predicted Budgets for {variable}"}
                ]
            )
        )

    # Create a layout with dropdown buttons for variable selection
    fig.update_layout(
        updatemenus=[
            {
                "buttons": variable_buttons,
                "direction": "down",
                "showactive": True,
                "x": 0.17,
                "y": 1.15,
                "xanchor": "left",
            }
        ],
        title="Actual vs Predicted Budgets",
        xaxis_title="Year",
        yaxis_title="Budget",
        height=800,  # Increase height to accommodate legend at the bottom
        grid=dict(rows=2, columns=3, pattern="independent"),  # 2x3 grid layout
        legend=dict(
            orientation="h",  # Horizontal layout
            yanchor="bottom",  # Place legend at the bottom
            y=-0.15,  # Position legend slightly below the graph area
            xanchor="center",  # Center the legend
            x=0.5,  # Center the legend horizontally
        ),
    )

    # Show the figure
    fig.show()



def main_workflow():
    # Load the data
    data = pd.read_csv('data/MajorMetroCityBudgets.csv')
    data = preprocess_data(data)
    
    # Step 2: Interactive graph for city trends
    interactive_city_trends(data)
    
    # Select a city (e.g., Boston MA) for analysis and prediction
    category = "MA: Boston"
    
    # Step 3: Prepare data for gradient boosting model
    X_train, X_test, y_train, y_test = prepare_data_for_gbm(data, category)
    
    # Step 4: Train the gradient boosting model
    gbm_model = train_gbm(X_train, X_test, y_train, y_test)
    
    # Step 5: Visualize predictions interactively
    visualize_predictions_interactive(data, gbm_model)

# Run the workflow
if __name__ == "__main__":
    main_workflow()
