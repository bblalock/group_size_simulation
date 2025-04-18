import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd

from core.visualization.style import plotly_theme_decorator
from core.visualization.base_plots import create_3d_scatter, create_box_plot
    

def create_disparity_ratio_label(disparity_ratio):
    """
    Create a standardized label for disparity ratio ranges.

    Parameters:
    -----------
    disparity_ratio : float
        The disparity ratio value

    Returns:
    --------
    str
        Formatted label for the disparity ratio range
    """
    if disparity_ratio == 1:
        return '1-1.49'
    elif disparity_ratio == 10:
        return '9.5-10'
    else:
        return f'{disparity_ratio-0.5}-{disparity_ratio+0.49}'


def calculate_deviation_metrics(data):
    """
    Calculate deviation metrics for disadvantaged groups.

    Parameters:
    -----------
    data : pandas.DataFrame
        DataFrame containing simulation results with rate_disadv and pop_avg columns

    Returns:
    --------
    pandas.DataFrame
        DataFrame with added deviation metrics
    """
    # Create a copy to avoid modifying the original
    df = data.copy()

    # Calculate absolute deviation
    df['disadv_delta_from_avg'] = df['rate_disadv'] - df['pop_avg']

    # Calculate percentage deviation
    df['disadv_delta_from_avg_percent'] = (
        df['rate_disadv'] - df['pop_avg']) / df['pop_avg'] * 100
    df['adv_delta_from_avg_percent'] = (
        df['rate_adv'] - df['pop_avg']) / df['pop_avg'] * 100

    # Round the disparity ratio for grouping
    df['disparity_ratio_rounded'] = df['disparity_ratio'].apply(np.round)

    # Add disparity ratio labels
    df['disparity_ratio_label'] = df['disparity_ratio_rounded'].apply(
        create_disparity_ratio_label)

    return df


def bin_proportion_disadvantaged(data, bins=None, labels=None):
    """
    Create bins for proportion disadvantaged.

    Parameters:
    -----------
    data : pandas.DataFrame
        DataFrame containing simulation results with prop_disadv column
    bins : list, optional
        List of bin edges. Default is [0, 0.25, 0.5, 0.75, 1.0]
    labels : list, optional
        List of labels for the bins. Default is standard minority/majority labels.

    Returns:
    --------
    pandas.DataFrame
        DataFrame with added prop_disadv_binned column
    """
    # Create a copy to avoid modifying the original
    df = data.copy()

    # Default bins and labels if not provided
    if bins is None:
        bins = [0, 0.25, 0.5, 0.75, 1.0]

    if labels is None:
        labels = ['Small Minority (0-25%)', 'Minority (26-50%)',
                  'Majority (51-75%)', 'Large Majority (76-100%)']

    # Create the binned column
    df['prop_disadv_binned'] = pd.cut(df['prop_disadv'],
                                      bins=bins,
                                      labels=labels,
                                      include_lowest=True)

    return df


@plotly_theme_decorator
def create_explanatory_visual(standard_sim_data, exemplar_pop_avg=200, exemplar_prop_disadv=[0.1, 0.5, 0.9], height=1000, width=1000, relative=False):
    """
    Creates an explanatory visualization showing incarceration rates by disparity ratio and group size.

    Parameters:
    -----------
    standard_sim_data : pandas.DataFrame
        Simulation data containing columns for pop_avg, prop_disadv, disparity_ratio, rate_adv, rate_disadv
    exemplar_pop_avg : float, default=200
        Population average to filter the data
    exemplar_prop_disadv : list, default=[0.1, 0.5, 0.9]
        List of proportions of disadvantaged population to include in the visualization
    height : int, default=1000
        Height of the figure in pixels
    width : int, default=1000
        Width of the figure in pixels
    relative : bool, default=False
        If True, plot percent deviation from population average instead of raw rates

    Returns:
    --------
    plotly.graph_objects.Figure
        The visualization figure
    """

    # Filter data based on parameters
    filtered_explanatory_data = standard_sim_data[standard_sim_data['pop_avg']
                                                  == exemplar_pop_avg]
    filtered_explanatory_data = filtered_explanatory_data[filtered_explanatory_data['prop_disadv'].isin(
        exemplar_prop_disadv)]

    if relative:
        # Calculate deviation metrics if plotting relative values
        filtered_explanatory_data = calculate_deviation_metrics(
            filtered_explanatory_data)

        # Create melted dataframe with percent deviations
        melted_df = pd.melt(
            filtered_explanatory_data,
            id_vars=['prop_disadv', 'disparity_ratio'],
            value_vars=['adv_delta_from_avg_percent',
                        'disadv_delta_from_avg_percent'],
            var_name='group',
            value_name='percent_deviation'
        )
        melted_df['group'] = melted_df['group'].str.replace(
            '_delta_from_avg_percent', '')

        # Create the figure
        fig = px.bar(
            data_frame=melted_df,
            x='disparity_ratio',
            y='percent_deviation',
            barmode='group',
            color='group',
            facet_row='prop_disadv',
            facet_row_spacing=0.01,
            labels={
                'disparity_ratio': 'Disparity Ratio',
                'percent_deviation': 'Deviation (%)',
                'group': 'Group',
                'prop_disadv': 'Proportion Disadvantaged'
            },
            title='Simulated Incarceration Rate Deviation from Population Average by Disparity Ratio and Group Size',
        )

        # Add horizontal line at 0% (population average)
        fig.add_hline(y=0)
    else:
        # Create melted dataframe with raw rates
        melted_df = pd.melt(
            filtered_explanatory_data,
            id_vars=['prop_disadv', 'disparity_ratio'],
            value_vars=['rate_adv', 'rate_disadv'],
            var_name='group',
            value_name='rate'
        )
        melted_df['group'] = melted_df['group'].str.replace('rate_', '')

        # Create the figure
        fig = px.bar(
            data_frame=melted_df,
            x='disparity_ratio',
            y='rate',
            barmode='group',
            color='group',
            facet_row='prop_disadv',
            facet_row_spacing=0.01,
            labels={
                'disparity_ratio': 'Disparity Ratio',
                'rate': 'Incarceration Rate',
                'group': 'Group',
                'prop_disadv': 'Proportion Disadvantaged'
            },
            title='Simulated Incarceration Rates by Disparity Ratio and Group Size',
        )

        # Add horizontal line at population average
        fig.add_hline(y=exemplar_pop_avg)

    # Make y-axes independent for each subplot
    fig.update_yaxes(matches=None)

    return fig


@plotly_theme_decorator
def plot_3d_simulation_results(standard_sim_data,
                               x='prop_disadv',
                               y='disadv_delta_from_avg_percent',
                               z='disparity_ratio',
                               color='bias_parameter',
                               **kwargs
                               ):
    """
    Create a 3D scatter plot showing the relationship between proportion disadvantaged,
    disadvantaged group's deviation from population average, and disparity ratio,
    colored by bias parameter.

    Parameters
    ----------
    standard_sim_data : pandas.DataFrame
        DataFrame containing simulation results
    height : int, default=800
        Height of the figure in pixels
    width : int, default=1000
        Width of the figure in pixels

    Returns
    -------
    plotly.graph_objects.Figure
        3D scatter plot figure
    """

    # Calculate deviation metrics
    data = calculate_deviation_metrics(standard_sim_data)

    # Create a 3D scatter plot with all data columns as hover data
    fig = create_3d_scatter(
        df=data,
        x_col=x,
        y_col=y,
        z_col=z,
        color_col=color,
        color_continuous_scale='Turbo',
        # color_continuous_midpoint=0.5,
        opacity=0.5,
        hover_data=data.columns.tolist(),
        **kwargs
    )

    # Improve layout
    fig.update_layout(
        title='Population Average vs Disparity Ratio vs Proportion Disadvantaged',
        scene=dict(
            xaxis_title='Proportion Disadvantaged',
            yaxis_title='Disadvantaged Group Deviation (%)',
            zaxis_title='Disparity Ratio'
        ),
        scene_camera=dict(
            up=dict(x=0, y=0, z=1),       # The 'up' direction
            center=dict(x=-0, y=0, z=0),   # The center point of the view
            eye=dict(x=-1.48, y=-1.70, z=0.8)  # Camera position
        ),
        margin=dict(l=0, r=0, b=0, t=40),
        coloraxis_colorbar=dict(
            title='Bias Parameter'
        )
    )

    # Add a plane at x=0.5 to highlight that value
    # Get the y and z ranges from the data
    y_min, y_max = min(data[y]), max(data[y])
    z_min, z_max = min(data[z]), max(data[z])
    # z_min, z_max = min(data['disparity_ratio']), max(data['disparity_ratio'])

    # Create a grid of points for the plane
    y_vals = np.linspace(y_min, y_max, 10)
    z_vals = np.linspace(z_min, z_max, 10)
    y_grid, z_grid = np.meshgrid(y_vals, z_vals)
    x_grid = np.full_like(y_grid, 0.5)  # x=0.5 plane

    # Add the plane as a surface
    plane = go.Surface(
        x=x_grid,
        y=y_grid,
        z=z_grid,
        # Semi-transparent black
        colorscale=[[0, 'rgba(0,0,0,0.2)'], [1, 'rgba(0,0,0,0.2)']],
        showscale=False,
        name='x=0.5'
    )

    fig.add_trace(plane)

    return fig


@plotly_theme_decorator
def plot_prop_disadv_to_bias_by_ratio(data, height=800, width=1000, n_std=1):
    """
    Create a line plot showing the relationship between proportion disadvantaged and bias parameter,
    with lines grouped by rounded disparity ratios and confidence bands.

    Parameters:
    -----------
    data : pd.DataFrame
        DataFrame containing the simulation data
    height : int, default=800
        Height of the figure in pixels
    width : int, default=1000
        Width of the figure in pixels

    Returns:
    --------
    plotly.graph_objects.Figure
        The configured plotly figure
    """
    fig = go.Figure()

    # Round disparity ratios for grouping
    data['disparity_ratio_rounded'] = data['disparity_ratio'].apply(np.round)

    # Get unique rounded disparity ratios
    rounded_ratios = sorted(data['disparity_ratio_rounded'].unique())

    # Group by prop_disadv and disparity_ratio (rounded) to calculate mean and std for confidence bands
    grouped_data = data.groupby(['prop_disadv', 'disparity_ratio_rounded'])[
        'bias_parameter'].agg(['mean', 'std']).reset_index()

    # Add upper and lower bounds for confidence bands
    grouped_data['upper'] = grouped_data['mean'] + n_std*grouped_data['std']
    grouped_data['lower'] = grouped_data['mean'] - n_std*grouped_data['std']

    # Get a categorical color scale from plotly
    colors = px.colors.qualitative.D3

    # Add lines and confidence bands for each disparity ratio
    for i, disparity_ratio in enumerate(rounded_ratios):
        subset = grouped_data[grouped_data['disparity_ratio_rounded']
                              == disparity_ratio]

        # Sort by prop_disadv to ensure proper line connection
        subset = subset.sort_values('prop_disadv')

        # Get color from the categorical color scale (cycling if needed)
        color_idx = i % len(colors)
        color = colors[color_idx]

        # Create label for the rounded disparity ratio range
        label = create_disparity_ratio_label(disparity_ratio)

        # Add the main line
        fig.add_trace(
            go.Scatter(
                x=subset['prop_disadv'],
                y=subset['mean'],
                mode='lines',
                name=label,
                line=dict(color=color)
            )
        )

        # Add the confidence band
        fig.add_trace(
            go.Scatter(
                # x, then x reversed
                x=subset['prop_disadv'].tolist(
                ) + subset['prop_disadv'].tolist()[::-1],
                # upper, then lower reversed
                y=subset['upper'].tolist() + subset['lower'].tolist()[::-1],
                fill='toself',
                fillcolor=color,
                line=dict(color=color),
                hoverinfo="skip",
                showlegend=False,
                opacity=0.2
            )
        )

    # Update layout
    fig.update_layout(
        title='Relationship Between Proportion Disadvantaged and Bias Parameter by Disparity Ratio',
        xaxis_title='Proportion Disadvantaged',
        yaxis_title=f'Mean Bias Parameter (+/- {n_std} SD)',
        legend_title='Disparity Ratio Range'
    )

    return fig


@plotly_theme_decorator
def plot_disadv_deviation_from_avg(data, height=800, width=800, n_std=1):
    """
    Create a plot showing the disadvantaged group's incarceration rate deviation from population average
    with confidence bands.

    Parameters:
    -----------
    data : pandas.DataFrame
        DataFrame containing simulation results
    height : int, default=800
        Height of the figure in pixels
    width : int, default=800
        Width of the figure in pixels

    Returns:
    --------
    plotly.graph_objects.Figure
        The configured plotly figure
    """
    # Calculate deviation metrics
    data = calculate_deviation_metrics(data)

    # Group by prop_disadv and disparity_ratio (rounded) to calculate mean and std for confidence bands
    grouped_data = data.groupby(['prop_disadv', 'disparity_ratio_rounded'])[
        'disadv_delta_from_avg_percent'].agg(['mean', 'std']).reset_index()

    # Add upper and lower bounds for confidence bands
    grouped_data['upper'] = grouped_data['mean'] + n_std*grouped_data['std']
    grouped_data['lower'] = grouped_data['mean'] - n_std*grouped_data['std']

    # Create the base figure
    fig = go.Figure()

    # Get a categorical color scale from plotly
    colors = px.colors.qualitative.D3

    # Add lines and confidence bands for each disparity ratio
    for i, disparity_ratio in enumerate(sorted(grouped_data['disparity_ratio_rounded'].unique())):
        subset = grouped_data[grouped_data['disparity_ratio_rounded']
                              == disparity_ratio]

        # Get color from the categorical color scale (cycling if needed)
        color_idx = i % len(colors)
        color = colors[color_idx]

        # Create label for the rounded disparity ratio range
        label = create_disparity_ratio_label(disparity_ratio)

        # Add the main line
        fig.add_trace(
            go.Scatter(
                x=subset['prop_disadv'],
                y=subset['mean'],
                mode='lines',
                name=label,
                line=dict(color=color)
            )
        )

        # Add the confidence band
        fig.add_trace(
            go.Scatter(
                # x, then x reversed
                x=subset['prop_disadv'].tolist(
                ) + subset['prop_disadv'].tolist()[::-1],
                # upper, then lower reversed
                y=subset['upper'].tolist() + subset['lower'].tolist()[::-1],
                fill='toself',
                fillcolor=color,
                line=dict(color=color),
                hoverinfo="skip",
                showlegend=False,
                opacity=0.2
            )
        )

    # Update layout
    fig.update_layout(
        title='Disadvantaged Group Incarceration Rate Deviation from Population Average',
        xaxis_title='Proportion of Disadvantaged Group',
        yaxis_title=f'Mean Deviation (+/- {n_std} SD) from Population Average (%)',
        legend=dict(title='Disparity Ratio Range')
    )

    return fig


@plotly_theme_decorator
def plot_disadv_deviation_boxplot(standard_sim_data, height=700, width=1200, **kwargs):
    """
    Create a box plot showing the disadvantaged group's incarceration rate deviation 
    from population average by proportion group and disparity ratio.

    Parameters:
    -----------
    standard_sim_data : pandas.DataFrame
        DataFrame containing simulation results
    height : int, default=700

    Returns:
    --------
    plotly.graph_objects.Figure
        The configured plotly figure
    """
    # Calculate the difference between disadvantaged group rate and population average
    standard_sim_data['disadv_delta_from_avg'] = standard_sim_data['rate_disadv'] - \
        standard_sim_data['pop_avg']

    # Calculate the percent deviation from average
    standard_sim_data['disadv_delta_from_avg_percent'] = (
        standard_sim_data['rate_disadv'] - standard_sim_data['pop_avg']) / standard_sim_data['pop_avg'] * 100

    # Round the disparity ratio for grouping
    standard_sim_data['disparity_ratio_rounded'] = standard_sim_data['disparity_ratio'].apply(
        np.round)

    # Create label for the rounded disparity ratio range
    def create_disparity_label(disparity_ratio):
        if disparity_ratio == 1:
            return '1-1.49'
        elif disparity_ratio == 10:
            return '9.5-10'
        else:
            return f'{disparity_ratio-0.5}-{disparity_ratio+0.49}'

    standard_sim_data['disparity_ratio_label'] = standard_sim_data['disparity_ratio_rounded'].apply(
        create_disparity_label)

    # Create bins for prop_disadv (4 groups split at 50%)
    bins = [0, 0.25, 0.5, 0.75, 1.0]
    labels = ['Small Minority (0-25%)', 'Minority (26-50%)',
              'Majority (51-75%)', 'Large Majority (76-100%)']
    standard_sim_data['prop_disadv_binned'] = pd.cut(standard_sim_data['prop_disadv'],
                                                     bins=bins,
                                                     labels=labels,
                                                     include_lowest=True)

    # Create box plot with binned proportions on x-axis and colored by disparity ratio
    fig = create_box_plot(
        df=standard_sim_data,
        x_col='prop_disadv_binned',
        y_col='disadv_delta_from_avg_percent',
        color_col='disparity_ratio_label',
        color_discrete_sequence=px.colors.qualitative.D3,
        category_orders={"prop_disadv_binned": labels},
        **kwargs
    )

    # Update layout
    fig.update_layout(
        title='Disadvantaged Group Incarceration Rate Deviation from Population Average',
        xaxis_title='Proportion of Disadvantaged Group',
        yaxis_title='Deviation from Population Average (%)',
        legend=dict(title='Disparity Ratio Range')
    )

    return fig
