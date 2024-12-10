import pandas as pd
import plotly.graph_objects as go

# Load and preprocess data
file_path = "data/budget_revisions_by_major_class.csv"  # Replace with your file path
data = pd.read_csv(file_path)

# Melt the DataFrame to long format for easier plotting
proposed_cols = [col for col in data.columns if "(Proposed)" in col]
revised_cols = [col for col in data.columns if "(Revised)" in col]

long_data = pd.DataFrame()

for proposed, revised in zip(proposed_cols, revised_cols):
    year = proposed.split()[0]
    subset = data.copy()
    subset["year"] = year
    subset["proposed_budget"] = data[proposed]
    subset["revised_budget"] = data[revised]
    subset = subset.drop(columns=proposed_cols + revised_cols)
    long_data = pd.concat([long_data, subset], ignore_index=True)

# Create the scatter plot using plotly.graph_objects for better control
fig = go.Figure()

# Add data for each year
years = long_data["year"].unique()
traces = []
for year in years:
    year_data = long_data[long_data["year"] == year]
    trace = go.Scatter(
        x=year_data["proposed_budget"],
        y=year_data["revised_budget"],
        mode="markers",
        name=str(year),
        marker=dict(size=10),
        customdata=year_data.drop(columns=["proposed_budget", "revised_budget", "year"]).to_dict("records"),
        hovertemplate="<br>".join([
            "Proposed: %{x}",
            "Revised: %{y}",
            "%{customdata}"
        ])
    )
    fig.add_trace(trace)

# Add a dashed line y = x
fig.add_shape(
    type="line",
    x0=long_data["proposed_budget"].min(),
    y0=long_data["proposed_budget"].min(),
    x1=long_data["proposed_budget"].max(),
    y1=long_data["proposed_budget"].max(),
    line=dict(color="LightGray", dash="dash"),
    name="x = y"
)

# Create buttons
buttons = [
    dict(
        label="Show All Points",
        method="update",
        args=[{"visible": [True] * len(fig.data)}]
    ),
    dict(
        label="Remove x=y",
        method="update",
        args=[
            {"visible": [
                any(
                    trace.x[i] != trace.y[i]
                    for i in range(len(trace.x))
                )
                for trace in fig.data
            ]}
        ]
    )
]

# Add a button for each year
for year in years:
    visibility = [
        trace.name == str(year) for trace in fig.data
    ]
    buttons.append(
        dict(
            label=f"Show {year}",
            method="update",
            args=[{"visible": visibility}]
        )
    )

# Add the buttons to the layout
fig.update_layout(
    updatemenus=[
        dict(
            type="buttons",
            direction="down",
            buttons=buttons,
            pad={"r": 10, "t": 10},
            showactive=True,
            x=0.1,
            xanchor="left",
            y=1.1,
            yanchor="top"
        )
    ]
)

# Show the plot
fig.show()
