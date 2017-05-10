from gui import gui
from parameters import parameters

# You can change the parameters in the parameters.py file

bot_gui = gui(database_name = parameters['database_name'],
              nrows=parameters['nrows'])
