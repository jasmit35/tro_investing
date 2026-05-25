"""
std_report.py
"""

from datetime import datetime
from logging import getLogger
from pathlib import Path

from python.services.std_logging import function_logger


class StdReport:
    #  -----------------------------------------------------------------------------
    def __init__(self, app_name = "Hello World", version="v0.0.0.0", rpt_dir="reports"):
        self._logger = getLogger()
        self._logger.info(f"Begin 'StdReport.__init__      ' arguments - ({app_name=}, {version=}, {rpt_dir=})")

        self._app_name = app_name
        self._version = version

        self._rpt_file_path = Path(rpt_dir) / f"{self._app_name}_{datetime.now().strftime('%Y_%m_%d_%H_%M')}.rpt"
        self._file = open(self._rpt_file_path, "w")  # noqa: SIM115

        self.print_header()
        self._logger.info("End   'StdReport.__init__      ' returns - None")

    #-----------------------------------------------------------------------------------------------
    def __str__(self):
        return "StdReport"

    __repr__ = __str__

    #   -----------------------------------------------------------------------------
    def __del__(self):

        #  self.print_footer(0)

        #  if hasattr(self, '_file'):
        #      self._file.close()

        #  self._logger.info("End   'StdReport.__del__      ' returns - None")
        return

    #  -----------------------------------------------------------------------------
    def report(self, output_string):
        self._file.write(output_string)

    #  -----------------------------------------------------------------------------
    @function_logger
    def print_header(self):
        start_date = datetime.today().strftime("%m/%d/%y")
        start_time = datetime.today().strftime("%H:%M:%S %z")

        self.report(("=" * 132) + "\n")

        self._file.write(f"{self._app_name}")
        blank_spaces = 132 - len(self._app_name) - 8
        self._file.write(" " * blank_spaces)
        self._file.write(f"{start_date}\n")

        self._file.write(f"Version - {self._version}")
        blank_spaces = 132 - len(self._version) - 18
        self._file.write(" " * blank_spaces)
        self._file.write(f"{start_time}\n")

        self._file.write(("-" * 132) + "\n")

    #  -----------------------------------------------------------------------------
    @function_logger
    def print_footer(self, return_code):
        #  end_date = datetime.today().strftime("%m/%d/%y")

        self.report(("-" * 132) + "\n")
        #  if return_code == 0:
        #  self.report(f"Finished successfully at {end_date}\n")
        #  else:
        #  self.report(f"FAILED! With return code {return_code} at {end_date}\n")

        self.report(("=" * 132) + "\n")

    #  -----------------------------------------------------------------------------
    def get_contents(self):
        self._file.flush()
        with open(self._rpt_file_path) as contents:
            return contents.read()

"""
    #  -----------------------------------------------------------------------------
    @function_logger
    def set_rpt_file_path(self, rpt_file_dir="reports"):
        p = Path(rpt_file_dir)
        p = p.absolute()
        if not p.exists():
            self._logger.info(f"Report directory {p} does not exist.\n")
            return None

        if not p.is_dir():
            self._logger.info(f"Report directory {p} is not a directory.\n")
            return None

        #     today = datetime.datetime.now().strftime("%m_%d_%y_%H_%M")
        today = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
        file_name = f"{self._app_name}_{today}.rpt"
        file_path = p / (file_name)

        return file_path
"""
