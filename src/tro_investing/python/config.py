from argparse import ArgumentParser
from os import environ
from pathlib import Path

from ruamel import yaml as pyyaml

from python.services.std_logging import function_logger

#  from python.services.std_report import StdReport


#-----------------------------------------------------------------------------
@function_logger
def set_default_values(app):

    environment = environ.get('ENVIRONMENT', 'undefined')
    if environment not in ["devl", "test", "prod"]:
        raise ValueError(f"Invalid environment - {environment}")
    app._config["environment"] = environment

    #  The default for the report file is expected to be in a 'reports' directory under the current working directory.
    report_file = Path.cwd() / "reports"
    report_path = Path(report_file)
    app._config["report_path"] = report_path

    #  The default for the stage directory is expected to be a directory under the current working directory.
    stage_dir = Path.cwd() / "stage"
    stage_dir_path = Path(stage_dir)
    app._config["stage_dir_path"] = stage_dir_path

    # Log the config for debugging purposes
    app._logger.debug(f"config is {app._config}\n")
    return

#-----------------------------------------------------------------------------
@function_logger
def set_config_file_values(app):
    #  The config file is expected to be in the etc directory under the
    #  current working directory and should be named <app_name>.cfg
    config_directory = Path.cwd() / "etc"
    config_file = config_directory / f"{app._config.get('app_name')}.cfg"
    app._logger.debug(f"config file is {config_file}\n")

    #  If the config file does not exist or is not a file, log a warning and return.
    #  The app will use the default values in this case.
    if not config_file.exists():
        app.report(f"Configuration file {config_file} does not exist. Using defaults.\n")
        return None

    if not config_file.is_file():
        app.report(f"Configuration file {config_file} is not a file, Using defaults.\n")
        return None

    #  Load the config file and update the app's config with the values from the file
    #  The config file is expected to be a yaml file with a top level key for each environment (devl, test, prod)
    #  The values for each environment are expected to be a dictionary of key value pairs.
    more_config = load_yaml_config_file(config_file, app._config["environment"])
    app._config.update(more_config)

    # Log the config for debugging purposes
    app._logger.debug(f"config is {app._config}\n")
    return

#-----------------------------------------------------------------------------
@function_logger
def set_command_line_values(app):
        parser = ArgumentParser(description="TROBanking")
        parser.add_argument(
            "-s",
            "--start_date",
            required=False,
            help="Date of the earliest transaction.",
        )
        parser.add_argument(
            "-f",
            "--finish_date",
            required=False,
            help="Date of the last transaction.",
        )
        parser.add_argument(
            "-c",
            "--cfgfile",
            required=False,
            default="etc/tro_banking.cfg",
            help="Name of the configuration file to use",
        )
        args = parser.parse_args()
        app._config.update(args.__dict__)

        # Log the config for debugging purposes
        app._logger.debug(f"config is {app._config}\n")

        return

#-----------------------------------------------------------------------------
def load_yaml_config_file(file_path, environment):

    yaml = pyyaml.YAML(typ="safe")
    with open(file_path) as f:
        cfg = yaml.load(f)
        return cfg[environment] 