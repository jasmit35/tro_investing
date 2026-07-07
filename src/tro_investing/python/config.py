from argparse import ArgumentParser

from ruamel import yaml as pyyaml

from python.services.std_logging import function_logger

#  from python.services.std_report import StdReport


#-----------------------------------------------------------------------------
def configure_app(app):
    #  app.set_default_values()
    app.set_config_file_values()
    app.set_command_line_values()

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
"""
        #-----------------------------------------------------------------------------
@function_logger
def set_default_values(app):
    app.set_default_values()

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
"""
