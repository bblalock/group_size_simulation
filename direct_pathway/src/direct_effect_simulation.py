import numpy as np
import pandas as pd
from typing import Callable, Dict, List, Any

from models.direct_effect import (
    standard_model_incarceration_rate,
)
from visualization.plots import (
    create_explanatory_visual,
    plot_3d_simulation_results,
    plot_prop_disadv_to_bias_by_ratio,
    plot_disadv_deviation_from_avg,
    plot_disadv_deviation_boxplot
)
from analysis.disparity_measures import calculate_disparity_measures
from utils.io import save_figure, save_simulation_data

def run_factorial_simulation(
    rate_function: Callable,
    param_grid: Dict[str, np.ndarray],
    model_name: str
) -> pd.DataFrame:
    """
    Run a factorial simulation for any incarceration rate model.
    
    Parameters:
    -----------
    rate_function : Callable
        Function that calculates incarceration rate. Must accept 'group' as one parameter
    param_grid : Dict[str, np.ndarray]
        Dictionary mapping parameter names to arrays of values to test
        Must include 'p' for population proportion
    model_name : str
        Name of the model being simulated
        
    Returns:
    --------
    pd.DataFrame
        DataFrame containing simulation results
    """
    data = []
    
    # Create all parameter combinations
    param_names = list(param_grid.keys())
    param_values = list(param_grid.values())
    param_combinations = np.meshgrid(*param_values, indexing='ij')
    param_combinations = [x.flatten() for x in param_combinations]
    
    # Run simulation for each parameter combination
    for params in zip(*param_combinations):
        # Create parameter dictionary for this combination
        param_dict = dict(zip(param_names, params))
        p = param_dict['p']  # Extract population proportion
        
        # Calculate rates for both groups
        rate_disadv = rate_function(group='disadvantaged', **param_dict)
        rate_adv = rate_function(group='advantaged', **param_dict)
        
        # Calculate population average
        pop_avg = p * rate_disadv + (1 - p) * rate_adv
        
        # Calculate disparity measures
        disparities = calculate_disparity_measures(rate_disadv=rate_disadv, rate_adv=rate_adv, p=p)
        
        # Store results for each group
        result = {
            'prop_disadv': p,
            "pop_avg": int(round(pop_avg)),
            "rate_adv": rate_adv,
            "rate_disadv": rate_disadv,
            # **param_dict, # all the parameters except for p can be calculated (and are for are simulation types)
            **disparities
        }
        data.append(result)
    
    return pd.DataFrame(data)

def create_model_param_grid(model: str, 
                          p_values: np.ndarray,
                          rate_values: np.ndarray,
                          d_values: np.ndarray = None,
                          b_values: np.ndarray = None) -> Dict[str, np.ndarray]:
    """
    Create parameter grid for specific model type.
    
    Parameters:
    -----------
    model : str
        Model type ('standard', 'bias', or 'non_redistributive')
    p_values : np.ndarray
        Array of population proportion values
    rate_values : np.ndarray
        Array of rate values (avg_rate or base_rate)
    d_values : np.ndarray, optional
        Array of disparity ratio values
    b_values : np.ndarray, optional
        Array of bias parameter values
    
    Returns:
    --------
    Dict[str, np.ndarray]
        Parameter grid dictionary
    """
    if model == 'standard':
        return {
            'p': p_values,
            'avg_rate': rate_values,
            'd': d_values
        }
    elif model == 'bias':
        return {
            'p': p_values,
            'avg_rate': rate_values,
            'b': b_values
        }
    elif model == 'non_redistributive':
        return {
            'p': p_values,
            'base_rate': rate_values,
            'd': d_values
        }
    else:
        raise ValueError(f"Unknown model type: {model}")

if __name__ == "__main__":
    """
    Run factorial simulations for all three models exploring how group size 
    and various disparity parameters affect measured inequality in incarceration rates.
    """
    # Define parameter ranges
    p_values = np.round(np.arange(0.1, 1, 0.01), 2)  # Group proportion values from 0.1 to 1.0 with 100 values
    d_values = np.linspace(1, 10, 30)   # Disparity ratio values with 100 values
    avg_rate_values = np.linspace(50, 500, 100)  # Rate values per 100,000 with 100 values

    n_results = len(p_values)*len(d_values)*len(avg_rate_values)
    print(f'{n_results} simulations')
    
    # Define model configurations
    model_configs = [
        {
            'name': 'Standard',
            'function': standard_model_incarceration_rate,
            'param_grid': create_model_param_grid(model='standard', p_values=p_values, rate_values=avg_rate_values, d_values=d_values)
        },
    ]
    
    # Run simulations for all models
    results = []
    for config in model_configs:
        print(f"Running {config['name']} Model simulation...")
        df = run_factorial_simulation(
            config['function'],
            config['param_grid'],
            config['name']
        )
        results.append(df)
        
        # Save individual model results
        save_simulation_data(df, f"{config['name'].lower()}_simulation.csv")
        
        # Create and save visualizations
        print(f"Creating visualizations for {config['name']} Model...")
        
        # 3D visualization of simulation results
        print("Generating 3D simulation plot...")
        fig_3d = plot_3d_simulation_results(df, width=900, height=700)
        save_figure(fig_3d, f"{config['name'].lower()}_3d_simulation")
        
        # Plot proportion disadvantaged to bias by ratio
        print("Generating proportion disadvantaged to bias plot...")
        fig_prop = plot_prop_disadv_to_bias_by_ratio(df, width=700, height=700)
        save_figure(fig_prop, f"{config['name'].lower()}_prop_disadv_to_bias")
        
        # Plot disadvantaged deviation from average
        print("Generating disadvantaged deviation plot...")
        fig_dev = plot_disadv_deviation_from_avg(df, width=700, height=700)
        save_figure(fig_dev, f"{config['name'].lower()}_disadv_deviation")
        
        # Plot disadvantaged deviation boxplot
        print("Generating disadvantaged deviation boxplot...")
        fig_box = plot_disadv_deviation_boxplot(df, width=900, height=700)
        save_figure(fig_box, f"{config['name'].lower()}_disadv_deviation_boxplot")
        
        # Create explanatory visual
        print("Generating explanatory visual...")
        fig_exp = create_explanatory_visual(df, width=700, height=700)
        save_figure(fig_exp, f"{config['name'].lower()}_explanatory_visual")
        
        # Create explanatory visual
        print("Generating relative explanatory visual...")
        fig_exp = create_explanatory_visual(df, relative=True, width=700, height=700)
        save_figure(fig_exp, f"{config['name'].lower()}_explanatory_visual_relative")
        
        