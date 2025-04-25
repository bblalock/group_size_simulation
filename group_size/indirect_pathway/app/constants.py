import os
# Constants shared across modules
PLOT_HEIGHT = 700
PLOT_CARD_WIDTH = 9
PORT = 8052

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_DATA_PATH = os.path.join(os.path.dirname(APP_ROOT), "output", "data")
