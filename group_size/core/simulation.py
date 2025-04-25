import numpy as np
import pandas as pd
from typing import Callable, Dict
from multiprocessing import Pool, cpu_count
from functools import partial

from core.disparity_measures import calculate_disparity_measures

def process_param_combination(params, param_names, rate_function):
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
        **param_dict,
        "pop_avg": int(round(pop_avg)),
        "rate_adv": rate_adv,
        "rate_disadv": rate_disadv,
        **disparities
    }
    return result

def run_factorial_simulation(
    rate_function: Callable,
    param_dict: Dict[str, np.ndarray]
) -> pd.DataFrame:
    """
    Run a factorial simulation for any incarceration rate model in parallel.
    """
    # Create all parameter combinations
    param_names = list(param_dict.keys())
    param_values = list(param_dict.values())
    param_combinations = np.meshgrid(*param_values, indexing='ij')
    param_combinations = [x.flatten() for x in param_combinations]
    
    # Create a list of parameter combinations
    all_params = list(zip(*param_combinations))
    
    # Create a partial function with fixed parameters
    process_func = partial(process_param_combination, param_names=param_names, rate_function=rate_function)
    
    # Run in parallel using all available cores
    with Pool(processes=cpu_count()) as pool:
        results = pool.map(process_func, all_params)
    
    return pd.DataFrame(results)