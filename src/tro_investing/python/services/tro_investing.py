"""
tro_investing - Import quicken investing transactions into the tro database.
"""

#  from argparse import ArgumentParser
#  from os import environ
from datetime import datetime, timedelta
from pathlib import Path
from time import sleep

from python.config import (
    set_command_line_values,
    set_config_file_values,
    set_default_values,
)
from python.services.investing_transactions_processor import InvestingTransactionsProcessor
from python.services.std_app import StdApp
from python.services.std_dbconn import get_database_connection
from python.services.std_logging import function_logger
from python.services.std_report import StdReport
from python.services.version import get_version
from schedule import every, idle_seconds, run_pending


# =============================================================================
class TroInvesting(StdApp):

    #  -----------------------------------------------------------------------------
    def __init__(self):
        super().__init__("tro_investing", get_version())

        self._config = {}
        self._config["app_name"] = self._app_name
        self._config["version"] = self._version

        #  The default for the report file is expected to be in a 'reports' 
        #  directory under the current working directory.
        current_directory = Path.cwd()
        report_file = current_directory / "reports"
        report_path = Path(report_file)
        self._config["report_path"] = report_path

        self._output_report = StdReport(self._config["app_name"], self._config["version"], self._config["report_path"])

        self._max_return_code = 0

        return

    #  -----------------------------------------------------------------------------
    def __del__(self):

        self._output_report.print_footer(self._max_return_code)

        if hasattr(self, '_output_report'):
            del self._output_report
        return

    # -------------------------------------------------------------------------------
    def __str__(self):
        return "TroInvesting"

    __repr__ = __str__

    #-----------------------------------------------------------------------------
    #  Configure the app by setting the defaults, reading the config file and processing the command line parameters.
    @function_logger
    def configure(self):
        set_default_values(self)
        set_config_file_values(self)
        set_command_line_values(self)

        try:
            self._db_conn = get_database_connection(self._config["environment"])
        except Exception as e:
            self.report(f"Error occurred while connecting to database: {e}\n")
            raise e

        return

    #  -----------------------------------------------------------------------------
    @function_logger
    def run(self):
        run_time = datetime.now().strftime("%H:%M")
        self.report(f"run time : {run_time} - processing files\n")

        #  every 15 minutes for the next 24 hours process the stagged files
        #  stop_time = datetime.timedelta(hours=24)
        #  every(15).minutes.until(stop_time).do(this_app.process_stagged_files)
        stop_time = timedelta(minutes=15)
        #  stop_time = timedelta(hours=1)
        #  stop_time = timedelta(hours=24)
        every(5).minutes.until(stop_time).do(self.process_stagged_files)
        #  every(60).minutes.until(stop_time).do(self.process_stagged_files)

        while True:
            n = idle_seconds()  # seconds until the next job is due

            if n is None:  # no more jobs to run
                self.report("No more jobs to run. Exiting.\n")
                break

            if n > 0:
                sleep(n)  # sleep until the next job is due
                self.report("Running pending jobs...\n")
                run_pending()

        return 0

    #  -----------------------------------------------------------------------------
    def report(self, msg):
        self._output_report.report(msg)

    #  -----------------------------------------------------------------------------
    @function_logger
    def process_stagged_files(self):
        file_list = self.filter_list()
        run_time = datetime.now().strftime("%H:%M")

        if len(file_list) > 0:
            for file in file_list:
                self.report(f"    processing file {file}\n")
                invest_trans_processor = InvestingTransactionsProcessor(self._db_conn, self._output_report, file)
                rc = invest_trans_processor.process_file()

                if rc > self._max_return_code:
                    self._max_return_code = rc

                new_file_path = f"{file}.bkp"
                file.rename(new_file_path)
        else:
            self.report(f"run time : {run_time} - no files to process\n")

        return None

    #-----------------------------------------------------------------------------
    #  The files to process are expected to be in the stage directory,
    #  and have a name that starts with "invest" and have a suffix of ".xlsx".
    #-----------------------------------------------------------------------------
    @function_logger
    def filter_list(self):
        file_list = []

        for stage_file in self._config["stage_dir_path"].iterdir():

            if stage_file.name[:6] == "invest" and  stage_file.suffix == ".xlsx":
                file_list.append(stage_file)

        return file_list

    #  -----------------------------------------------------------------------------
    @function_logger
    def close(self):

        self._output_report.print_footer(self._max_return_code)
#          self._output_report = None

        return
#
#          #  final_return_code = this_app._max_return_code
#          #  this_app = None  # clean up
#          #  exit(final_return_code)
#
#      #  -----------------------------------------------------------------------------
#      def fred(self):
#
#          self._max_return_code = 0
#
#        environment = "devl"
#          self._yaml_cfg = self.load_yaml_cfg(environment)
#          self._db_conn = get_database_connection(environment, self._yaml_cfg)
#          self._stage_dir_path = self.set_stage_dir_path()
#
#  witch to the application user and set up the venv for the application.
#
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
