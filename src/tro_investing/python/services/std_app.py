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
from python.services.std_logging import StdLogging

#=============================================================================
class StdApp:
    #  -----------------------------------------------------------------------------
    def __init__(self, app_name="Hello World", version="v0.0.0") -> None:
        self._app_name = app_name
        self._version = version

        self._environment = None 
        self._logger = None 

    #---------------------------------------------------------------------------------------------------------------------

    def __str__(self) -> str:
        return self._app_name 

    def __repr__(self) -> str:
        return self._app_name 

    #---------------------------------------------------------------------------------------------------------------------
    def set_default_values(self):
        #  The default for the environment is expected to be set in the environment variable ENVIRONMENT.
        #  Numerious parameters depend on it's value so set it and validate it before setting the other parameters.
        app._environment = environ.get('ENVIRONMENT', 'undefined')
        if app._environment not in ["devl", "test", "prod"]:
            raise ValueError(f"Invalid environment - {environment}")

jasmit
    #  Set the default log level.
        self._logger = StdLogging(f"logs/{self._app_name}.log")
    switch = {
        case "devl":
            app._log_level = "DEBUG"
        case "test":
            app._log_level = "INFO"
        case "prod":
            app._log_level = "WARNING"
        case _:
            raise ValueError(f"Invalid environment - {environment}")



    app._config["log_level"] = "INFO"

        return

    # ---------------------------------------------------------------------------------------------------------------------
    def set_config_file_values(self):
        return

    # ---------------------------------------------------------------------------------------------------------------------
    def set_command_line_values(self):
        return

