"""
"""

from datetime import datetime, timedelta
from pathlib import Path
from time import sleep

from python.services.investing_transactions_processor import InvestingTransactionsProcessor
from python.services.std_app import StdApp
from python.services.std_dbconn import DatabaseConnection
from python.services.std_logging import function_logger
from python.services.std_report import StdReport
from python.services.version import get_version
from schedule import every, idle_seconds, run_pending


#===================================================================================================================================
class TroInvesting(StdApp):
    _database_connection: DatabaseConnection = None
    _output_report: StdReport = None
    _stage_dir_path: Path = None
    _report_dir_path: Path = None

    #-------------------------------------------------------------------------------------------------------------------------------
    #  Dunder methods

    def __init__(self):
        super().__init__("tro_investing", get_version())
        self._report_dir_path = Path.cwd() / "reports"
        self._stage_dir_path = Path.cwd() / "stage"


    def __repr__(self):
        return f"TroInvesting(f'{self._output_report=}, {self._stage_dir_path=}')"

    def __str__(self):
        return f"TroInvesting(f'{self._output_report=}, {self._stage_dir_path=}')"
        
    #-------------------------------------------------------------------------------------------------------------------------------
    @function_logger
    def process_investing_file(self):
        rc: int = 98

        file_list = self.search_for_investing_files()

        if len(file_list) == 0:
            run_time = datetime.now().strftime("%H:%M")
            self._logger.info(f"run time : {run_time} - no files to process\n")
            rc = 0

        else:
            file = file_list[0]

            output_report = StdReport(self._app_name, self._version, self._report_dir_path)
            output_report.print_header()
            output_report.report(f"\nProcessing file {file}\n")

            invest_trans_processor = InvestingTransactionsProcessor(self._logger,
                                        output_report, 
                                        self._database_connection,
                                        file)
            
            rc = invest_trans_processor.process_file()

            output_report.print_footer(rc)
            output_report = None  #  close the report file

            #  Rename the processed file to have a .bkp suffix so it is not processed again.
            new_file_path = f"{file}.bkp"
            file.rename(new_file_path)

        return rc

    #-------------------------------------------------------------------------------------------------------------------------------
    #  Short cut to report messages to the output report.
    @function_logger
    def report(self, message: str):
        self._output_report.report(message)

    #-------------------------------------------------------------------------------------------------------------------------------
    @function_logger
    def run(self):
        run_time = datetime.now().strftime("%H:%M")
        self._logger.info(f"run time : {run_time} - processing files\n")

        #  every 15 minutes for the next 24 hours process the stagged files
        #  stop_time = timedelta(hours=24)
        stop_time = timedelta(minutes=15)
        #  every(15).minutes.until(stop_time).do(this_app.process_stagged_files)
        every(5).minutes.until(stop_time).do(self.process_investing_file)

        while True:
            n = idle_seconds()  # seconds until the next job is due

            if n is None:  # no more jobs to run
                self._logger.info("No more jobs to run. Exiting.\n")
                break

            if n > 0:
                sleep(n)  # sleep until the next job is due
                self._logger.info("Running pending jobs...\n")
                run_pending()

        return 0


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

"""
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
    @function_logger
    def set_command_line_values(self):
        super().set_command_line_values()   
"""
