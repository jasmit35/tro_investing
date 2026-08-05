"""
tro_investing config.py

Use the cofiuration file to set up the app's configuration, including database connection and logging level.
"""

from os import environ
from pathlib import Path

from fire_starter import function_logger
from pydantic_settings import BaseSettings, SettingsConfigDict
from python.services.std_dbconn import DatabaseConnection


# ----------------------------------------------------------------------------------------------------------------------
@function_logger
def configure_app(app) -> None:
    #  Determine the config file path based on the app's environment and log it.
    app._environment = environ.get("ENVIRONMENT", "prod")
    config_dir = Path.cwd() / "etc"
    config_file_path = config_dir / f"{app._environment}.env"
    app._logger.debug(f"config file path is {config_file_path}\n")

    #  If the config file does not exist or is not a file, log a warning and return.
    #  The app will use the default values in this case.
    if not config_file_path.exists():
        app._logger.warning(f"Configuration file {config_file_path} does not exist. Using defaults.\n")
        return

    if not config_file_path.is_file():
        app._logger.warning(f"Configuration file {config_file_path} is not a file. Using defaults.\n")
        return

    # Use Pydantic's BaseSettings to load the config file and update the app's config with those values.
    class All_Settings(BaseSettings):
        model_config = SettingsConfigDict(env_file=(config_file_path))

        db_name: str = "unknown"
        db_user: str = "unknown"
        db_password: str = "unknown"

        host: str = "localhost"
        port: int = 5432

        log_level: str = "info"

    #  Load the config file and update the app's config with the values from the file
    app._settings = All_Settings()
    app._logger.debug(f"settings model dump is {app._settings.model_dump()}\n")

    app._database_connection = DatabaseConnection(
        database=app._settings.db_name,
        user_id=app._settings.db_user,
        password=app._settings.db_password,
        host=app._settings.host,
        port=app._settings.port,
    )

    app._logger.level = app._settings.log_level


# ----------------------------------------------------------------------------------------------------------------------
