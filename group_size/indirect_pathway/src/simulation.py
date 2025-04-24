import numpy as np
import pandas as pd
from model.indirect_effect import (
    indirect_model_incarceration_rate
)
# from visualization.plots import (
    
# )

from core.simulation import run_factorial_simulation
from core.utils.io import save_figure, save_simulation_data
from indirect_pathway.app.constants import APP_DATA_PATH
import os

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
    
    ## Parameters affecting z (economic) position b/w groups
    p_values = np.linspace(0.001,.99,20)   # Group proportion values
    
    ### Distribution parameters for beta distributions
    #### Mean positions - disadvantaged group always lower than advantaged
    mu_disadv_values = [0.2] #np.linspace(.1,.5,5)
    z_position_gap_values = np.arange(0, .9, .2)
    
    #### Concentration parameters controlling distribution spread
    c_disadv_values = [20] #np.arange(1,50,5)  # Concentration parameter for disadvantaged group
    c_adv_values = [20] #np.arange(1,50,5)  # Concentration parameter for advantaged group
    
    ## Parameters affecting incarceration risk given z  
    gamma_values = np.linspace(0.1,5,20) 
    target_avg_rate_values = [500] # np.linspace(100,500,5)
    # max_rate_values = [500] #np.array([100,200,300, 400, 500])  # Maximum rate value per 100,000
    floor_rate_values = np.linspace(0,500, 20)
    
    # Sample size for simulation
    sample_size_values = np.array([10000])
    
    n_results = (len(p_values) * len(gamma_values) * len(floor_rate_values) * 
                len(mu_disadv_values) * len(z_position_gap_values) * 
                len(c_disadv_values) * len(c_adv_values) * 
                len(sample_size_values)
                )
    
    print(f'{n_results} simulations')
    
    # Define model configurations
    model_configs = [
        # {
        #     'name': 'indirect',
        #     'function': indirect_model_incarceration_rate,
        #     'param_dict': {
        #         'p': p_values,
        #         'gamma': gamma_values,
        #         'max_rate': max_rate_values,
        #         'mu_disadv': mu_disadv_values,
        #         'z_position_gap': z_position_gap_values,
        #         'c_disadv': c_disadv_values,
        #         'c_adv': c_adv_values,
        #         'sample_size': sample_size_values
        #     }
        # },
        {
            'name': 'normalized_indirect',
            'function': indirect_model_incarceration_rate,
            'param_dict': {
                'p': p_values,
                'gamma': gamma_values,
                # 'max_rate': max_rate_values,
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
