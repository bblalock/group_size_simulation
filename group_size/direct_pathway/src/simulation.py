import numpy as np
from model.direct_effect import (
    direct_pathway_model_incarceration_rate,
)
from visualization.plots import (
    create_explanatory_visual,
    plot_3d_simulation_results,
    plot_prop_disadv_to_bias_by_ratio,
    plot_disadv_deviation_from_avg,
    plot_disadv_deviation_boxplot
)

from core.simulation import run_factorial_simulation
from core.utils.io import save_figure, save_simulation_data
import os

DIRECT_PATHWAY_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR_DATA = os.path.join(DIRECT_PATHWAY_ROOT, "output", "data")
OUTPUT_DIR_FIGURES = os.path.join(DIRECT_PATHWAY_ROOT, "output", "figures")

if __name__ == "__main__":
    """
    Run factorial simulations for all three models exploring how group size 
    and various disparity parameters affect measured inequality in incarceration rates.
    """
    # Define parameter ranges
    p_values = np.round(np.arange(0.01, 1, 0.01), 2)  # Group proportion values from 0.1 to 1.0 with 100 values
    d_values = np.linspace(1, 10, 30)   # Disparity ratio values with 100 values
    avg_rate_values = np.linspace(50, 500, 100)  # Rate values per 100,000 with 100 values

    n_results = len(p_values)*len(d_values)*len(avg_rate_values)
    print(f'{n_results} simulations')
    
    # Define model configurations
    model_configs = [
        {
            'name': 'Standard',
            'function': direct_pathway_model_incarceration_rate,
            'param_dict': dict(p=p_values, avg_rate=avg_rate_values, d=d_values)
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
        
        # Create and save visualizations
        print(f"Creating visualizations for {config['name']} Model...")
        
        # 3D visualization of simulation results
        print("Generating 3D simulation plot...")
        fig_3d = plot_3d_simulation_results(df, width=900, height=700)
        save_figure(fig_3d, f"{config['name'].lower()}_3d_simulation", output_dir=OUTPUT_DIR_FIGURES)
        
        # Plot proportion disadvantaged to bias by ratio
        print("Generating proportion disadvantaged to bias plot...")
        fig_prop = plot_prop_disadv_to_bias_by_ratio(df, width=700, height=700)
        save_figure(fig_prop, f"{config['name'].lower()}_prop_disadv_to_bias", output_dir=OUTPUT_DIR_FIGURES)
        
        # Plot disadvantaged deviation from average
        print("Generating disadvantaged deviation plot...")
        fig_dev = plot_disadv_deviation_from_avg(df, width=700, height=700)
        save_figure(fig_dev, f"{config['name'].lower()}_disadv_deviation", output_dir=OUTPUT_DIR_FIGURES)
        
        # Plot disadvantaged deviation boxplot
        print("Generating disadvantaged deviation boxplot...")
        fig_box = plot_disadv_deviation_boxplot(df, width=900, height=700)
        save_figure(fig_box, f"{config['name'].lower()}_disadv_deviation_boxplot", output_dir=OUTPUT_DIR_FIGURES)
        
        # Create explanatory visual
        print("Generating explanatory visual...")
        fig_exp = create_explanatory_visual(df, width=700, height=700)
        save_figure(fig_exp, f"{config['name'].lower()}_explanatory_visual", output_dir=OUTPUT_DIR_FIGURES)
        
        # Create explanatory visual
        print("Generating relative explanatory visual...")
        fig_exp = create_explanatory_visual(df, relative=True, width=700, height=700)
        save_figure(fig_exp, f"{config['name'].lower()}_explanatory_visual_relative", output_dir=OUTPUT_DIR_FIGURES)
        
        