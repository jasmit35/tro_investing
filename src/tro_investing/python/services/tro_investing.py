"""
tro_investing - Import quicken investing transactions into the tro database.
"""

#  from argparse import ArgumentParser
#  from os import environ
from datetime import datetime, timedelta
from pathlib import Path
from time import sleep

from pydantic_settings import BaseSettings
from python.services.investing_transactions_processor import InvestingTransactionsProcessor
from python.services.std_app import StdApp
from python.services.std_dbconn import get_database_connection
from python.services.std_logging import function_logger
from python.services.std_report import StdReport
from python.services.version import get_version
from schedule import every, idle_seconds, run_pending


#===================================================================================================================================
class TroInvesting(StdApp):

    _db_conn = None
    _report_dir_path = None
    _stage_dir_path = None

    #-------------------------------------------------------------------------------------------------------------------------------
    #  Dunder methods

    def __init__(self):
        super().__init__("tro_investing", get_version())

    def __repr__(self):
        return "TroInvesting"

    def __str__(self):
        return "TroInvesting"

    #-------------------------------------------------------------------------------------------------------------------------------
    @function_logger
    def load_config_file(self, config_file_path, environment):

        class Settings(BaseSettings):
            def __init__(self, environment: str):
                super().__init__()
                self._environment = environment

            def is_production(self) -> bool:
                return self._environment == "prod"

        settings = Settings(environment)
        
        self._db_conn = get_database_connection(self._environment)
        self._report_dir_path = Path.cwd() / "reports"
        self._stage_dir_path = Path.cwd() / "stage"

    #-------------------------------------------------------------------------------------------------------------------------------
    @function_logger
    def set_config_file_values(self):
        super().set_config_file_values()

        #  The config file is expected to be in the etc directory under the
        #  current working directory and should be named <app_name>.cfg
        config_dir = Path.cwd() / "etc"
        config_file_path = config_dir / f"{self._app_name}.cfg"
        self._logger.debug(f"config file path is {config_file_path}\n")

        #  If the config file does not exist or is not a file, log a warning and return.
        #  The app will use the default values in this case.
        if not config_file_path.exists():
            self._logger.warning(f"Configuration file {config_file_path} does not exist. Using defaults.\n")
            return

        if not config_file_path.is_file():
            self._logger.warning(f"Configuration file {config_file_path} is not a file. Using defaults.\n")
            return

        #  Load the config file and update the app's config with the values from the file
        more_config = self.load_config_file(config_file_path, self._environment)
        # self._config.update(more_config)

    #-------------------------------------------------------------------------------------------------------------------------------
    @function_logger
    def process_stage_dir(self):
        file_list = self.search_for_investing_files()

        if len(file_list) == 0:
            run_time = datetime.now().strftime("%H:%M")
            self._logger.info(f"run time : {run_time} - no files to process\n")
            rc = 0
        else:
            file = file_list[0]

            output_report = StdReport("TRO Investing", self._version, self._report_dir_path)
            output_report.print_header()
            output_report.report(f"\nProcessing file {file}\n")

            invest_trans_processor = InvestingTransactionsProcessor(self._db_conn, output_report, file)
            rc = invest_trans_processor.process_file()

            output_report.print_footer(rc)

            if rc > self._max_return_code:
                self._max_return_code = rc

            new_file_path = f"{file}.bkp"
            file.rename(new_file_path)

        return rc

    #-------------------------------------------------------------------------------------------------------------------------------
    @function_logger
    def run(self):
        #  run_time = datetime.now().strftime("%H:%M")
        #  self.report(f"run time : {run_time} - processing files\n")

        #  every 15 minutes for the next 24 hours process the stagged files
        #  stop_time = datetime.timedelta(hours=24)
        #  every(15).minutes.until(stop_time).do(this_app.process_stagged_files)
        stop_time = timedelta(minutes=15)
        #  stop_time = timedelta(hours=1)
        #  stop_time = timedelta(hours=24)
        every(5).minutes.until(stop_time).do(self.process_stage_dir)
    
        while True:
            n = idle_seconds()  # seconds until the next job is due

            if n is None:  # no more jobs to run
                self._logger.info("No more jobs to run. Exiting.\n")
                break

            if n > 0:
                sleep(n)  # sleep until the next job is due
                #  self.report("Running pending jobs...\n")
                run_pending()

        return 0

    #-------------------------------------------------------------------------------------------------------------------------------
    @function_logger
    def set_command_line_values(self):
        super().set_command_line_values()   


    #-------------------------------------------------------------------------------------------------------------------------------
    #  The files to process are expected to be in the stage directory,
    #  and have a name that starts with "invest" and have a suffix of ".xlsx".
    #-------------------------------------------------------------------------------------------------------------------------------
    @function_logger
    def search_for_investing_files(self):
        file_list = []

        for stage_file in self._stage_dir_path.iterdir():

            if stage_file.name[:6] == "invest" and  stage_file.suffix == ".xlsx":
                file_list.append(stage_file)

        return file_list

    #-------------------------------------------------------------------------------------------------------------------------------
#    @function_logger
#    def close(self):
#        pass


#          self._output_report.print_footer(self._max_return_code)
#          self._output_report = None

#          return
#
#          #  final_return_code = this_app._max_return_code
#          #  this_app = None  # clean up
#          #  exit(final_return_code)
#
#      @function_logger
#      def set_stage_dir_path(self):
#          # -----------------------------------------------------------------------------
#          #  The stage directory is expected to be in the current working directory and should be named "stage".i
#          #  The name of the stage directory can be overridden by setting the "stage_dir" parameter in the config file.
#          # -----------------------------------------------------------------------------
#
#          stage_dir = "stage"
#
#          cfg_stage_dir = self.cfg_file_params.get("stage_dir")
#          if cfg_stage_dir:
#              stage_dir = cfg_stage_dir
#
#          stage_dir_path = Path(stage_dir)
#          stage_dir_path = stage_dir_path.absolute()
#
#          if not stage_dir_path.exists():
#              self.report(f"Stage directory {stage_dir_path} does not exist.\n")
#              self._output_report.print_footer(1)
#              return None
#          if not stage_dir_path.is_dir():
#              self.report(f"Stage directory {stage_dir_path} is not a directory.\n")
#              self._output_report.print_footer(1)
#              return None
#
#          self.report(f"processing files in {stage_dir_path}\n")
#          return stage_dir_path
#
#
#          self._max_return_code = 0
#
#          self._output_report = StdReport("tro_banking", self.__version__)
#
#          environment = environ.get('ENVIRONMENT', 'undefined')
#          if environment not in ["devl", "test", "prod"]:
#              raise ValueError(f"Invalid environment - {environment}")
#
#          self._yaml_cfg = self.load_yaml_cfg(environment)
#          self._db_conn = get_database_connection(environment, self._yaml_cfg)
#          self._stage_dir_path = self.set_stage_dir_path()
#  """
#
"""
    #-----------------------------------------------------------------------------
    #  Configure the app by setting the defaults, reading the config file and processing the command line parameters.
    @function_logger
    def configure(self):
        set_default_values(self)
        set_config_file_values(self)
        set_command_line_values(self)

        #  Set the log level based on the value in the configuration.
        self._logger.setLevel(self._log_level)

        try:
            self._db_conn = get_database_connection(self._config["environment"])
        except Exception as e:
            self.report(f"Error occurred while connecting to database: {e}\n")
            raise e

        return
"""
"""
        #  The stage directory is expected to be in the current working directory and should be named "stage".
        #  The name of the stage directory can be overridden by setting the "stage_dir" parameter in the config file.
        cfg_stage_dir = self._config.get("stage_dir")
        if cfg_stage_dir:
            self._stage_dir_path = Path(cfg_stage_dir)
        else:
            self._stage_dir_path = Path.cwd() / "stage"

        if not self._stage_dir_path.exists():
            raise ValueError(f"Stage directory {self._stage_dir_path} does not exist.")
        if not self._stage_dir_path.is_dir():
            raise ValueError(f"Stage directory {self._stage_dir_path} is not a directory.") 
"""

"""
        #  Load the configuration file and return a dictionary of the values.
        return 
        config = {}
        with open(config_file_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                config[key] = value

        #  If the environment is specified in the config file, use it to override the environment passed in.
        if "environment" in config:
            environment = config["environment"]

        return config
    """