import numpy as np
from scipy.stats import beta

def beta_params_from_mean_concentration(mean, concentration):
    """
    Calculate alpha and beta parameters for a beta distribution
    based on the mean and concentration parameter.
    
    Parameters:
    -----------
    mean : float
        Desired mean in (0,1)
    concentration : float
        Concentration parameter (α + β)
        Controls how concentrated the distribution is around its mean
        
    Returns:
    --------
    tuple
        (alpha, beta) parameters for scipy.stats.beta
    """
    # Calculate alpha and beta
    alpha = mean * concentration
    beta = (1 - mean) * concentration
    
    return alpha, beta

def generate_stratification_positions(p, mu_disadv, z_position_gap, c_disadv, c_adv, sample_size):
    """
    Generate positions in the stratification dimension Z for both groups
    using beta distributions.
    
    Parameters:
    -----------
    p : float
        Proportion of disadvantaged group in population
    mu_disadv : float
        Mean position for disadvantaged group in (0,1)
    z_position_gap : float
        Absolute difference to add to disadvantaged group mean to get advantaged group mean
    c_disadv : float
        Concentration parameter for disadvantaged group
    c_adv : float
        Concentration parameter for advantaged group
    sample_size : int
        Total number of individuals to simulate
        
    Returns:
    --------
    dict
        Dictionary with positions for both groups and group assignments
    """
    # Calculate mu_adv based on mu_disadv and z_position_gap
    mu_adv = mu_disadv + z_position_gap
    
    # Ensure mu_adv is within valid range (0,1)
    mu_adv = min(max(mu_adv, 0.001), 0.999)
    
    # Calculate number of individuals in each group
    n_disadv = int(p * sample_size)
    n_adv = sample_size - n_disadv
    
    # Calculate beta distribution parameters
    alpha_disadv, beta_disadv = beta_params_from_mean_concentration(mu_disadv, c_disadv)
    alpha_adv, beta_adv = beta_params_from_mean_concentration(mu_adv, c_adv)
    
    # Generate positions from beta distributions
    positions_disadv = beta.rvs(alpha_disadv, beta_disadv, size=n_disadv)
    positions_adv = beta.rvs(alpha_adv, beta_adv, size=n_adv)
    
    # Create group assignments (1 for disadvantaged, 0 for advantaged)
    groups = np.concatenate([np.ones(n_disadv), np.zeros(n_adv)])
    
    # Combine positions
    all_positions = np.concatenate([positions_disadv, positions_adv])
    
    return {
        'positions': all_positions,
        'groups': groups,
        'positions_disadv': positions_disadv,
        'positions_adv': positions_adv,
        'mu_adv': mu_adv,
        'alpha_disadv': alpha_disadv,
        'beta_disadv': beta_disadv,
        'alpha_adv': alpha_adv,
        'beta_adv': beta_adv
    }

def calculate_incarceration_rates_non_normalized(positions, gamma, max_rate):
    """
    Calculate incarceration rates based on positions in the stratification dimension
    using the non-normalized approach.
    
    Parameters:
    -----------
    positions : dict
        Dictionary with positions and group assignments from generate_stratification_positions
    gamma : float
        Shape parameter controlling relationship between position and incarceration rate
    max_rate : float
        Maximum incarceration rate (per 100,000)
        
    Returns:
    --------
    dict
        Dictionary with incarceration rates for both groups
    """
    
    # Extract positions for each group
    positions_disadv = positions['positions_disadv']
    positions_adv = positions['positions_adv']
    
    # Calculate position effect: (1-z)^gamma
    effect_disadv = np.power(1 - positions_disadv, gamma)
    effect_adv = np.power(1 - positions_adv, gamma)
    
    # Calculate individual incarceration rates
    rates_disadv = max_rate * effect_disadv
    rates_adv = max_rate * effect_adv
    
    # Calculate group-level rates (average)
    rate_disadv = np.mean(rates_disadv)
    rate_adv = np.mean(rates_adv)
    
    return {
        'rate_disadv': rate_disadv,
        'rate_adv': rate_adv
    }

import numpy as np

def normalize_rates_to_target(rates, target_avg_rate):
    """
    Normalize a set of rates to achieve a target population average.
    
    Parameters:
    -----------
    rates : numpy.ndarray
        Array of rates to normalize
    target_avg_rate : float
        Target average rate to achieve
        
    Returns:
    --------
    tuple
        (normalized_rates, normalization_factor)
    """
    current_avg = np.mean(rates)
    norm_factor = target_avg_rate / current_avg
    normalized_rates = rates * norm_factor
    
    return normalized_rates, norm_factor

def apply_floor_constraint(rates, floor_rate=0, shift_mode=True):
    """
    Apply a floor constraint to rates, either as a hard floor or by shifting the function.
    
    Parameters:
    -----------
    rates : numpy.ndarray
        Array of rates to apply floor to
    floor_rate : float, optional
        Minimum rate value (default=0)
    shift_mode : bool, optional
        If True, shift the entire curve up by adding the difference needed to reach floor_rate
        If False, apply a hard floor: max(floor_rate, rates)
        
    Returns:
    --------
    numpy.ndarray
        Array of rates with floor constraint applied
    """
    if floor_rate <= 0:
        return rates
    
    if shift_mode:
        # Shift everything up by the floor rate
        rates_with_floor = rates + floor_rate
    else:
        # Apply a hard floor: max(floor_rate, rates)
        rates_with_floor = np.maximum(floor_rate, rates)
    
    return rates_with_floor

def calculate_incarceration_rates_normalized(positions, gamma, target_avg_rate, floor_rate=0, return_only_factors=False):
    """
    Calculate incarceration rates based on positions in the stratification dimension
    using the normalized approach to maintain a constant population-average rate.
    """
    # Extract positions for each group
    positions_disadv = positions['positions_disadv']
    positions_adv = positions['positions_adv']
    all_positions = positions['positions'] if 'positions' in positions else np.concatenate([positions_disadv, positions_adv])
    
    # Calculate base position effect: (1-z)^gamma for all positions
    all_base_effects = np.power(1 - all_positions, gamma)
    
    # First normalization: adjust for expected effect
    expected_effect = np.mean(all_base_effects)
    first_norm_factor = 1 / expected_effect
    
    # Calculate initial normalized rates (without floor)
    initial_rates_all = target_avg_rate * all_base_effects * first_norm_factor
    
    # Apply floor if specified
    if floor_rate > 0:
        # Apply floor to all rates using apply_floor_constraint
        rates_with_floor_all = apply_floor_constraint(initial_rates_all, floor_rate)
        
        # Second normalization: adjust to maintain target average after applying floor
        _, second_norm_factor = normalize_rates_to_target(rates_with_floor_all, target_avg_rate)
    else:
        # No floor needed
        second_norm_factor = 1
    
    # If we only need factors, return them now
    if return_only_factors:
        return {
            'first_norm_factor': first_norm_factor,
            'second_norm_factor': second_norm_factor,
            'total_norm_factor': first_norm_factor * second_norm_factor
        }
    
    # Calculate base position effect for each group
    disadv_base_effects = np.power(1 - positions_disadv, gamma)
    adv_base_effects = np.power(1 - positions_adv, gamma)
    
    # Apply normalization factors to calculate rates
    initial_rates_disadv = target_avg_rate * disadv_base_effects * first_norm_factor
    initial_rates_adv = target_avg_rate * adv_base_effects * first_norm_factor
    
    # Apply floor if needed
    if floor_rate > 0:
        # Apply floor using apply_floor_constraint (using the same approach as used for calculating factors)
        rates_with_floor_disadv = apply_floor_constraint(initial_rates_disadv, floor_rate)
        rates_with_floor_adv = apply_floor_constraint(initial_rates_adv, floor_rate)
        
        # Apply second normalization
        rates_disadv = rates_with_floor_disadv * second_norm_factor
        rates_adv = rates_with_floor_adv * second_norm_factor
    else:
        rates_disadv = initial_rates_disadv
        rates_adv = initial_rates_adv
    
    # Calculate group-level rates (average)
    rate_disadv = np.mean(rates_disadv)
    rate_adv = np.mean(rates_adv)
    
    # Create return data structure with all the relevant information
    groups = np.concatenate([np.ones(len(positions_disadv)), np.zeros(len(positions_adv))])
    
    return {
        'all_positions': all_positions,
        'all_rates': np.concatenate([rates_disadv, rates_adv]),
        'groups': groups,
        'rate_disadv': rate_disadv,
        'rate_adv': rate_adv,
        'positions_disadv': positions_disadv,
        'positions_adv': positions_adv,
        'rates_disadv': rates_disadv,
        'rates_adv': rates_adv,
        'pop_avg_rate': np.mean(np.concatenate([rates_disadv, rates_adv])),
        'first_norm_factor': first_norm_factor,
        'second_norm_factor': second_norm_factor,
        'total_norm_factor': first_norm_factor * second_norm_factor,
        'floor_rate': floor_rate,
        'effective_floor': floor_rate * second_norm_factor
    }
    
def indirect_model_incarceration_rate(
    group, 
    p, 
    gamma, 
    max_rate=None,
    min_rate=None, 
    mu_disadv=0.3, 
    z_position_gap=0.4, 
    c_disadv=5, 
    c_adv=5, 
    sample_size=10000,
    normalized=False,
    target_avg_rate=None
    ):
    """
    Calculate incarceration rates for the indirect pathway model.
    
    Parameters:
    -----------
    group : str
        'advantaged', 'disadvantaged', or 'population'
    p : float
        Proportion of disadvantaged group in population
    gamma : float
        Shape parameter controlling relationship between position and incarceration rate
    max_rate : float
        Maximum incarceration rate (per 100,000) for non-normalized approach
    mu_disadv : float
        Mean position for disadvantaged group in (0,1)
    z_position_gap : float
        Absolute difference between advantaged and disadvantaged group means
    c_disadv : float
        Concentration parameter for disadvantaged group
    c_adv : float
        Concentration parameter for advantaged group
    sample_size : int
        Number of individuals to simulate
    normalized : bool
        Whether to use the normalized approach (True) or non-normalized approach (False)
    target_avg_rate : float
        Target population-average incarceration rate for normalized approach
        
    Returns:
    --------
    float
        Incarceration rate for the specified group
    """
    # Generate positions for both groups
    positions = generate_stratification_positions(
        p=p, 
        mu_disadv=mu_disadv, 
        z_position_gap=z_position_gap,
        c_disadv=c_disadv,
        c_adv=c_adv,
        sample_size=sample_size
    )
    
    # Calculate incarceration rates using appropriate method
    if normalized:
        if target_avg_rate is None:
            raise ValueError("target_avg_rate must be provided when normalized=True")
        
        rates = calculate_incarceration_rates_normalized(
            positions=positions,
            gamma=gamma,
            target_avg_rate=target_avg_rate,
            floor_rate=min_rate
        )
    else:
        rates = calculate_incarceration_rates_non_normalized(
            positions=positions,
            gamma=gamma,
            max_rate=max_rate
        )
    
    # Return rate for the requested group
    if group == 'disadvantaged':
        return rates['rate_disadv']
    else:
        return rates['rate_adv']