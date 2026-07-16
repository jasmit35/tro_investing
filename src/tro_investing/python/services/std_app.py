"""
std_app.py
---------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------
"""
from datetime import datetime
from os import environ

from python.services.std_logging import StdLogging


#=============================================================================
class StdApp:
    _app_name: str = None
    _environment: str = None
    _logger: StdLogging = None
    _max_return_code: int = 0
    _settings: dict = None
    _version: str = None


    #-----------------------------------------------------------------------------
    # Dunder methods.
    #-----------------------------------------------------------------------------

    def __init__(self, app_name="Hello World", version="v0.0.0") -> None:
        self._app_name = app_name
        self._version = version
        
        #  The default for the environment is expected to be set in the environment variable ENVIRONMENT.
        #  Numerious parameters depend on it's value so set it and validate it before setting the other parameters.
        self._environment = environ.get('ENVIRONMENT', 'undefined')
        if self._environment not in ["devl", "test", "prod"]:
            raise ValueError(f"Invalid environment - {self._environment}")
        
        #  Set up the default logging for the app based on the environment.
        this_day = datetime.today().strftime("%y_%m_%d")
        log_file = f"logs/{self._app_name}_{this_day}.log"
        match (self._environment): 
            case "devl":        
                self._logger = StdLogging("DEBUG", log_file) 
            case "test":
                self._logger = StdLogging("INFO", log_file) 
            case "prod":
                self._logger = StdLogging("WARNING", log_file)
            case _:
                raise ValueError(f"Invalid environment - {self._environment}")

    def __str__(self) -> str:
        return f"{self._app_name} - {self._version} - {self._environment}" 

    def __repr__(self) -> str:
        return f"{self._app_name} - {self._version} - {self._environment}" 
