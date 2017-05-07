from src.gui import gui
from src.parameters import parameters

bot_gui = gui(database_name = parameters['database_name'],
              nrows=parameters['nrows'])
