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

def calculate_incarceration_rates_normalized(positions, gamma, target_avg_rate):
    """
    Calculate incarceration rates based on positions in the stratification dimension
    using the normalized approach to maintain a constant population-average rate.
    
    Parameters:
    -----------
    positions : dict
        Dictionary with positions and group assignments from generate_stratification_positions
    gamma : float
        Shape parameter controlling relationship between position and incarceration rate
    target_avg_rate : float
        Target population-average incarceration rate (per 100,000)
        
    Returns:
    --------
    dict
        Dictionary with incarceration rates for both groups
    """
    
    # Extract positions for each group
    positions_disadv = positions['positions_disadv']
    positions_adv = positions['positions_adv']
    all_positions = positions['positions']
    groups = np.concatenate([np.ones(len(positions_disadv)), np.zeros(len(positions_adv))])
    
    # Calculate base position effect: (1-z)^gamma for all positions
    all_effects = np.power(1 - all_positions, gamma)
    
    # Calculate expected value: average of (1-z)^gamma across the population
    expected_effect = np.mean(all_effects)
    
    # Calculate normalization factor
    norm_factor = 1 / expected_effect
    
    # Calculate normalized position effects
    norm_effect_disadv = np.power(1 - positions_disadv, gamma) * norm_factor
    norm_effect_adv = np.power(1 - positions_adv, gamma) * norm_factor
    
    # Calculate individual incarceration rates
    rates_disadv = target_avg_rate * norm_effect_disadv
    rates_adv = target_avg_rate * norm_effect_adv
    
    # Calculate group-level rates (average)
    rate_disadv = np.mean(rates_disadv)
    rate_adv = np.mean(rates_adv)
    
    # Verify population average matches target
    all_norm_effects = np.power(1 - all_positions, gamma) * norm_factor
    all_rates = target_avg_rate * all_norm_effects
    pop_avg_rate = np.mean(all_rates)
    
    return {
        'all_positions': all_positions,
        'all_rates': all_rates,
        'groups': groups,
        'rate_disadv': rate_disadv,
        'rate_adv': rate_adv,
        'positions_disadv': positions_disadv,
        'positions_adv': positions_adv,
        'rates_disadv': rates_disadv,
        'rates_adv': rates_adv,
        'pop_avg_rate': pop_avg_rate,
        'expected_effect': expected_effect,
        'norm_factor': norm_factor
    }

def indirect_model_incarceration_rate(
    group, 
    p, 
    gamma, 
    max_rate=None, 
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
            target_avg_rate=target_avg_rate
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