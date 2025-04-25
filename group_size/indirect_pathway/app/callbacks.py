from dash.dependencies import Input, Output
from dash import html
import dash_bootstrap_components as dbc
import numpy as np

from indirect_pathway.src.model.indirect_effect import generate_stratification_positions, calculate_incarceration_rates_normalized
from indirect_pathway.src.visualization.plots import (
    create_incarceration_rate_plot, create_stratification_plot, create_position_to_rate_plot,
    plot_parameter_metric_correlations,
    plot_derived_metric_correlations,
    create_disparity_probability_plot,
    create_simulation_3d_plot
)
from constants import PLOT_HEIGHT

def register_callbacks(app, simulation_results):
    @app.callback(
        [Output('incarceration-plot', 'figure'),
         Output('position-distribution-plot', 'figure'),
         Output('position-to-rate-plot', 'figure'),
         Output('stats-container', 'children')],
        [Input('sample-size-slider', 'value'),
         Input('p-slider', 'value'),
         Input('mu-disadv-slider', 'value'),
         Input('z-position-gap-slider', 'value'),
         Input('c-disadv-slider', 'value'),
         Input('c-adv-slider', 'value'),
         Input('gamma-slider', 'value'),
         Input('target-rate-slider', 'value'),
         Input('floor-rate-slider', 'value'),
         Input('population-average-rate-slider', 'value')]
    )
    def update_graph(sample_size, p, mu_disadv, z_position_gap, c_disadv, c_adv, gamma, target_avg_rate, floor_rate, population_avg_rate):
        # Generate positions
        positions = generate_stratification_positions(
            p=p,
            mu_disadv=mu_disadv,
            z_position_gap=z_position_gap,
            c_disadv=c_disadv,
            c_adv=c_adv,
            sample_size=sample_size,
        )
        
        # Calculate incarceration rates
        rate_data = calculate_incarceration_rates_normalized(
            positions=positions,
            gamma=gamma,
            target_avg_rate=population_avg_rate,
            floor_rate=floor_rate
        )
        
        # Get positions for additional gamma values
        positions_for_factors = positions
        
        # Get norm factors for different gamma values
        norm_factors = {
            'gamma': {
                'value': gamma,
                'factors': {
                    'first_norm_factor': rate_data['first_norm_factor'],
                    'second_norm_factor': rate_data['second_norm_factor'],
                    'total_norm_factor': rate_data['total_norm_factor']
                }
            },
            'gamma-1': {
                'value': max(gamma-1, 0),
                'factors': calculate_incarceration_rates_normalized(
                    positions=positions_for_factors,
                    gamma=max(gamma-1, 0),
                    target_avg_rate=population_avg_rate,
                    floor_rate=floor_rate,
                    return_only_factors=True
                )
            },
            'gamma+1': {
                'value': gamma+1,
                'factors': calculate_incarceration_rates_normalized(
                    positions=positions_for_factors,
                    gamma=gamma+1,
                    target_avg_rate=population_avg_rate,
                    floor_rate=floor_rate,
                    return_only_factors=True
                )
            }
        }
        
        # Create plots
        incarceration_fig = create_incarceration_rate_plot(
            rate_data=rate_data,
            gamma=gamma,
            target_avg_rate=population_avg_rate,
            positions=positions,
            norm_factors=norm_factors['gamma']['factors'],
            height=PLOT_HEIGHT 
        )

        position_fig = create_stratification_plot(
            positions=positions,
            height=PLOT_HEIGHT
        )

        position_to_rate_fig = create_position_to_rate_plot(
            gamma=gamma,
            target_avg_rate=population_avg_rate,
            floor_rate=floor_rate,
            norm_factors=norm_factors,
            height=PLOT_HEIGHT
        )
        
        # Create statistics display
        stats = html.Div([
            dbc.Row([
                dbc.Col([
                    html.P([
                        html.Strong("Disadvantaged Group Rate: "), 
                        f"{rate_data['rate_disadv']:.1f} per 100,000"
                    ]),
                    html.P([
                        html.Strong("Advantaged Group Rate: "), 
                        f"{rate_data['rate_adv']:.1f} per 100,000"
                    ])
                ], width=4),
                dbc.Col([
                    html.P([
                        html.Strong("Population Average Rate: "), 
                        f"{rate_data['pop_avg_rate']:.1f} per 100,000"
                    ]),
                    html.P([
                        html.Strong("Disparity Ratio: "), 
                        f"{rate_data['rate_disadv'] / rate_data['rate_adv']:.2f}"
                    ])
                ], width=4),
                dbc.Col([
                    html.P([
                        html.Strong("Disparity Difference: "), 
                        f"{rate_data['rate_disadv'] - rate_data['rate_adv']:.1f} per 100,000"
                    ]),
                    html.P([
                        html.Strong("Normalized Disparity Index (η): "), 
                        f"{(rate_data['rate_disadv'] / rate_data['rate_adv'] - 1) / (rate_data['rate_disadv'] / rate_data['rate_adv'] + (1-p)/p):.3f}"
                    ])
                ], width=4)
            ])
        ])
        
        return incarceration_fig, position_fig, position_to_rate_fig, stats
    
    
    # Add new callback for parameter space analysis
    @app.callback(
        [Output('param-metric-correlation-plot', 'figure'),
         Output('derived-metric-correlation-plot', 'figure'),
         Output('disparity-probability-plot', 'figure'),
         Output('simulation-3d-plot', 'figure')],
        [Input('param-space-floor-rate-slider', 'value'),
         Input('z-axis-variable-dropdown', 'value'),
         Input('color-variable-dropdown', 'value')]
    )
    def update_parameter_space_plots(floor_rate, z_axis_variable, color_variable):
        # You'll need to load or generate simulation_results here
        # This should be your DataFrame containing the simulation results
        # For now, I'll assume it's loaded from somewhere
        
        # Create all plots
        param_corr = plot_parameter_metric_correlations(
            simulation_results=simulation_results,
            min_rate=floor_rate
        )
        
        derived_corr = plot_derived_metric_correlations(
            simulation_results=simulation_results,
            min_rate=floor_rate
        )
        
        prob_plot = create_disparity_probability_plot(
            simulation_results=simulation_results,
            min_rate_value=floor_rate,
            height=PLOT_HEIGHT
        )
        
        sim_3d = create_simulation_3d_plot(
            simulation_results=simulation_results,
            min_rate=floor_rate,
            z_col=z_axis_variable,
            color_col=color_variable,
            height=PLOT_HEIGHT
        )
        
        return param_corr, derived_corr, prob_plot, sim_3d