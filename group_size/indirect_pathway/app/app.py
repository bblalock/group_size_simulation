import dash
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np

from layouts import create_layout
from callbacks import register_callbacks
from constants import PORT, APP_DATA_PATH
import os

from direct_pathway.src.visualization.plots import calculate_deviation_metrics

port = int(os.environ.get("PORT", PORT))

# Load simulation results from the same path that would be used by save_simulation_data
simulation_results = pd.read_csv(os.path.join(APP_DATA_PATH,'normalized_indirect_simulation.csv'))
simulation_results = calculate_deviation_metrics(simulation_results)
simulation_results['z_position_gap'] = np.round(simulation_results['z_position_gap'],1)

# Initialize the Dash app with bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUMEN])
server = app.server  # Expose Flask server for Heroku deployment

# Set app layout
app.layout = create_layout(simulation_results=simulation_results)

# Register callbacks
register_callbacks(app, simulation_results=simulation_results)

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=port, host='0.0.0.0')