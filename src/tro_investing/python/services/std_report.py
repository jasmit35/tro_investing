"""
std_report.py
"""

from datetime import datetime
from pathlib import Path


class StdReport:
    #  -----------------------------------------------------------------------------
    def __init__(self, app_name="Hello World", version="v0.0.0.0", rpt_dir="reports") -> None:
        self._app_name = app_name
        self._version = version
        self._rpt_dir = rpt_dir

        rpt_file_path = Path(self._rpt_dir) / f"{self._app_name}_{datetime.now().strftime('%Y_%m_%d_%H_%M')}.rpt"
        self._file = open(rpt_file_path, "w")  # noqa: SIM115

    # -----------------------------------------------------------------------------------------------
    def __str__(self):
        return "StdReport"

    # -----------------------------------------------------------------------------------------------
    def __repr__(self):
        return "StdReport"

    #   -----------------------------------------------------------------------------
    def __del__(self):
        self._file.close()

    #  -----------------------------------------------------------------------------
    def report(self, output_string) -> None:
        self._file.write(output_string)

    #  -----------------------------------------------------------------------------
    def print_header(self) -> None:
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
    def print_footer(self, return_code) -> None:
        end_date = datetime.today().strftime("%m/%d/%y %H:%M:%S %z")

        self.report(("-" * 132) + "\n")
        if return_code == 0:
            self.report(f"Finished successfully at {end_date}\n")
        else:
            self.report(f"FAILED! With return code {return_code} at {end_date}\n")

        self.report(("=" * 132) + "\n")

    #  -----------------------------------------------------------------------------
    def get_contents(self):
        self._file.flush()
        with open(self._rpt_file_path) as contents:
            return contents.read()
