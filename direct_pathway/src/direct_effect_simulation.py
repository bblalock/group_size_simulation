import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def group_effect(is_disadvantaged, theta, pi):
    """
    Calculate group effect where:
    - theta = 0: Both groups equal to population average
    - theta = 1: Advantaged group at 0, disadvantaged group carries the full population average
    - Population average is maintained at 1 for all theta values
    
    Parameters:
    - is_disadvantaged: Boolean, True for disadvantaged group
    - theta: Float between 0 and 1, controls disparity
    - pi: Proportion of population in disadvantaged group
    
    Returns: Multiplier for the group's incarceration rate
    """
    if is_disadvantaged:
        # When theta=1, this equals 1/pi to ensure population average
        return 1 + theta * ((1 - pi) / pi)
    else:
        # When theta=1, this equals 0
        return 1 - theta

# Parameters to explore
thetas = np.linspace(0, 1, 5)
pi_values = np.linspace(.1, .9, 3)
avg_rate = 200  # Maximum incarceration rate

# Calculate rates for all pi values
data = []
for pi in pi_values:
    for theta in thetas:
        # Calculate effects
        effect_disadv = group_effect(True, theta, pi)
        effect_adv = group_effect(False, theta, pi)
        
        # Calculate rates (using pure group effect, α=1)
        rate_disadv = avg_rate * effect_disadv
        rate_adv = avg_rate * effect_adv
        
        # Calculate population average
        pop_avg = pi * rate_disadv + (1 - pi) * rate_adv
        
        # Calculate disparity metrics
        disparity_diff = rate_disadv - rate_adv
        disparity_ratio = rate_disadv / rate_adv if rate_adv > 0 else float('inf')
        
        # Calculate odds and odds ratio
        # Assuming rates are per 100,000 population
        odds_disadv = rate_disadv / (100000 - rate_disadv) if rate_disadv < 100000 else float('inf')
        odds_adv = rate_adv / (100000 - rate_adv) if rate_adv < 100000 else float('inf')
        odds_ratio = odds_disadv / odds_adv if odds_adv > 0 else float('inf')
        
        # Add to data
        data.append({
            "theta": theta, 
            "Group": "Disadvantaged", 
            "Rate": rate_disadv, 
            "pi": pi,
            "Disparity Difference": disparity_diff,
            "Disparity Ratio": disparity_ratio,
            "Odds": odds_disadv,
            "Odds Ratio": odds_ratio
        })
        data.append({
            "theta": theta, 
            "Group": "Advantaged", 
            "Rate": rate_adv, 
            "pi": pi,
            "Disparity Difference": disparity_diff,
            "Disparity Ratio": disparity_ratio,
            "Odds": odds_adv,
            "Odds Ratio": odds_ratio
        })
        data.append({
            "theta": theta, 
            "Group": "Population Average", 
            "Rate": pop_avg, 
            "pi": pi,
            "Disparity Difference": disparity_diff,
            "Disparity Ratio": disparity_ratio,
            "Odds": pop_avg / (100000 - pop_avg) if pop_avg < 100000 else float('inf'),
            "Odds Ratio": odds_ratio
        })

# Create DataFrame
df = pd.DataFrame(data)

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
                f"{row['Disparity Difference']:.1f}",
                f"{row['Disparity Ratio']:.2f}",
                f"{row['Odds']:.5f}",
                f"{row['Odds Ratio']:.2f}"
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

fig.show()