def calculate_disparity_measures(rate_disadv: float, rate_adv: float, p: float) -> dict:
    """
    Calculate various disparity measures between groups.
    
    Parameters:
    -----------
    rate_disadv : float
        Incarceration rate for disadvantaged group
    rate_adv : float
        Incarceration rate for advantaged group
        
    Returns:
    --------
    dict
        Dictionary containing disparity measures:
        - disparity_ratio
        - disparity_difference
        - odds_ratio
        - odds_disadvantaged
        - odds_advantaged
    """
    # Rate-based measures
    disparity_diff = rate_disadv - rate_adv
    disparity_ratio = rate_disadv / rate_adv if rate_adv > 0 else float('inf')

    # Calculate bias parameter
    bias_parameter = (disparity_ratio - 1)/(disparity_ratio + (1-p)/p) if rate_adv > 0 else 1.0 # This condition does make sense, if rate_adv 0, b =1 
    
    # # Odds-based measures (rates are per 100,000)
    # odds_disadv = rate_disadv / (100000 - rate_disadv) if rate_disadv < 100000 else float('inf')
    # odds_adv = rate_adv / (100000 - rate_adv) if rate_adv < 100000 else float('inf')
    # odds_ratio = odds_disadv / odds_adv if odds_adv > 0 else float('inf')
    
    return {
        'bias_parameter': bias_parameter,
        'disparity_ratio': disparity_ratio,
        'disparity_difference': disparity_diff,
        # 'odds_ratio': odds_ratio,
        # 'odds_disadvantaged': odds_disadv,
        # 'odds_advantaged': odds_adv
    }