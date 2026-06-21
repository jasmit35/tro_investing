"""
investing_transactions_processor.py

This module provides the InvestingTransactionsProcessor class for processing
transactions from an Excel spreadsheet.
"""
from datetime import datetime
from logging import getLogger
from math import isnan
from pathlib import Path

import pandas as pd
from python.models.database.accounts import Accounts
from python.models.database.categories import Categories
from python.models.database.invest_trans import InvestTrans
from python.models.database.securites import Securities
from python.services.std_logging import function_logger


# ======================================================================
class InvestingTransactionsProcessor:
    def __init__(self, db_conn, report, file_path):
        self._logger = getLogger()
        self._logger.info(f"Begin 'InvestingTransactionsProcessor.__init__({file_path=})")

        self._db_conn = db_conn
        self._report = report
        self._file_path = file_path

        self._accounts = Accounts(self._db_conn)
        self._invest_trans = InvestTrans(self._db_conn)
        self._categories = Categories(self._db_conn)
        self._securities = Securities(self._db_conn)

        self._logger.info("End   'InvestingTransactionsProcessor.__init__()")

    # -------------------------------------------------------------------------------------------------
    def __str__(self):
        return f"InvestingTransactionsProcessor({self._file_path=})"

    __repr__ = __str__

    # --------------------------------------------------------------------------------------------------
    #  Short cut to report a single message
    def report(self, msg):
        self._report.report(msg)

    # ----------------------------------------------------------------------
    @function_logger
    def process_file(self):
        """
        Process the transactions in the Excel file.
        """
        #  First determine the date range the transactions are for.
        #  Then delete the existing transactions for that date range.
        start_date, end_date = self.extract_date_range()
        self.delete_obsolete_tranactions(start_date, end_date)

        #  Load data into pandas dataframe
        pd.set_option("future.no_silent_downcasting", True)
        df = pd.read_excel(self._file_path, engine="openpyxl", header=4)

        #  Use pandas to clean the data before processing
        df = self.massage_data(df)

        #  Save the cleaned data to a new Excel file for reference
        cleaned_file_path = Path(self._file_path).with_name(self._file_path.stem + "_cleaned")
        df.to_excel(cleaned_file_path, index=False) 

        #  Check for any new accounts and add them to the database
        new_account_names = self._accounts.check_dataframe_for_new_accounts(df)
        if new_account_names.__len__() > 0:
            self.report("\n\n    The following new accounts have been added:\n")
            for account_name in new_account_names:
                self.report(f"      {account_name}\n")  

        #  Check for any new categories and add them to the database
        new_category_names = self._categories.check_dataframe_for_new_categories(df)
        if new_category_names.__len__() > 0:
            self.report("\n\n    The following new categories have been added:\n")
            for category_name in new_category_names:
                self.report(f"      {category_name}\n")  

        #  Load the transactions from the dataframe
        rc = self.load_transactions_from_dataframe(df)
        self._report.print_footer(rc)

        return rc

    # ----------------------------------------------------------------------
    #  @function_logger
    def massage_data(self, df):
        """
        Use pandas to clean the data before processing
        """
        # Drop the last 4 rows
        df = df.iloc[:-4]

        #  Drop all rows and columns that are completely empty
        df = df.dropna(axis=0, how="all")
        df = df.dropna(axis=1, how="all")

        #  Assign the desired column names
        df.columns = ['Date', 'Account', 'Action', 'Symbol', 'Security', 'Category', 'Memo',
            'Price', 'Shares', 'Commission', 'Cash', 'Invested']

        #  Drop the rows that don't have an action since they are not transactions.
        df.dropna(subset=['Action'], inplace=True)

        # Fill in blank values with the previous value for the listed columns
        cols = ["Date", "Account"]
        df.loc[:, cols] = df.loc[:, cols].ffill()

        # Fill in some of the NaN values
        df.fillna({"Symbol": "Unknown"}, inplace=True)
        df.fillna({"Security": "Unknown"}, inplace=True)
        
        df.fillna({"Category": ""}, inplace=True)
        df.fillna({"Memo": ""}, inplace=True)
        
        df.fillna({"Shares": 0}, inplace=True)
        df.fillna({"Commission": 0}, inplace=True)
        df.fillna({"Cash": 0}, inplace=True)

        return df   

    # ----------------------------------------------------------------------
    @function_logger
    def load_transactions_from_dataframe(self, df):
        """
        Read each row of the dataframe and turn it into an investment transaction record.
        """
        self.report("\n\n    The following transactions have been added:\n")
        self.report(("=" * 132) + "\n")
        self.report((" " * 8) + "Account")
        self.report((" " * 20) + "Date")
        self.report((" " * 20) + "Category")
        self.report((" " * 20) + "Amount")
        self.report("\n")

        for row in df.itertuples():
            #  Skip balance rows since they don't have a valid date and are not transactions.
            if type(row.Date) is str and row.Date[:7] == "BALANCE":
                continue

            #  Skip rows that don't have a valid security.
            if type(row.Security) is None:
                continue    

            # Use data from each dataframe row to create InvestTrans object and insert it
            nt = InvestTrans()

            #  Get the values for the foreign keys
            nt.account_fk  = self._accounts.get_id(row.Account, True)
            nt.security_fk = self._securities.get_id(row.Symbol, row.Security, True)
            nt.category_fk = self._categories.get_id(row.Category, True)

            #  Set the remaining values for the transaction record.
            nt.transaction_date = row.Date
            nt.action           = row.Action
            nt.symbol           = row.Symbol
            nt.memo             = row.Memo

            nt.price            = row.Price
            nt.shares           = row.Shares
            nt.commission       = row.Commission
            if isnan(row.Invested): 
                nt.amount = row.Cash
            else:
                nt.amount = row.Invested

            #  
            self._invest_trans.insert(self._db_conn, nt)

            #  Report the transaction that was just added.
            amount_string = f"{nt.amount:10.2f}"
            self.report(
                f"      {row.Account.ljust(35)} {nt.transaction_date.strftime('%m/%d/%y').ljust(10)} \
                     {str(row.Category).ljust(35)} {amount_string} \n"
            )
        self._report.print_footer(0)    

        return 0

    # ----------------------------------------------------------------------
    @function_logger
    def extract_date_range(self) -> tuple[datetime, datetime]:
        df = pd.read_excel(self._file_path, engine="openpyxl")
        #  The date range is expected to be in the first row, first column, and look like "01/01/2024 - 01/31/2024"
        date_raw_header = df.iloc[1, 0]
        date_header_split = date_raw_header.split()
        start_date = date_header_split[3]
        end_date = date_header_split[5]
        return start_date, end_date

    # ----------------------------------------------------------------------
    def delete_obsolete_tranactions(self, start_date, end_date):
        sql = """
            DELETE FROM tro.invest_trans 
            WHERE transaction_date >= %s AND transaction_date <= %s 
            AND DATA_SOURCE = 'quicken'
            """
        with self._db_conn.cursor() as cursor:
            cursor.execute(sql, (start_date, end_date))
            return cursor.rowcount
