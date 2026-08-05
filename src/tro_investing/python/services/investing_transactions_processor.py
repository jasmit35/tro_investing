"""
investing_transactions_processor.py

This module provides the InvestingTransactionsProcessor class for processing
transactions from an Excel spreadsheet.
"""

from datetime import datetime
from math import isnan
from pathlib import Path

import pandas as pd
from fire_starter import function_logger
from python.models.database.accounts import Accounts
from python.models.database.categories import Categories
from python.models.database.invest_trans import InvestTran, InvestTrans
from python.models.database.securites import Securities


#======================================================================
class InvestingTransactionsProcessor:
    #--------------------------------------------------------------------------------------------------------------------------------------------
    #  Dunder methods
    def __init__(self, logger, report, db_conn, file_path) -> None:
        self._logger = logger
        self._logger.info(f"Begin 'InvestingTransactionsProcessor.__init__({file_path=})")
        self._report = report
        self._db_conn = db_conn
        self._file_path = file_path

        self._accounts = Accounts(self._db_conn)
        self._invest_trans = InvestTrans(self._db_conn)
        self._categories = Categories(self._db_conn)
        self._securities = Securities(self._db_conn)

        self._logger.info("End   'InvestingTransactionsProcessor.__init__()")

    def __str__(self) -> str:
        return f"InvestingTransactionsProcessor({self._file_path=})"

    def __repr__(self) -> str:
        return f"InvestingTransactionsProcessor({self._file_path=})"

    #----------------------------------------------------------------------
    def check_for_new_stuff(self, dataframe):
        #  Check for any new accounts and add them to the database
        new_account_names = self._accounts.check_for_new_accounts(dataframe)
        if not new_account_names:
            self._logger.info("No new accounts were found")
        else:
            self.report("\n\n    The following new accounts have been added:\n")
            for account_name in new_account_names:
                self.report(f"      {account_name}\n")

        #  Check for any new securities and add them to the database
        new_security_names = self._securities.check_for_new_securities(dataframe)
        if not new_security_names:
            self._logger.info("No new securities were found")
        else:
            self.report("\n\n    The following new securities have been added:\n")
            for security_name in new_security_names:
                self.report(f"      {security_name}\n")

        #  Check for any new categories and add them to the database
        new_category_names = self._categories.check_for_new_categories(dataframe)
        if not new_category_names:
            self._logger.info("No new categories were found")
        else:
            self.report("\n\n    The following new categories have been added:\n")
            for category_name in new_category_names:
                self.report(f"      {category_name}\n")

    #----------------------------------------------------------------------
    @function_logger
    def process_file(self):
        """
        Process the transactions in the Excel file.
        """
        #  Determine the date range the transactions are for.
        start_date, end_date = self.extract_date_range()

        #  Delete the existing transactions for that date range.
        self._invest_trans.delete_range(start_date, end_date)

        #  Load data into pandas dataframe
        pd.set_option("future.no_silent_downcasting", True)
        dataframe = pd.read_excel(self._file_path, engine="openpyxl", header=4)

        #  Use pandas to clean the data before processing
        dataframe = self.massage_data(dataframe)

        #  Save the cleaned data to a new Excel file for reference only
        cleaned_file_path = Path(self._file_path.parent) / f"cleaned_{self._file_path.stem}.{self._file_path.suffix}"
        dataframe.to_excel(cleaned_file_path, index=False)

        #  Check for any new accounts, categories, and securities and add them to the database
        self.check_for_new_stuff(dataframe)

        #  Load the transactions from the dataframe
        rc = self.load_transactions_from_dataframe(dataframe)
        #  self._report.print_footer(rc)

        return rc

    #--------------------------------------------------------------------------------------------------
    #  Short cut to report a single message
    def report(self, msg) -> None:
        self._report.report(msg)

    #------------------------------------------------------------------------------------------------------------------
    @function_logger
    def massage_data(self, dataframe):
        """
        Use pandas to clean the data before processing
        """
        # Drop the last 4 rows
        dataframe = dataframe.iloc[:-4]

        #  Drop all rows and columns that are completely empty
        dataframe = dataframe.dropna(axis=0, how="all")
        dataframe = dataframe.dropna(axis=1, how="all")

        #  Assign the desired column names
        dataframe.columns = [
            "Date",
            "Account",
            "Action",
            "Security",
            "Symbol",
            "Category",
            "Memo",
            "Price",
            "Shares",
            "Commission",
            "Cash",
            "Invested",
            "cash+invested",
        ]

        #  Drop the rows that don't have an action since they are not transactions.
        dataframe.dropna(subset=["Action"], inplace=True)

        # Fill in blank values with the previous value for the listed columns
        cols = ["Date", "Account"]
        dataframe.loc[:, cols] = dataframe.loc[:, cols].ffill()

        # Fill in some of the NaN values
        dataframe.fillna({"Security": "Unknown"}, inplace=True)
        dataframe.fillna({"Category": "Unknown"}, inplace=True)

        dataframe.fillna({"Memo": ""}, inplace=True)
        dataframe.fillna({"Symbol": ""}, inplace=True)

        dataframe.fillna({"Shares": 0}, inplace=True)
        dataframe.fillna({"Commission": 0}, inplace=True)
        dataframe.fillna({"Cash": 0}, inplace=True)

        return dataframe

    #----------------------------------------------------------------------
    @function_logger
    def load_transactions_from_dataframe(self, dataframe):
        """
        Read each row of the dataframe and turn it into an investment transaction record.
        """
        self.report(("=" * 132) + "\n")
        self.report("\n\n    The following transactions have been added:\n\n")
        rpt_str = f"{'  Date'.ljust(14)}"
        rpt_str += f"{'Account'.ljust(35)}"
        rpt_str += f"{'Security'.ljust(32)}"
        rpt_str += f"{'Category'.ljust(35)}"
        rpt_str += f"{'Amount'.rjust(10)}\n"
        self.report(f"{rpt_str}\n")

        for row in dataframe.itertuples():
            #  Skip bal ance rows since they don't have a valid date and are not transactions.
            if type(row.Date) is str and row.Date[:7] == "BALANCE":
                continue

            #  Skip rows that don't have a valid security.
            if type(row.Security) is None:
                continue

            # Use data from each dataframe row to create an InvestTran object and insert it
            nt = InvestTran()

            #  Get the values for the foreign keys
            nt.account_fk = self._accounts.get_by_name(row.Account, True)._account_id
            nt.security_fk = self._securities.get_by_name(row.Security, True)._security_id
            nt.category_fk = self._categories.get_by_name(row.Category, True)._category_id

            #  Set the remaining values for the transaction record.
            nt.transaction_date = row.Date
            nt.action = row.Action
            nt.symbol = row.Symbol
            nt.memo = row.Memo

            nt.price = row.Price
            nt.shares = row.Shares
            nt.commission = row.Commission
            nt.data_source = "quicken"

            if isnan(row.Invested):
                nt.amount = row.Cash
            else:
                nt.amount = row.Invested

            #  Insert the transaction into the database
            self._invest_trans.insert(nt)

            #  Report the transaction that was just added.
            rpt_str = f"{row.Date.strftime('%m/%d/%y').ljust(10)}"
            rpt_str += f"{row.Account.ljust(35)}"
            rpt_str += f"{row.Security.ljust(35)}"
            rpt_str += f"{row.Category.ljust(35)}"
            rpt_str += f"{nt.amount:10.2f}"
            self.report(f"{rpt_str}\n")

        return 0

    #----------------------------------------------------------------------
    @function_logger
    def extract_date_range(self) -> tuple[datetime, datetime]:
        df = pd.read_excel(self._file_path, engine="openpyxl")
        #  The date range is expected to be in the first row, first column, and look like "01/01/2024 - 01/31/2024"
        date_raw_header = df.iloc[1, 0]
        date_header_split = date_raw_header.split()
        start_date = date_header_split[3]
        end_date = date_header_split[5]
        return start_date, end_date
