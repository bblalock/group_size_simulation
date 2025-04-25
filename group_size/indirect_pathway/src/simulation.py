import numpy as np
import os
import pandas as pd
from core.simulation import run_factorial_simulation
from core.utils.io import save_figure, save_simulation_data
from model.indirect_effect import (
    indirect_model_incarceration_rate,
    generate_stratification_positions,
    calculate_incarceration_rates_normalized
)
from direct_pathway.src.visualization.plots import calculate_deviation_metrics
from indirect_pathway.app.constants import APP_DATA_PATH
from indirect_pathway.src.visualization.plots import (
    plot_parameter_metric_correlations,
    plot_derived_metric_correlations,
    create_disparity_probability_plot,
    create_simulation_3d_plot,
    create_stratification_plot,
    create_position_to_rate_plot,
    create_incarceration_rate_plot
)


INDIRECT_PATHWAY_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR_DATA = os.path.join(INDIRECT_PATHWAY_ROOT, "output", "data")
OUTPUT_DIR_FIGURES = os.path.join(INDIRECT_PATHWAY_ROOT, "output", "figures")

if __name__ == "__main__":
    """
    Run factorial simulations for the indirect pathway model exploring how group size,
    stratification distributions, and the shape parameter affect measured inequality
    in incarceration rates.
    """
    # Create output directories if they don't exist
    os.makedirs(OUTPUT_DIR_DATA, exist_ok=True)
    os.makedirs(OUTPUT_DIR_FIGURES, exist_ok=True)
    
    # Define parameter ranges
    
    # VARYING PARAMETERS
    # ----------------------------------
    # Group size parameter - similar to README population proportions
    p_values = np.linspace(0.001, .99, 20)   # Group proportion values (disadvantaged group)
    
    # Stratification gap parameter - difference in economic position between groups
    z_position_gap_values = np.arange(0, .9, .2)
    
    # Shape parameter affecting incarceration risk given economic position
    gamma_values = np.linspace(0.1, 5, 20)
    
    # Minimum incarceration rate (floor) - varies the baseline risk
    floor_rate_values = np.linspace(0, 500, 20)
    
    # FIXED PARAMETERS (held constant across simulations)
    # ----------------------------------
    # Distribution parameters for economic position
    mu_disadv_values = [0.2]  # Mean position of disadvantaged group
    c_disadv_values = [20]    # Concentration parameter for disadvantaged group
    c_adv_values = [20]       # Concentration parameter for advantaged group
    
    # Target average incarceration rate (per 100,000)
    target_avg_rate_values = [500] 
    
    # Sample size for each simulation run
    sample_size_values = np.array([10000])
    
    # Calculate total number of simulation runs
    n_results = (len(p_values) * len(gamma_values) * len(floor_rate_values) * 
                len(mu_disadv_values) * len(z_position_gap_values) * 
                len(c_disadv_values) * len(c_adv_values) * 
                len(sample_size_values))
    
    print(f'{n_results} simulations')
    
    # Define model configurations
    model_configs = [
        {
            'name': 'normalized_indirect',
            'function': indirect_model_incarceration_rate,
            'param_dict': {
                'p': p_values,
                'gamma': gamma_values,
                'mu_disadv': mu_disadv_values,
                'z_position_gap': z_position_gap_values,
                'c_disadv': c_disadv_values,
                'c_adv': c_adv_values,
                'sample_size': sample_size_values,
                'normalized': [True],
                'target_avg_rate': target_avg_rate_values,
                'min_rate': floor_rate_values
            }
        },
    ]
    
    # Run simulations for all models
    results = []
    for config in model_configs:
        print(f"Running {config['name']} Model simulation...")
        df = run_factorial_simulation(
            config['function'],
            config['param_dict'],
        )
        results.append(df)
        
        # Save individual model results
        save_simulation_data(df, f"{config['name'].lower()}_simulation.csv", output_dir=OUTPUT_DIR_DATA)
        save_simulation_data(df, f"{config['name'].lower()}_simulation.csv", output_dir=APP_DATA_PATH)
        
        # Create and save visualizations
        print(f"Creating visualizations for {config['name']} Model...")
        
        # 1. Correlation Heatmap - Unconstrained model (floor_rate = 0)
        print("Generating parameter-metric correlation heatmap (unconstrained)...")
        df = calculate_deviation_metrics(df)
        df['z_position_gap'] = np.round(df['z_position_gap'],1)
        unconstrained_df = df[df['min_rate'] == 0]
        if not unconstrained_df.empty:
            fig_corr_unconstrained = plot_parameter_metric_correlations(
                simulation_results=unconstrained_df,
                min_rate=0
            )
            save_figure(fig_corr_unconstrained, f"{config['name'].lower()}_correlation_heatmap_unconstrained", 
                        output_dir=OUTPUT_DIR_FIGURES)
            
            # 2. Probability Distribution Visualization (unconstrained)
            print("Generating disparity probability distribution (unconstrained)...")
            fig_prob_unconstrained = create_disparity_probability_plot(
                simulation_results=unconstrained_df,
                min_rate_value=0
            )
            save_figure(fig_prob_unconstrained, f"{config['name'].lower()}_disparity_probability_unconstrained", 
                        output_dir=OUTPUT_DIR_FIGURES)
            
            # 3. Parameter Space 3D visualization (unconstrained)
            print("Generating 3D parameter space visualization (unconstrained)...")
            fig_3d_unconstrained = create_simulation_3d_plot(
                simulation_results=unconstrained_df,
                z_col='disparity_ratio',
                min_rate=0,
                color_col='z_position_gap', 
                width=900, height=700
            )
            save_figure(fig_3d_unconstrained, f"{config['name'].lower()}_3d_parameter_space_unconstrained", 
                        output_dir=OUTPUT_DIR_FIGURES)
        
        # Get a representative non-zero floor rate value from the simulation parameters
        constrained_floor_rate = floor_rate_values[5] if len(floor_rate_values) > 1 else floor_rate_values[0]
        constrained_df = df[df['min_rate'] == constrained_floor_rate]
        
        if not constrained_df.empty:
            # 4. Disparity Probability Distribution (constrained)
            print(f"Generating disparity probability distribution (floor_rate={constrained_floor_rate})...")
            fig_prob_constrained = create_disparity_probability_plot(
                simulation_results=constrained_df,
                min_rate_value=constrained_floor_rate
            )
            save_figure(fig_prob_constrained, f"{config['name'].lower()}_disparity_probability_constrained", 
                        output_dir=OUTPUT_DIR_FIGURES)
            
            # 5. Correlation Heatmap (constrained)
            print(f"Generating parameter-metric correlation heatmap (floor_rate={constrained_floor_rate})...")
            fig_corr_constrained = plot_parameter_metric_correlations(
                simulation_results=constrained_df,
                min_rate=constrained_floor_rate
            )
            save_figure(fig_corr_constrained, f"{config['name'].lower()}_correlation_heatmap_constrained", 
                        output_dir=OUTPUT_DIR_FIGURES)
            
            # 6. Parameter Space 3D visualization (constrained)
            print(f"Generating 3D parameter space visualization (floor_rate={constrained_floor_rate})...")
            fig_3d_constrained = create_simulation_3d_plot(
                simulation_results=constrained_df,
                z_col='disparity_ratio',
                min_rate=constrained_floor_rate,
                color_col='z_position_gap', 
                width=900, height=700
            )
            save_figure(fig_3d_constrained, f"{config['name'].lower()}_3d_parameter_space_constrained", 
                        output_dir=OUTPUT_DIR_FIGURES)
            
            # Additional visualization: Derived metric correlations
            print(f"Generating derived metric correlation heatmap (floor_rate={constrained_floor_rate})...")
            fig_derived_corr = plot_derived_metric_correlations(
                simulation_results=constrained_df,
                min_rate=constrained_floor_rate
            )
            save_figure(fig_derived_corr, f"{config['name'].lower()}_derived_metric_correlations", 
                        output_dir=OUTPUT_DIR_FIGURES)
        
        # Generate mechanism explanation plots
        print("Generating mechanism explanation plots...")
        
        # Use fixed parameters from the simulation
        p = 0.15  # Proportion of disadvantaged group
        mu_disadv = mu_disadv_values[0]  # Mean position of disadvantaged group
        z_position_gap = 0.3  # Fixed position gap
        c_disadv = c_disadv_values[0]  # Concentration parameter for disadvantaged group
        c_adv = c_adv_values[0]  # Concentration parameter for advantaged group
        sample_size = sample_size_values[0]  # Sample size
        target_avg_rate = target_avg_rate_values[0]  # Target average incarceration rate
        
        # Generate positions for stratification plot
        positions = generate_stratification_positions(
            p=p,
            mu_disadv=mu_disadv,
            z_position_gap=z_position_gap,
            c_disadv=c_disadv,
            c_adv=c_adv,
            sample_size=sample_size,
        )
        
        # Create stratification plot
        print("Generating stratification position distribution plot...")
        stratification_fig = create_stratification_plot(
            positions=positions,
            width=900, height=700
        )
        # Update title and subtitle after generating the plot
        stratification_fig.update_layout(
            title=dict(
                text="Stratification Position Distribution",
                subtitle=dict(
                    text=f"p={p}, μ_disadv={mu_disadv}, z_gap={z_position_gap}, c_disadv={c_disadv}, c_adv={c_adv}"
                )
            )
        )
        save_figure(stratification_fig, f"{config['name'].lower()}_stratification_distribution", 
                    output_dir=OUTPUT_DIR_FIGURES)
        
        # Create position-to-rate plot with gamma=1 (with floor rate)
        print("Generating position-to-rate function plot with floor rate...")
        gamma_position_rate = 1.0
        floor_rate = constrained_floor_rate
        
        # Get norm factors for different gamma values with floor rate
        norm_factors_with_floor = {
            'gamma': {
                'value': gamma_position_rate,
                'factors': calculate_incarceration_rates_normalized(
                    positions=positions,
                    gamma=gamma_position_rate,
                    target_avg_rate=target_avg_rate,
                    floor_rate=floor_rate,
                    return_only_factors=True
                )
            },
            'gamma-1': {
                'value': max(gamma_position_rate-1, 0),
                'factors': calculate_incarceration_rates_normalized(
                    positions=positions,
                    gamma=max(gamma_position_rate-1, 0),
                    target_avg_rate=target_avg_rate,
                    floor_rate=floor_rate,
                    return_only_factors=True
                )
            },
            'gamma+1': {
                'value': gamma_position_rate+1,
                'factors': calculate_incarceration_rates_normalized(
                    positions=positions,
                    gamma=gamma_position_rate+1,
                    target_avg_rate=target_avg_rate,
                    floor_rate=floor_rate,
                    return_only_factors=True
                )
            }
        }
        
        position_to_rate_fig_with_floor = create_position_to_rate_plot(
            gamma=gamma_position_rate,
            target_avg_rate=target_avg_rate,
            floor_rate=floor_rate,
            norm_factors=norm_factors_with_floor,
            width=900, height=700
        )
        # Update title and subtitle after generating the plot
        position_to_rate_fig_with_floor.update_layout(
            title=dict(
                text="Position to Incarceration Rate Function (With Floor Rate)",
                subtitle=dict(
                    text=f"γ={gamma_position_rate}, target_rate={target_avg_rate}, floor_rate={floor_rate}"
                )
            )
        )
        save_figure(position_to_rate_fig_with_floor, f"{config['name'].lower()}_position_to_rate_function_with_floor", 
                    output_dir=OUTPUT_DIR_FIGURES)
        
        # Create position-to-rate plot with gamma=1 (without floor rate)
        print("Generating position-to-rate function plot without floor rate...")
        no_floor_rate = 0.0
        
        # Get norm factors for different gamma values without floor rate
        norm_factors_no_floor = {
            'gamma': {
                'value': gamma_position_rate,
                'factors': calculate_incarceration_rates_normalized(
                    positions=positions,
                    gamma=gamma_position_rate,
                    target_avg_rate=target_avg_rate,
                    floor_rate=no_floor_rate,
                    return_only_factors=True
                )
            },
            'gamma-1': {
                'value': max(gamma_position_rate-1, 0),
                'factors': calculate_incarceration_rates_normalized(
                    positions=positions,
                    gamma=max(gamma_position_rate-1, 0),
                    target_avg_rate=target_avg_rate,
                    floor_rate=no_floor_rate,
                    return_only_factors=True
                )
            },
            'gamma+1': {
                'value': gamma_position_rate+1,
                'factors': calculate_incarceration_rates_normalized(
                    positions=positions,
                    gamma=gamma_position_rate+1,
                    target_avg_rate=target_avg_rate,
                    floor_rate=no_floor_rate,
                    return_only_factors=True
                )
            }
        }
        
        position_to_rate_fig_no_floor = create_position_to_rate_plot(
            gamma=gamma_position_rate,
            target_avg_rate=target_avg_rate,
            floor_rate=no_floor_rate,
            norm_factors=norm_factors_no_floor,
            width=900, height=700
        )
        # Update title and subtitle after generating the plot
        position_to_rate_fig_no_floor.update_layout(
            title=dict(
                text="Position to Incarceration Rate Function (No Floor Rate)",
                subtitle=dict(
                    text=f"γ={gamma_position_rate}, target_rate={target_avg_rate}, floor_rate={no_floor_rate}"
                )
            )
        )
        save_figure(position_to_rate_fig_no_floor, f"{config['name'].lower()}_position_to_rate_function_no_floor", 
                    output_dir=OUTPUT_DIR_FIGURES)
        
        # Create incarceration rate plot with gamma=2 (for interaction visualization)
        print("Generating incarceration rate interaction plot...")
        gamma_interaction = 2.0
        
        # Calculate incarceration rates with gamma=2
        rate_data = calculate_incarceration_rates_normalized(
            positions=positions,
            gamma=gamma_interaction,
            target_avg_rate=target_avg_rate,
            floor_rate=floor_rate
        )
        
        # Get norm factors for gamma=2
        interaction_norm_factors = calculate_incarceration_rates_normalized(
            positions=positions,
            gamma=gamma_interaction,
            target_avg_rate=target_avg_rate,
            floor_rate=floor_rate,
            return_only_factors=True
        )
        
        incarceration_fig = create_incarceration_rate_plot(
            rate_data=rate_data,
            gamma=gamma_interaction,
            target_avg_rate=target_avg_rate,
            positions=positions,
            norm_factors=interaction_norm_factors,
            width=900, height=700
        )
        # Update title and subtitle after generating the plot
        incarceration_fig.update_layout(
            title=dict(
                text="Incarceration Rate Interaction",
                subtitle=dict(
                    text=f"p={p}, γ={gamma_interaction}, z_gap={z_position_gap}, target_rate={target_avg_rate}, floor_rate={floor_rate}"
                )
            )
        )
        save_figure(incarceration_fig, f"{config['name'].lower()}_incarceration_rate_interaction", 
                    output_dir=OUTPUT_DIR_FIGURES)
