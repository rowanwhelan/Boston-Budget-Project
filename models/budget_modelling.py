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
from sklearn.preprocessing import OneHotEncoder

# Step 1: Clean the data so it can be used 
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

"""# Step 3: Analyze Trends with Prophet and Add Context
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
"""

# Step 3 and 7: Prepare Data for Gradient Boosting Model
def prepare_data_for_gbm_all(data):
    # Create lag features for all cities
    
    data = data.sort_values(by=["Variable", "Year"]).reset_index(drop=True)
 
    data["Lag1"] = data["Budget"].shift(1)
    data["Lag2"] = data["Budget"].shift(2)
    
    # Apply the condition to set Lag1 and Lag2 to NaN based on index
    data["Lag1"] = data.apply(lambda row: 0 if (row.name) % 22 == 0 else row["Lag1"], axis=1)
    data["Lag2"] = data.apply(lambda row: 0 if (row.name) % 22 == 0 else row["Lag2"], axis=1)
    data["Lag2"] = data.apply(lambda row: 0 if (row.name) % 22 == 1 else row["Lag2"], axis=1)
    
    data.dropna(inplace=True)
    
    # Apply one-hot encoding to the 'Variable' column
    encoder = OneHotEncoder(sparse_output=False)
    variable_encoded = encoder.fit_transform(data[["Variable"]])

    # Convert encoded array to a DataFrame with appropriate column names
    encoded_df = pd.DataFrame(variable_encoded, columns=encoder.get_feature_names_out(["Variable"]))

    # Concatenate with existing lag features
    data = pd.concat([data.reset_index(drop=True), encoded_df.reset_index(drop=True)], axis=1)
    
    # Split into features and target
    X = data.drop(columns=["Budget", "Variable", "City"])
    y = data["Budget"]
    
    # Train-test split (we will train on the entire dataset and predict on the same)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    return X_train, X_test, y_train, y_test

def prepare_data_for_gbm_category(data, category):
    # Filter for Boston city only
    boston_data = data[data["City"] == category].copy()  # Explicitly create a copy
    
    boston_data = boston_data.sort_values(by=["Variable", "Year"]).reset_index(drop=True)
    
    # Create lag features for Boston data
    boston_data["Lag1"] = boston_data["Budget"].shift(1)
    boston_data["Lag2"] = boston_data["Budget"].shift(2)
    
    # Apply the condition to set Lag1 and Lag2 to NaN based on index
    boston_data["Lag1"] = boston_data.apply(lambda row: 0 if (row.name) % 22 == 0 else row["Lag1"], axis=1)
    boston_data["Lag2"] = boston_data.apply(lambda row: 0 if (row.name) % 22 == 0 else row["Lag2"], axis=1)
    boston_data["Lag2"] = boston_data.apply(lambda row: 0 if (row.name) % 22 == 1 else row["Lag2"], axis=1)
    
    boston_data.dropna(inplace=True)
    
    # Apply one-hot encoding to the 'Variable' column
    encoder = OneHotEncoder(sparse_output=False)
    variable_encoded = encoder.fit_transform(boston_data[["Variable"]])

    # Convert encoded array to a DataFrame with appropriate column names
    encoded_df = pd.DataFrame(variable_encoded, columns=encoder.get_feature_names_out(["Variable"]))

    # Concatenate with existing lag features
    boston_data = pd.concat([boston_data.reset_index(drop=True), encoded_df.reset_index(drop=True)], axis=1)
    
    # Split into features and target
    X_boston = boston_data.drop(columns=["Budget", "Variable", "City"])
    y_boston = boston_data["Budget"]
    
    # Train-test split for Boston
    X_train, X_test, y_train, y_test = train_test_split(X_boston, y_boston, test_size=0.2, random_state=42)
    
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
    print(f"MSE:{mse}")
    
    return model

# Step 6: Visualize the changes and the model
def visualize_predictions_interactive(data, model):
    # Ensure data includes predictions for all cities
    data = data.copy()
    
    data = data.sort_values(by=["Variable", "Year"]).reset_index(drop=True)
 
    data["Lag1"] = data["Budget"].shift(1)
    data["Lag2"] = data["Budget"].shift(2)
    
    # Apply the condition to set Lag1 and Lag2 to NaN based on index
    data["Lag1"] = data.apply(lambda row: 0 if (row.name) % 22 == 0 else row["Lag1"], axis=1)
    data["Lag2"] = data.apply(lambda row: 0 if (row.name) % 22 == 0 else row["Lag2"], axis=1)
    data["Lag2"] = data.apply(lambda row: 0 if (row.name) % 22 == 1 else row["Lag2"], axis=1)
    
    data.dropna(inplace=True)
    
    encoder = OneHotEncoder(sparse_output=False)
    
    # One-hot encode the 'Variable' column
    categorical_encoded = encoder.fit_transform(data["Variable"].values.reshape(-1,1))
    
    encoded_df = pd.DataFrame(categorical_encoded, columns=encoder.get_feature_names_out(['Variable']))
    data = pd.concat([data.reset_index(drop=True), encoded_df.reset_index(drop=True)], axis=1)
    data["Predicted"] = model.predict(data.drop(columns=["Budget", "City", "Variable"]))
    data.loc[(data["Lag1"] == 0) & (data["Lag2"] == 0), "Predicted"] = 0

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
                "x": .32,
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

# Step 8: Generate predictions on the future
def generate_future_predictions(data, model, category, start_year=2022, end_year=2022):
    # Filter for the given city/category
    city_data = data[data["City"] == category].copy()
    
    city_data = city_data.sort_values(by=["Variable", "Year"]).reset_index(drop=True)
 
    city_data["Lag1"] = city_data["Budget"].shift(1)
    city_data["Lag2"] = city_data["Budget"].shift(2)
    
    # Apply the condition to set Lag1 and Lag2 to NaN based on index
    city_data["Lag1"] = city_data.apply(lambda row: 0 if (row.name) % 22 == 0 else row["Lag1"], axis=1)
    city_data["Lag2"] = city_data.apply(lambda row: 0 if (row.name) % 22 == 0 else row["Lag2"], axis=1)
    city_data["Lag2"] = city_data.apply(lambda row: 0 if (row.name) % 22 == 1 else row["Lag2"], axis=1)
    
    city_data.dropna(inplace=True)
    
    encoder = OneHotEncoder(sparse_output=False)
    
    # One-hot encode the 'Variable' column
    categorical_encoded = encoder.fit_transform(city_data["Variable"].values.reshape(-1,1))
    
    encoded_df = pd.DataFrame(categorical_encoded, columns=encoder.get_feature_names_out(['Variable']))
    
    city_data = pd.concat([city_data.reset_index(drop=True), encoded_df.reset_index(drop=True)], axis=1)
    
    city_data["Predicted"] = model.predict(city_data.drop(columns=["Budget", "City", "Variable"]))
    city_data.loc[(city_data["Lag1"] == 0) & (city_data["Lag2"] == 0), "Predicted"] = 0
    
    city_data.dropna(inplace=True)
    future_data = []
    previous_prediction = 0
    previous_previous_predicition = 0
    for i in range(city_data.shape[0] // 22):
        for year in range(start_year, end_year + 1):      
            # Generate future predictions
            future_row = {}
            future_row["Variable"] = city_data.loc[i*22+1]["Variable"]
            future_row["Year"] = year
            future_row["City"] = category            
            future_row["Budget"] = None
            # Calculate the lags for the future data
            if year-start_year == 0:
                future_row["Lag1"] = city_data.loc[(i+1)*22+ year - start_year - 1]["Budget"]
                future_row["Lag2"] = city_data.loc[(i+1)*22 + year - start_year - 2]["Budget"]
            elif year-start_year == 1:
                future_row["Lag1"] = previous_prediction
                future_row["Lag2"] = city_data.loc[(i+1)*22 + year - start_year-2]["Budget"]
            else:
                future_row["Lag1"] = previous_prediction
                future_row["Lag2"] = previous_previous_predicition

            for col in city_data.columns:
                if col.startswith("Variable_"):
                    future_row[col] = city_data.loc[i*22 + 1, col]
            
            prediction = model.predict(pd.DataFrame([[future_row["Year"], future_row["Lag1"], future_row["Lag2"]] + \
            [future_row[col] for col in future_row if col.startswith("Variable_")]], columns=["Year", "Lag1", "Lag2"] + \
            [col for col in future_row if col.startswith("Variable_")]))[0]
            future_row["Predicted"] = prediction
                
            previous_previous_predicition = previous_prediction
            previous_prediction = prediction
            if future_row["Lag1"] == 0 and future_row["Lag2"] == 0:
                future_row["Predicted"] = 0
            # Append the future row to the future data list
            future_data.append(future_row)
        
    future_data = pd.DataFrame(future_data)

    # Concatenate the historical data with the predicted future data
    complete_data = pd.concat([city_data, future_data], ignore_index=True)
    complete_data = complete_data.sort_values(by=["Variable", "Year"]).reset_index(drop=True)
    return complete_data

# Step 9: Graph the future predictions
def visualize_boston_predictions(complete_data):
    
    # Define the unique variables in the data
    unique_variables = complete_data["Variable"].unique().tolist()
    unique_variables.append("All Variables")  # Add "All Variables" as an option
    
    # Create traces for actual and predicted values
    traces = []
    
    for variable in unique_variables:
        if variable == "All Variables":
            pass
        else:
            # Filter data by the selected variable
            filtered_data = complete_data[complete_data["Variable"] == variable]
            
            # Add actual trace
            traces.append(
                go.Scatter(
                    x=filtered_data["Year"],
                    y=filtered_data["Budget"],
                    mode="lines",
                    name=f"Actual - {variable}",
                )
            )
            
            # Add predicted trace
            traces.append(
                go.Scatter(
                    x=filtered_data["Year"],
                    y=filtered_data["Predicted"],
                    mode="lines",
                    name=f"Predicted - {variable}",
                )
            )
    
    # Create dropdown buttons for variables
    variable_buttons = []
    for variable in unique_variables:
        visibility = [True] * len(traces)  # Show all traces initially
        
        # Filter the traces to show only for the selected variable
        if variable != "All Variables":
            visibility = [False if ( (str(variable)) not in (str(trace.name))) else True for trace in traces]
        
        variable_buttons.append(
            dict(
                label=variable,
                method="update",
                args=[{"visible": visibility}, {"title": f"Actual vs Predicted Budgets for {variable}"}],
            )
        )
    
    # Create the figure
    fig = go.Figure(data=traces)
    
    # Add dropdown menu for variables
    fig.update_layout(
        updatemenus=[{
            "buttons": variable_buttons,
            "direction": "down",
            "showactive": True,
            "x": 0.17,
            "y": 1.15,
            "xanchor": "left",
        }],
        title="Actual vs Predicted Budgets for Boston (with Future Predictions)",
        xaxis_title="Year",
        yaxis_title="Budget",
    )
    
    fig.show()

def main_workflow():
    # Load the data
    data = pd.read_csv('data/MajorMetroCityBudgets.csv')
    
    # Step 1: Preprocess the Data
    data = preprocess_data(data)

    # Step 2: Interactive graph for city trends
    interactive_city_trends(data)
    
    # Step 3: Prepare data for gradient boosting model (Train on all cities)
    X_train, X_test, y_train, y_test = prepare_data_for_gbm_all(data)
    
    # Step 4: Train the gradient boosting model
    gbm_model_all = train_gbm(X_train, X_test, y_train, y_test)
    
    # Step 5: Visualize predictions interactively for all cities
    visualize_predictions_interactive(data, gbm_model_all)

    # Select a city (e.g., Boston MA) for analysis and prediction
    category = "MA: Boston"
    
    # Step 6: Prepare data for gradient boosting model (Train only on Boston)
    X_train, X_test, y_train, y_test = prepare_data_for_gbm_category(data, category)
    
    # Step 7: Train the gradient boosting model for Boston
    gbm_model_boston = train_gbm(X_train, X_test, y_train, y_test)
    
    # Step 8: Generate future predictions for Boston (2021-2030)
    complete_data = generate_future_predictions(data, gbm_model_boston, category, start_year=2022, end_year=2025)
    
    # Step 9: Visualize the actual and predicted budgets for Boston (including future predictions)
    visualize_boston_predictions(complete_data)
    return True

if __name__ == "__main__":
    assert main_workflow()