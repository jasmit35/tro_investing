"""
std_app.py
"""
from python.services.std_logging import function_logger, StdLogging

#=============================================================================
class StdApp:
    #  -----------------------------------------------------------------------------
    def __init__(self, app_name="Hello World", version="v.0.0.0.0") -> None:
        self._app_name = app_name
        self._version = version

        self._logger = StdLogging(f"logs/{self._app_name}.log")

    # ---------------------------------------------------------------------------------------------------------------------
    def __str__(self):
        return "StdApp"

    __repr__ = __str__

    # ---------------------------------------------------------------------------------------------------------------------
    def set_default_values(self):
        return

    # ---------------------------------------------------------------------------------------------------------------------
    def set_config_file_values(self):
        return

    # ---------------------------------------------------------------------------------------------------------------------
    def set_command_line_values(self):
        return

