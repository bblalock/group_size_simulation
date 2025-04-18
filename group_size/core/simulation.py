import numpy as np
import pandas as pd
from typing import Callable, Dict

from core.disparity_measures import calculate_disparity_measures

def run_factorial_simulation(
    rate_function: Callable,
    param_dict: Dict[str, np.ndarray]
) -> pd.DataFrame:
    """
    Run a factorial simulation for any incarceration rate model.
    
    Parameters:
    -----------
    rate_function : Callable
        Function that calculates incarceration rate. Must accept 'group' as one parameter
    param_dict : Dict[str, np.ndarray]
        Dictionary mapping parameter names to arrays of values to test
        Must include 'p' for population proportion
        
    Returns:
    --------
    pd.DataFrame
        DataFrame containing simulation results
    """
    data = []
    
    # Create all parameter combinations
    param_names = list(param_dict.keys())
    param_values = list(param_dict.values())
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