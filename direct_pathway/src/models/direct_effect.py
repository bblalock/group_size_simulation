def group_effect(group: str, theta: float, pi: float) -> float:
    """
    Calculate the group effect multiplier for incarceration rates.
    
    Parameters:
    -----------
    group : str
        Either 'disadvantaged' or 'advantaged'
    theta : float
        Disparity parameter in [0,1] that controls discrimination strength
        theta = 0: Both groups equal to population average
        theta = 1: Advantaged group at 0, disadvantaged group at 1/pi
    pi : float
        Proportion of population in disadvantaged group
        
    Returns:
    --------
    float
        Multiplier for the group's incarceration rate
    """
    is_disadvantaged = group.lower() == 'disadvantaged'
    if is_disadvantaged:
        return 1 + theta * ((1 - pi) / pi)  # When theta=1, equals 1/pi
    else:
        return 1 - theta  # When theta=1, equals 0

def incarceration_rate(avg_rate: float, group: str, theta: float, pi: float) -> float:
    """
    Calculate the incarceration rate for a given group.
    
    Parameters:
    -----------
    avg_rate : float
        Base/average incarceration rate for the population
    group : str
        Either 'disadvantaged' or 'advantaged'
    theta : float
        Disparity parameter controlling discrimination strength
    pi : float
        Proportion of population in disadvantaged group
        
    Returns:
    --------
    float
        Expected incarceration rate for the group
    """
    return avg_rate * group_effect(group, theta, pi)