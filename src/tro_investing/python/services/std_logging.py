"""
std_logging.py

This module provides a simple logging utility for Python applications.
It uses the built-in logging module to log messages to a file.
The logging level is set to DEBUG by default, and the log messages
are formatted with a timestamp, log level, and message.

OThe StdLogging class provides methods for logging messages at
different levels: debug, info, warning, error, exception, and critical.

The function_logger decorator can be used to log the start and end
of a function, along with its arguments and return value.
"""

from logging import basicConfig, getLogger, shutdown


class StdLogging:
    #     _std_logger = None

    #----------------------------------------------------------------------------------------------------
    def __init__(self, log_level, log_name):
        basicConfig(
            level=log_level,
            filename=f"{log_name}",
            datefmt="%Y-%m-%d %H:%M:%S",
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        self._std_logger = getLogger()
        return None

    #-------------------------------------------------------------------------------------------------------
    def __del__(self):
        shutdown()

    #--------------------------------------------------------------------------------------------------------
    #  Define helper short cuts to log at the standard levels:
    def debug(self, message):
        self._std_logger.debug(message)
        return None

    def info(self, message):
        self._std_logger.info(message)
        return None

    def warning(self, message):
        self._std_logger.warning(message)
        return None

    def error(self, message):
        self._std_logger.error(message)
        return None

    def exception(self, message):
        self._std_logger.exception(message)
        return None

    def critical(self, message):
        self._std_logger.critical(message)
        return None


# ======================================================================================================================
def function_logger(func):
    def logged(*args, **kwargs):
        function_name = func.__name__.ljust(24)
        getLogger().info(f"Begin '{function_name}' arguments - {args} keyword arguments - {kwargs}")
        result = func(*args, **kwargs)
        getLogger().info(f"End   '{function_name}' returns   - {result}")
        return result

    return logged
