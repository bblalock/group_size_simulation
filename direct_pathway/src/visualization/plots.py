import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_explanatory_simulation(df, pi_values, thetas):
    """
    Create visualization of explanatory simulation results with fixed average rate.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing simulation results
    pi_values : list
        List of pi values used in the simulation
    thetas : list
        List of theta values used in the simulation
    """
    # Create figure with subplots
    fig = make_subplots(
        rows=len(pi_values), 
        cols=2,
        subplot_titles=[f"π = {pi}" for pi in pi_values for _ in range(2)],
        specs=[[{"type": "bar"}, {"type": "table"}] for _ in range(len(pi_values))],
        horizontal_spacing=0.05,
        vertical_spacing=0.1
    )

    # Add bar charts to left column
    for i, pi in enumerate(pi_values):
        # Filter data for this pi value
        pi_data = df[(df["pi"] == pi) & (df["Group"] != "Population Average")]
        
        # Add grouped bar chart
        for group in ["Disadvantaged", "Advantaged"]:
            group_data = pi_data[pi_data["Group"] == group]
            fig.add_trace(
                go.Bar(
                    x=group_data["theta"],
                    y=group_data["Rate"],
                    name=group,
                    legendgroup=group,
                    showlegend=(i == 0),  # Only show in legend for first row
                    marker_color="red" if group == "Disadvantaged" else "blue"
                ),
                row=i+1, col=1
            )
        
        # Add population average line
        pop_avg_data = df[(df["Group"] == "Population Average") & (df["pi"] == pi)]
        fig.add_trace(
            go.Scatter(
                x=pop_avg_data["theta"],
                y=pop_avg_data["Rate"],
                mode="lines",
                line=dict(color="grey", width=1.5, dash="dash"),
                name="Population Average",
                legendgroup="Population Average",
                showlegend=(i == 0)  # Only show in legend for first row
            ),
            row=i+1, col=1
        )
        
        # Add disparity metrics table to right column
        # Create summary table for each theta value
        table_data = []
        for theta in thetas:
            theta_data = df[(df["pi"] == pi) & (df["theta"] == theta) & (df["Group"] == "Disadvantaged")]
            if not theta_data.empty:
                row = theta_data.iloc[0]
                table_data.append([
                    f"{theta:.2f}",
                    f"{row['disparity_difference']:.1f}",
                    f"{row['disparity_ratio']:.2f}",
                    f"{row['odds_disadvantaged']:.5f}",
                    f"{row['odds_ratio']:.2f}"
                ])
        
        fig.add_trace(
            go.Table(
                header=dict(
                    values=["θ", "Disparity Diff", "Disparity Ratio", "Odds (Disadv)", "Odds Ratio"],
                    font=dict(size=10),
                    align="left"
                ),
                cells=dict(
                    values=list(map(list, zip(*table_data))),
                    font=dict(size=10),
                    align="left"
                )
            ),
            row=i+1, col=2
        )

    # Update layout
    fig.update_layout(
        height=300 * len(pi_values),
        width=1000,
        title="Group Effect on Incarceration Rates with Disparity Metrics",
        barmode="group",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        )
    )

    # Update axes
    for i in range(len(pi_values)):
        fig.update_xaxes(title_text="θ (Disparity Parameter)", row=i+1, col=1)
        if i == len(pi_values) - 1:
            fig.update_yaxes(title_text="Incarceration Rate", row=i+1, col=1)
        else:
            fig.update_yaxes(title_text="", row=i+1, col=1)
    
    return fig

def plot_total_simulation(df, pi_values, thetas, avg_rates):
    """
    Create visualization of total simulation results with varying average rates.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing simulation results
    pi_values : list
        List of pi values used in the simulation
    thetas : list
        List of theta values used in the simulation
    avg_rates : list
        List of average rate values used in the simulation
    """
    # Placeholder for future implementation
    print("Total simulation plotting not yet implemented")
    pass