"""
std_app.py
---------------------------------------------------------------------------------------------------------------------
  The following methods are expected to be overridden by the app that inherits from StdApp. They are called by the
  app in the following order:
  
  1. set_default_values() - This method is expected to set the default values for the app's configuration.
     It is called before the config file is read and the command line parameters are processed.
     This allows the app to have default values that can be overridden by the config file and / or
     the command line parameters.

  2. set_config_file_values() - This method is expected to read the config file and set the values in the 
     app's configuration. It is called after the default values are set and before the command line parameters 
     are processed. This allows the app to have values that are set in the config file that can be overridden by 
     the command line parameters.

  3. set_command_line_values() - This method is expected to process the command line parameters and set the values 
     in the app's configuration. It is called after the default values are set and after the config file values 
     are set. This allows the app to have values that are set by the command line parameters that override the 
     default values and the config file values.
---------------------------------------------------------------------------------------------------------------------
"""
from datetime import datetime
from os import environ

from python.services.std_logging import StdLogging


#=============================================================================
class StdApp:
    #  The following are expected attributes of the app that inherits from StdApp.
    #  They are set in the __init__ method.
    _app_name = None 
    _environment = None
    _logger = None
    _max_return_code = None
    _version = None

    #-----------------------------------------------------------------------------
    def __init__(self, app_name="Hello World", version="v0.0.0") -> None:
        #  The default for the environment is expected to be set in the environment variable ENVIRONMENT.
        #  Numerious parameters depend on it's value so set it and validate it before setting the other parameters.
        self._environment = environ.get('ENVIRONMENT', 'undefined')
        if self._environment not in ["devl", "test", "prod"]:
            raise ValueError(f"Invalid environment - {self._environment}")

        self._app_name = app_name
        
        #  Set up the default logging for the app based on the environment.
        this_day = datetime.today().strftime("%y_%m_%d")
        match (self._environment): 
            case "devl":        
                self._logger = StdLogging("DEBUG", f"logs/{self._app_name}_{this_day}.log")
            case "test":
                self._logger = StdLogging("INFO", f"logs/{self._app_name}_{this_day}.log")
            case "prod":
                self._logger = StdLogging("WARNING", f"logs/{self._app_name}_{this_day}.log")
            case _:
                raise ValueError(f"Invalid environment - {self._environment}")

        self._max_return_code = 0
        
        self._version = version

    #-----------------------------------------------------------------------------
    # Dunder methods.

    def __str__(self) -> str:
        return f"{self._app_name} - {self._version} - {self._environment}" 

    def __repr__(self) -> str:
        return f"{self._app_name} - {self._version} - {self._environment}" 

    #---------------------------------------------------------------------------------------------------------------------
    #  The following methods are expected to be overridden by the app that inherits from StdApp.

    def set_default_values(self):
        pass

    def set_config_file_values(self):
        pass 

    def set_command_line_values(self):
        pass

    #---------------------------------------------------------------------------------------------------------------------
