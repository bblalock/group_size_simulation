def standard_model_incarceration_rate(avg_rate: float, group: str, d: float, p: float, **kwargs) -> float:
    """
    Calculate incarceration rates using the Standard Model.
    Maintains constant population-wide incarceration rate with disparity ratio d.
    
    Parameters:
    -----------
    avg_rate : float
        Population average incarceration rate
    group : str
        Either 'disadvantaged' or 'advantaged'
    d : float
        Disparity ratio between groups (d >= 1)
    p : float
        Proportion of population in disadvantaged group
        
    Returns:
    --------
    float
        Expected incarceration rate for the group
    """
    advantaged_rate = avg_rate / (d * p + (1 - p))
    is_disadvantaged = group.lower() == 'disadvantaged'
    if is_disadvantaged:
        return d * advantaged_rate
    else:
        return advantaged_rate

def bias_controlled_redistribution_rate(avg_rate: float, group: str, b: float, p: float, **kwargs) -> float:
    """
    Calculate incarceration rates using the Bias-Controlled Redistribution Model.
    Uses bias parameter b to redistribute punishment while maintaining constant total.
    
    Parameters:
    -----------
    avg_rate : float
        Population average incarceration rate
    group : str
        Either 'disadvantaged' or 'advantaged'
    b : float
        Bias parameter in [0,1] controlling punishment redistribution
    p : float
        Proportion of population in disadvantaged group
        
    Returns:
    --------
    float
        Expected incarceration rate for the group
    """
    is_disadvantaged = group.lower() == 'disadvantaged'
    if is_disadvantaged:
        return avg_rate * (1 + b * ((1 - p) / p))
    else:
        return avg_rate * (1 - b)


def non_redistributive_disparity_rate(base_rate: float, group: str, d: float, **kwargs) -> float:
    """
    Calculate incarceration rates using the Non-Redistributive Disparity Model.
    Adds punishment rather than redistributing it.
    
    Parameters:
    -----------
    base_rate : float
        Baseline incarceration rate for advantaged group
    group : str
        Either 'disadvantaged' or 'advantaged'
    d : float
        Disparity ratio between groups (d >= 1)
        
    Returns:
    --------
    float
        Expected incarceration rate for the group
    """
    is_disadvantaged = group.lower() == 'disadvantaged'
    if is_disadvantaged:
        return d * base_rate
    else:
        return base_rate