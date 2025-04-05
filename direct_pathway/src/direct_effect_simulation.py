import numpy as np
import pandas as pd

from models.direct_effect import incarceration_rate
from analysis.disparity_measures import calculate_disparity_measures
from visualization.plots import plot_explanatory_simulation
from utils.io import save_figure, save_simulation_data

def create_explanatory_simulation_data(thetas, pi_values, avg_rate=200):
    """
    Create simulation data for the explanatory simulation with fixed average rate.
    
    Parameters:
    -----------
    thetas : list or array
        Disparity parameter values
    pi_values : list or array
        Group proportion values
    avg_rate : float, default=200
        Fixed average incarceration rate per 100,000
        
    Returns:
    --------
    pd.DataFrame
        DataFrame containing simulation results
    """
    # Store simulation results
    data = []
    
    # Run simulation
    for pi in pi_values:
        for theta in thetas:
            # Calculate group rates
            rate_disadv = incarceration_rate(avg_rate, 'disadvantaged', theta, pi)
            rate_adv = incarceration_rate(avg_rate, 'advantaged', theta, pi)
            
            # Calculate population average
            pop_avg = pi * rate_disadv + (1 - pi) * rate_adv
            
            # Calculate disparity measures
            disparities = calculate_disparity_measures(rate_disadv, rate_adv)
            
            # Store results
            for group, rate in [('Disadvantaged', rate_disadv), 
                              ('Advantaged', rate_adv),
                              ('Population Average', pop_avg)]:
                data.append({
                    "theta": theta,
                    "Group": group,
                    "Rate": rate,
                    "pi": pi,
                    "avg_rate": avg_rate,
                    **disparities
                })
    
    # Convert results to DataFrame
    return pd.DataFrame(data)

def create_total_simulation_data(thetas, pi_values, avg_rates):
    """
    Create simulation data varying disparity parameter, group proportion, and average rate.
    
    Parameters:
    -----------
    thetas : list or array
        Disparity parameter values
    pi_values : list or array
        Group proportion values
    avg_rates : list or array
        Average incarceration rate values per 100,000
        
    Returns:
    --------
    pd.DataFrame
        DataFrame containing simulation results
    """
    # Store simulation results
    data = []
    
    # Run simulation
    for avg_rate in avg_rates:
        for pi in pi_values:
            for theta in thetas:
                # Calculate group rates
                rate_disadv = incarceration_rate(avg_rate, 'disadvantaged', theta, pi)
                rate_adv = incarceration_rate(avg_rate, 'advantaged', theta, pi)
                
                # Calculate population average
                pop_avg = pi * rate_disadv + (1 - pi) * rate_adv
                
                # Calculate disparity measures
                disparities = calculate_disparity_measures(rate_disadv, rate_adv)
                
                # Store results
                for group, rate in [('Disadvantaged', rate_disadv), 
                                  ('Advantaged', rate_adv),
                                  ('Population Average', pop_avg)]:
                    data.append({
                        "theta": theta,
                        "Group": group,
                        "Rate": rate,
                        "pi": pi,
                        "avg_rate": avg_rate,
                        **disparities
                    })
    
    # Convert results to DataFrame
    return pd.DataFrame(data)

if __name__ == "__main__":
    """
    Run simulations exploring how group size and disparity parameters affect
    measured inequality in incarceration rates.
    """
    # Simulation parameters
    thetas = np.linspace(0, 1, 5)  # Disparity parameter values
    pi_values = np.linspace(.1, .9, 3)  # Group proportion values
    avg_rate = 200  # Average incarceration rate per 100,000 for explanatory simulation
    avg_rates = [100, 200, 500, 1000]  # Average rates for total simulation
    
    # Run explanatory simulation (fixed average rate)
    print("Running explanatory simulation...")
    explanatory_df = create_explanatory_simulation_data(thetas, pi_values, avg_rate)
    
    # Save explanatory simulation data
    save_simulation_data(explanatory_df, "explanatory_simulation_data.csv")
    
    # Create and save explanatory simulation plot
    explanatory_fig = plot_explanatory_simulation(explanatory_df, pi_values, thetas)
    save_figure(explanatory_fig, "explanatory_direct_effect_simulation")
    
    # Run total simulation (varying average rate)
    print("Running total simulation...")
    total_df = create_total_simulation_data(thetas, pi_values, avg_rates)
    
    # Save total simulation data
    save_simulation_data(total_df, "total_simulation_data.csv")
    
    # Note: Total simulation plotting will be implemented later
    # plot_total_simulation(total_df, pi_values, thetas, avg_rates)