import numpy as np
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import beta

from core.visualization.base_plots import create_3d_scatter
from core.visualization.style import plotly_theme_decorator
from indirect_pathway.src.model.indirect_effect import normalize_rates_to_target

# Global legend group names
DISADV_GROUP = "Disadvantaged"
ADV_GROUP = "Advantaged"


@plotly_theme_decorator
def create_stratification_plot(positions, num_bins=100, **kwargs):
    """Creates a combined plot with histograms and PDF curves for both groups"""
    # Create figure with secondary y-axis
    fig = make_subplots(rows=1, cols=1, specs=[[{"secondary_y": True}]])

    # Extract parameters
    alpha_disadv = positions['alpha_disadv']
    beta_disadv = positions['beta_disadv']
    alpha_adv = positions['alpha_adv']
    beta_adv = positions['beta_adv']

    # Create histograms and PDF curves for disadvantaged group
    fig.add_trace(
        go.Histogram(
            x=positions['positions_disadv'],
            name=DISADV_GROUP,
            opacity=0.5,
            marker_color='red',
            nbinsx=num_bins,
            showlegend=True,
            legendgroup=DISADV_GROUP
        ),
        secondary_y=False
    )

    x = np.linspace(0, 1, 1000)
    fig.add_trace(
        go.Scatter(
            x=x,
            y=beta.pdf(x, alpha_disadv, beta_disadv),
            mode='lines',
            name=DISADV_GROUP,
            line=dict(color='darkred', width=2),
            showlegend=False,
            legendgroup=DISADV_GROUP
        ),
        secondary_y=True
    )

    # Create histograms and PDF curves for advantaged group
    fig.add_trace(
        go.Histogram(
            x=positions['positions_adv'],
            name=ADV_GROUP,
            opacity=0.5,
            marker_color='blue',
            nbinsx=num_bins,
            showlegend=True,
            legendgroup=ADV_GROUP
        ),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(
            x=x,
            y=beta.pdf(x, alpha_adv, beta_adv),
            mode='lines',
            name=ADV_GROUP,
            line=dict(color='darkblue', width=2),
            showlegend=False,
            legendgroup=ADV_GROUP
        ),
        secondary_y=True
    )

    # Update layout
    fig.update_layout(
        title='Stratification Position Distributions',
        xaxis_title='Z Position (Economic Status)',
        legend_title='Groups',
        barmode='overlay',
        boxgap=0
    )

    # Update y-axis labels
    fig.update_yaxes(title_text="Frequency", secondary_y=False, showgrid=False)
    fig.update_yaxes(title_text="Density", secondary_y=True, showgrid=False)
    fig.update_yaxes(rangemode='tozero')

    return fig


def calculate_rates_with_floor(x_curve, gamma, target_avg_rate, floor_rate=0):
    """
    Calculate rates for a given curve, applying floor and normalization if needed.

    Parameters:
    -----------
    x_curve : numpy.ndarray
        Array of x positions to calculate rates for
    gamma : float
        Shape parameter controlling relationship between position and incarceration rate
    target_avg_rate : float
        Target population-average incarceration rate
    floor_rate : float, optional
        Minimum incarceration rate before normalization (default=0)

    Returns:
    --------
    numpy.ndarray
        Array of final calculated rates
    """
    # Calculate base position effect: (1-z)^gamma for all positions
    all_effects = np.power(1 - x_curve, gamma)

    # Calculate initial rates
    initial_rates = target_avg_rate * all_effects / np.mean(all_effects)

    # Apply floor if specified
    if floor_rate > 0:
        rates_with_floor = np.maximum(floor_rate, initial_rates)
        # Normalize to maintain target average
        final_rates, _ = normalize_rates_to_target(
            rates_with_floor, target_avg_rate)
    else:
        final_rates = initial_rates

    return final_rates


@plotly_theme_decorator
def create_position_to_rate_plot(gamma, target_avg_rate, floor_rate=0, norm_factors=None, **kwargs):
    """
    Creates a plot showing how position maps to incarceration rate

    Parameters:
    -----------
    gamma : float
        Shape parameter controlling relationship between position and incarceration rate
    target_avg_rate : float
        Target population-average incarceration rate
    floor_rate : float, optional
        Minimum incarceration rate before normalization (default=0)
    """

    # Generate curve data points
    x_curve = np.linspace(0, 1, 100)
    
    # Create dataframe to hold all curves
    curves_data = []
    
    # Add curves for gamma-1, gamma, and gamma+1
    for g_key, g_label, g_delta in [('gamma-1', f'γ={max(gamma-1, 0):.1f}', -1), 
                                    ('gamma', f'γ={gamma:.1f}', 0), 
                                    ('gamma+1', f'γ={gamma+1:.1f}',1)
                                    ]:
        
        # Calculate base effects
        base_effects = np.power(1 - x_curve, gamma + g_delta)
        
        # Apply normalization factors
        if norm_factors:
            nf = norm_factors[g_key]['factors']
            initial_rates = target_avg_rate * base_effects * nf['first_norm_factor']
            
            # Apply floor and second normalization
            rates_with_floor = np.maximum(floor_rate, initial_rates)
            final_rates = rates_with_floor * nf['second_norm_factor']
        else:
            # Fallback to original calculation if norm_factors not provided
            final_rates = calculate_rates_with_floor(x_curve, float(g_key.replace('gamma', '')) + gamma, 
                                                   target_avg_rate, floor_rate)
        
        # Add to dataframe
        curves_data.extend([{
            'x': x,
            'y': y,
            'gamma': g_label
        } for x, y in zip(x_curve, final_rates)])

    df = pd.DataFrame(curves_data)

    # Create scatter plot with lines
    fig = px.scatter(df, x='x', y='y', color='gamma',
                     title=f'Position-to-Rate Function (γ={gamma:.1f} (+/- 1), Target Average Rate={target_avg_rate:,.0f})',
                     labels={'x': 'Economic Position (Z)',
                             'y': 'Expected Incarceration Rate (per 100,000)',
                             'gamma': 'Steepness Parameter'},
                     marginal_y='box')

    # Update layout for better readability
    fig.update_layout(
        title_x=0.5,  # Center the title
        legend_title_text='Shape Parameter (γ), (+/- 1)',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99
        ),
        xaxis=dict(
            title_font=dict(size=14),
            tickfont=dict(size=12),
            gridcolor='lightgray'
        ),
        yaxis=dict(
            title_font=dict(size=14),
            tickfont=dict(size=12),
            gridcolor='lightgray'
        )
    )

    # Convert scatter to lines and improve boxplots
    for g in [max(gamma-1, 0), gamma, gamma+1]:
        # Update line traces
        fig.update_traces(
            mode='lines',
            line=dict(
                width=3,  # Thicker lines
                color='lightgray' if g != gamma else 'black',
                dash='dash' if g != gamma else None
            ),
            selector=dict(name=f'γ={g:.1f}', type='scatter')
        )

        # Update boxplots
        fig.update_traces(
            marker=dict(
                color='lightgray' if g != gamma else 'black',
                opacity=0.7
            ),
            boxmean=True,  # Show mean as a dashed line
            line=dict(width=2),  # Thicker box lines
            selector=dict(name=f'γ={g:.1f}', type='box')
        )

    # Add y-axis label for boxplots
    fig.update_layout(
        yaxis2=dict(
            showgrid=True,
            gridcolor='lightgray'
        )
    )

    fig.update_yaxes(rangemode='tozero')

    return fig


@plotly_theme_decorator
def create_incarceration_rate_plot(rate_data, gamma, target_avg_rate, positions, norm_factors=None, **kwargs):
    """Creates a plot of incarceration rates with position markers and group boxplots"""
    # Create figure with marginal box plots
    fig = make_subplots(
        rows=2, cols=2,
        column_widths=[0.2, 0.8],
        row_heights=[0.2, 0.8],
        specs=[
            [None,
             {"type": "xy", 'secondary_y': True}],
            [{"type": "box"},
             {"type": "scatter"}
             ]
        ],
        shared_xaxes='columns',
        shared_yaxes='rows',
        horizontal_spacing=0.05,
        vertical_spacing=0.05
    )

    # Extract data
    positions_disadv = rate_data['positions_disadv']
    positions_adv = rate_data['positions_adv']
    rates_disadv = rate_data['rates_disadv']
    rates_adv = rate_data['rates_adv']
    pop_avg_rate = rate_data['pop_avg_rate']
    floor_rate = rate_data['floor_rate']

    # Generate curve data points
    x_curve = np.linspace(0, 1, 1000)
    
    # Calculate base effects
    base_effects = np.power(1 - x_curve, gamma)
    
    # Apply the empirical normalization factors
    if norm_factors:
        initial_rates = target_avg_rate * base_effects * norm_factors['first_norm_factor']
        rates_with_floor = np.maximum(floor_rate, initial_rates)
        y_curve = rates_with_floor * norm_factors['second_norm_factor']
    else:
        # Fallback to original calculation if norm_factors not provided
        y_curve = calculate_rates_with_floor(x_curve, gamma, target_avg_rate, floor_rate)
    
    # Add the theoretical curve
    fig.add_trace(
        go.Scatter(
            x=x_curve,
            y=y_curve,
            mode='lines',
            name=f'Incarceration Rate Curve (γ={gamma:.1f})',
            line=dict(color='black', width=2)
        ),
        row=2, col=2
    )

    # Add position/rate markers for disadvantaged group
    fig.add_trace(
        go.Scatter(
            x=positions_disadv,
            y=rates_disadv,
            mode='markers',
            name=DISADV_GROUP,
            marker=dict(color='red',
                        size=12,
                        opacity=0.4,
                        symbol='diamond-open',
                        # line=dict(width=2, color='black')
                        ),
            legendgroup=DISADV_GROUP
        ),
        row=2, col=2
    )

    # Add position/rate markers for advantaged group
    fig.add_trace(
        go.Scatter(
            x=positions_adv,
            y=rates_adv,
            mode='markers',
            name=ADV_GROUP,
            marker=dict(color='blue',
                        size=12,
                        opacity=0.4,
                        symbol='circle-open',
                        # line=dict(width=2, color='black')
                        ),
            legendgroup=ADV_GROUP
        ),
        row=2, col=2
    )

    # Add target/population average line to scatter plot
    fig.add_trace(
        go.Scatter(
            x=[0, 1],
            y=[pop_avg_rate, pop_avg_rate],
            mode='lines',
            name=f'Population Average ({pop_avg_rate:.1f})',
            line=dict(color='green', width=2, dash='dash')
        ),
        row=2, col=2
    )

    # Add target/population average line to box plot
    fig.add_trace(
        go.Scatter(
            x=[0, 1],
            y=[pop_avg_rate, pop_avg_rate],
            mode='lines',
            name=f'Population Average ({pop_avg_rate:.1f})',
            line=dict(color='green', width=2, dash='dash'),
            showlegend=False
        ),
        row=2, col=1
    )

    # Add boxplot for disadvantaged group
    fig.add_trace(
        go.Box(
            y=rates_disadv,
            name=DISADV_GROUP,
            marker_color='red',
            boxmean=True,
            legendgroup=DISADV_GROUP,
            showlegend=False
        ),
        row=2, col=1
    )

    # Add boxplot for advantaged group
    fig.add_trace(
        go.Box(
            y=rates_adv,
            name=ADV_GROUP,
            marker_color='blue',
            boxmean=True,
            legendgroup=ADV_GROUP,
            showlegend=False
        ),
        row=2, col=1
    )

    # Add distribution of positions along x-axis
    # Get the traces from create_stratification_plot
    strat_plot = create_stratification_plot(positions)

    # Add each trace to our main figure in row 1, col 2
    for i, trace in enumerate(strat_plot.data):
        # First trace goes on primary y-axis
        if trace.type == 'scatter':
            fig.add_trace(
                trace,
                row=1, col=2,
                secondary_y=True
            )
        # Second trace goes on secondary y-axis
        else:
            fig.add_trace(
                trace,
                row=1, col=2,
                secondary_y=False
            )

    # Update layout
    fig.update_layout(
        title=f'Incarceration Rate by Stratification Position (γ={gamma:.1f}, Target Avg={target_avg_rate})',
        boxmode='group',
        barmode='overlay'
    )

    # Update axes
    fig.update_xaxes(title_text='Z Position (Economic Status)', row=2, col=2)
    fig.update_yaxes(
        title_text='Incarceration Rate (per 100,000)', row=2, col=1)
    fig.update_xaxes(row=1, col=2, showgrid=True)
    fig.update_yaxes(title_text='Frequency', row=1, col=2, showgrid=False)
    fig.update_yaxes(title_text='Density', row=1, col=2,
                     secondary_y=True, showgrid=False)
    fig.update_yaxes(rangemode='tozero')

    return fig

@plotly_theme_decorator
def plot_parameter_metric_correlations(simulation_results, min_rate=0):
    """
    Creates a heatmap showing correlations between variable parameters and derived metrics.
    
    Args:
        simulation_results (pd.DataFrame): The simulation results dataframe
        min_rate (int, optional): The minimum rate to filter by. Defaults to 0.
        
    Returns:
        plotly.graph_objects.Figure: The correlation heatmap figure
    """
    # Variable parameters (those that have multiple values in the simulation)
    variable_params = [
        'prop_disadv',  # Same as 'p'
        'gamma',
        'z_position_gap',
        # 'min_rate'  # This is floor_rate_values in simulation.py
    ]

    # Derived metrics (calculated from the simulation results)
    derived_metrics = [
        'disparity_ratio',
        'rate_difference',
        'rate_disadv',
        'disadv_delta_from_avg_percent',
        'rate_adv',
        'adv_delta_from_avg_percent',
        'normalized_disparity_index',
    ]

    # Filter data for a specific min_rate to focus analysis
    plot_df = simulation_results[simulation_results['min_rate']==min_rate]

    # Create a non-square correlation matrix with variable parameters as rows and derived metrics as columns
    var_derived_corr = pd.DataFrame(index=variable_params, columns=derived_metrics)
    for param in variable_params:
        for metric in derived_metrics:
            var_derived_corr.loc[param, metric] = plot_df[param].corr(plot_df[metric])

    # Create a heatmap for variable parameters vs derived metrics (non-square matrix)
    fig = go.Figure(data=go.Heatmap(
        z=var_derived_corr.values,
        x=var_derived_corr.columns,
        y=var_derived_corr.index,
        colorscale='RdBu_r',
        zmid=0,
        zmin=-1, zmax=1,
        text=np.round(var_derived_corr.values.astype(float), 2),
        texttemplate='%{text:.2f}',
        hoverinfo='text',
        colorbar=dict(title='Correlation'),
    ))

    fig.update_layout(
        title=f'Correlation Between Variable Parameters and Derived Metrics (min_rate={min_rate})',
        title_font_size=16,
        width=700,
        height=500,
        xaxis=dict(
            tickangle=-45,
            title='Derived Metrics'
        ),
        yaxis=dict(
            title='Variable Parameters'
        ),
        template='plotly_white'
    )
    
    return fig

@plotly_theme_decorator
def plot_derived_metric_correlations(simulation_results, min_rate=0):
    """
    Creates a heatmap showing correlations among derived metrics.
    
    Args:
        simulation_results (pd.DataFrame): The simulation results dataframe
        min_rate (int, optional): The minimum rate to filter by. Defaults to 0.
        
    Returns:
        plotly.graph_objects.Figure: The correlation heatmap figure
    """
    # Derived metrics (calculated from the simulation results)
    derived_metrics = [
        'disparity_ratio',
        'rate_difference',
        'rate_disadv',
        'disadv_delta_from_avg_percent',
        'rate_adv',
        'adv_delta_from_avg_percent',
        'normalized_disparity_index',
    ]

    # Filter data for a specific min_rate to focus analysis
    plot_df = simulation_results[simulation_results['min_rate']==min_rate]

    # Create a correlation matrix for derived metrics only
    derived_corr = plot_df[derived_metrics].corr()
    mask = np.triu(np.ones_like(derived_corr, dtype=bool))
    derived_corr_masked = derived_corr.copy()
    derived_corr_masked.values[mask] = None

    # Create a heatmap for derived metrics only
    fig = go.Figure(data=go.Heatmap(
        z=derived_corr_masked.values,
        x=derived_corr.columns,
        y=derived_corr.index,
        colorscale='RdBu_r',
        zmid=0,
        zmin=-1, zmax=1,
        text=np.where(np.isnan(derived_corr_masked.values), '', np.round(derived_corr_masked.values, 2)),
        texttemplate='%{text:.2f}',
        hoverinfo='text',
        colorbar=dict(title='Correlation'),
    ))

    fig.update_layout(
        title=f'Correlation Among Derived Metrics (min_rate={min_rate})',
        title_font_size=16,
        width=700,
        height=500,
        xaxis=dict(tickangle=-45),
        yaxis=dict(autorange='reversed'),
        template='plotly_white'
    )
    
    return fig

@plotly_theme_decorator
def create_disparity_probability_plot(simulation_results, min_rate_value=None):
    """
    Creates a stacked area plot showing the probability of different disparity ratio categories
    across group sizes, aggregating across all gamma and position gap values.
    
    Args:
        simulation_results (pd.DataFrame): DataFrame containing simulation results
        min_rate_value (float, optional): Specific min_rate value to filter by
        
    Returns:
        plotly.graph_objects.Figure: The created figure
    """
    # Define disparity ratio buckets
    plot_df = simulation_results.copy()
    plot_df['disparity_bucket'] = pd.cut(plot_df['disparity_ratio'], 
                                        bins=[0, 2, 4, 10, 30, float('inf')],
                                        labels=['Low (1-2)', 'Moderate (2-4)', 
                                               'High (5-10)', 'Very High (10-30)',
                                               'Extreme (30+)'])

    # Filter data based on provided min_rate parameter
    if min_rate_value is not None:
        plot_df = plot_df[plot_df['min_rate'] == min_rate_value]
    
    # Calculate probability of each bucket for each prop_disadv value
    # This aggregates across all gamma and position gap values
    prob_df = (plot_df.groupby(['prop_disadv', 'disparity_bucket'])
               .size()
               .unstack(fill_value=0))

    # Convert to probabilities
    prob_df = prob_df.div(prob_df.sum(axis=1), axis=0)

    # Convert to long format for plotting
    prob_df_long = prob_df.reset_index().melt(id_vars=['prop_disadv'],
                                             var_name='Disparity Category',
                                             value_name='Probability')

    # Create title with parameter information
    title = 'Probability of Disparity Ratio Categories by Group Size'
    if min_rate_value is not None:
        title += f' (Min Rate={min_rate_value})'
    subtitle= 'Aggregated Across All Gamma and Position Gap Values'

    # Create stacked area plot
    fig = px.area(prob_df_long,
                  x='prop_disadv',
                  y='Probability', 
                  color='Disparity Category',
                  color_discrete_sequence=px.colors.qualitative.Set2,
                  title=title,
                  subtitle=subtitle,
                  labels={'prop_disadv': 'Proportion of Disadvantaged Group',
                         'Probability': 'Probability of Observing'},
                  )

    fig.update_layout(
        xaxis_title='Proportion of Disadvantaged Group',
        yaxis_title='Probability',
        legend_title='Disparity Category',
    )
            
    return fig

def create_simulation_3d_plot(simulation_results, z_col='disparity_ratio', min_rate=0, color_col='z_position_gap', **kwargs):
    """
    Creates a 3D scatter plot of simulation results with customizable z-axis and color dimension.
    
    Args:
        simulation_results (pd.DataFrame): DataFrame containing simulation results
        z_col (str, optional): Column to use for z-axis. Defaults to 'disparity_ratio'.
        min_rate (int, optional): Minimum incarceration rate to filter by. Defaults to 0.
        color_col (str, optional): Column to use for color dimension. Defaults to 'z_position_gap'.
        **kwargs: Additional arguments to pass to create_3d_scatter
        
    Returns:
        plotly.graph_objects.Figure: The created 3D scatter plot
    """
    plot_df = simulation_results[simulation_results['min_rate']==min_rate]
    
    # Set default parameters that can be overridden by kwargs
    params = {
        'x_col': 'prop_disadv',
        'y_col': 'gamma',
        'color_continuous_scale': 'Turbo',
        'hover_data': plot_df.columns.tolist(),
    }
    
    # Add log_z=True by default only for disparity_ratio
    if z_col == 'disparity_ratio':
        params['log_z'] = True
    
    # Override defaults with any provided kwargs
    params.update(kwargs)
    
    fig = create_3d_scatter(
        plot_df,
        z_col=z_col,
        color_col=color_col,
        **params
    )
    
    # Create a descriptive title
    title = f"Parameter Space Analysis: Impact on {z_col.replace('_', ' ').title()}"
    if min_rate > 0:
        title += f" (Min Rate={min_rate})"
    
    # Add better labels for axes and title
    fig.update_layout(
        title=title,
        scene=dict(
            xaxis=dict(title="Proportion of Disadvantaged Group"),
            yaxis=dict(title="Stratification Parameter (γ)"),
        )
    )
    
    # Add specific z-axis label if it's disparity ratio
    if z_col == 'disparity_ratio':
        fig.update_layout(
            scene=dict(
                zaxis=dict(title="Disparity Ratio (log scale)")
            )
        )
    # For other z values, add a formatted label
    else:
        fig.update_layout(
            scene=dict(
                zaxis=dict(title=z_col.replace('_', ' ').title())
            )
        )
    
    if color_col == 'z_position_gap':
        fig.update_layout(
            coloraxis=dict(
                colorbar=dict(
                    title="Position Gap Between Groups"
                )
            )
        )
    else:
        fig.update_layout(
            coloraxis=dict(
                colorbar=dict(
                    title=color_col.replace('_', ' ').title()
                )
            )
        )
    
    return fig