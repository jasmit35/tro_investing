"""
investment_transactions_processor.py

This module provides the InvestingTransactionsProcessor class for processing
transactions from an Excel spreadsheet.
"""
from datetime import datetime
from logging import getLogger
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

    #-------------------------------------------------------------------------------------------------
    def __str__(self):
        return f"InvestingTransactionsProcessor({self._file_path=})"

    __repr__ = __str__

    #--------------------------------------------------------------------------------------------------
    #  Short cut to report a single message
    def report(self, msg):
        self._report.report(msg)

    # ----------------------------------------------------------------------
    @function_logger
    def process_file(self):
        """
        Process the transactions in the Excel file.
        """
        #  First we need to determine the date range the transactions are for.
        start_date, end_date = self.extract_date_range()

        #  Delete the existing transactions for this date range.
        self.delete_obsolete_tranactions(start_date, end_date)

        #  Load data into pandas dataframe
        pd.set_option("future.no_silent_downcasting", True)
        df = pd.read_excel(self._file_path, engine="openpyxl", header=4)

        #  Use pandas to clean the data before processing
        df = self.massage_data(df)

        #  Save the cleaned data to a new Excel file for reference
        cleaned_file_path = Path(self._file_path).with_name(self._file_path.stem + "_cleaned" + self._file_path.suffix)
        df.to_excel(cleaned_file_path, index=False) 

        #  Check for any new accounts and add them to the database
        new_account_names = self._accounts.check_dataframe_for_new_accounts(df)
        if new_account_names.__len__() > 0:
            self.report("\n\n    The following new accounts have been added:\n")
            for account_name in new_account_names:
                self.report(f"      {account_name}\n")  

        #  Check for any new accounts and add them to the database
        #  new_account_names = self._accounts.check_dataframe_for_new_accounts(df)
        #  if new_account_names.__len__() > 0:
        #      self.report("\n\n    The following new accounts have been added:\n")
        #      for account_name in new_account_names:
        #         self.report(f"      {account_name}\n")  

        #  Load the transactions from the dataframe
        rc = self.load_transactions_from_dataframe(df)
        return rc

    # ----------------------------------------------------------------------
    @function_logger
    def massage_data(self, df):
        """
        Use pandas to clean the data before processing
        """
        # Drop the first and last 4 rows
        #  df = df.iloc[0:3]
        df = df.iloc[:-4]

        #  Drop all rows and columns that are completely empty
        df = df.dropna(axis=0, how="all")  # Drop rows that are all NaN
        df = df.dropna(axis=1, how="all")  # Drop columns that are all NaN

        #  Clean up the column names
        df.columns = df.columns.str.replace(" ", "")
        df.rename(columns={'Quote/Price': 'Price'}, inplace=True)

        # Fill in blank values with the previous value for the listed columns
        cols = ["Date", "Account"]
        df.loc[:, cols] = df.loc[:, cols].ffill()

        # Fill in NaN values with ""
        cols = ["Symbol, Category, Memo"]
        #  df.loc[:, cols] = df.loc[:, cols].fillna("")

        return df   

    # ----------------------------------------------------------------------
    @function_logger
    def load_transactions_from_dataframe(self, df):
        """
        Read each row of the dataframe and turn it into an investment transaction record.
        """
        self.report("\n\n    The following transactions have been added:\n")

        for row in df.itertuples():
            #  Skip balance rows since they don't have a valid date and are not transactions.
            if type(row.Date) is str and row.Date[:7] == "BALANCE":
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
            nt.amount           = row.Cash

            #  You will feel a slight push...
            self._invest_trans.insert(self._db_conn, nt)

            #  Report the transaction that was just added.
            amount_string = f"{nt.amount:10.2f}"
            self.report(
                f"      {row.Account.ljust(35)} {nt.transaction_date.strftime('%m/%d/%y').ljust(10)} \
                     {str(row.Category).ljust(35)} {amount_string} \n"
            )

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
        DELETE FROM tro.transactions
        WHERE transaction_date >= %s
        AND transaction_date <= %s
        AND DATA_SOURCE = 'quicken'
        """
        with self._db_conn.cursor() as cursor:
            cursor.execute(sql, (start_date, end_date))
            return cursor.rowcount

    # #  ----------------------------------------------------------------------
    # @function_logger
    # def validate_transaction(self, trans):
    #     """
    #     Checks a transaction record to make sure certain fields are valid,
    #     otherwise raise an exception.

    #     Args:
    #         trans (_type_): _description_

    #     Raises:
    #         InvalidTransactionException:
    #     """

    #     date_str = str(trans[trans_date_col])

    #     if "BALANCE" in date_str:
    #         raise InvalidTransactionException(trans, f"This transaction does not have a valid date - {date_str}")
    #     if "Date" in date_str:
    #         raise InvalidTransactionException(trans, f"This transaction does not have a valid date - {date_str}")

    #     amount = trans[amount_col]
    #     if amount is None:
    #         raise InvalidTransactionException(trans, 'This transaction has an invalid amount - "None"')

    # #  ----------------------------------------------------------------------
    # @function_logger
    # def load_transactions_from_workbook(self):
    #     #  The spreadsheet we are loading from does not repeat all transactions for split transactions.
    #     #  Theirfore it is necessary to retain the previous transactions.
    #     previous_transaction_date_string = "1960-01-12 00:00:00"
    #     previous_account_id = 0
    #     previous_account_name = ""
    #     previous_description = ""

    #     self.report("\n\n    The following transactions have been added:\n")

    #     rc = 0

    #     for transaction in sheet.iter_rows(min_row=1, max_row=99999, min_col=1, max_col=11, values_only=True):

    #             category_name = self._set_category_name(transaction)
    #             category_id = self._categories_table.get_id_using_name(category_name)

    #             amount = transaction[amount_col]

    #             this_trans = Transaction(account_id, transaction_date, category_id, amount)

    #             this_trans.cleared = transaction[cleared_col]
    #             this_trans.number = transaction[number_col]
    #             this_trans.tag = transaction[tag_col]

    #             this_trans.description = transaction[description_col]
    #             if this_trans.description:
    #                 previous_description = this_trans.description
    #             else:
    #                 this_trans.description = previous_description

    #             this_trans.memo = transaction[memo_col]
    #             this_trans.tax_item = transaction[tax_col]

    #             trans_tab.insert_transaction(this_trans)
    #             self.report(f"      {account_name}, {transaction_date}, {category_name}, {amount}\n")

    #         except InvalidTransactionException as e:
    #             self.report(f"\nError! {e.message}\n")
    #             self.report(f"{transaction}\n")

    #     return rc

    #     #  ----------------------------------------------------------------------
    #     @function_logger
    #     def resolve_category_id(self, category_name):
    #         category_name = self._massage_category_name(category_name)
    #         category_id = self._categories_table.get_id_using_name(category_name)
    #
    #         if category_id is None:
    #             raise InvalidTransactionException(
    #                 Transaction,
    #                 f"This transaction has an invalid category - '{category_name}'",
    #             )
    #
    #         return category_id

    # #  ----------------------------------------------------------------------
    # @function_logger
    # def load_any_new_categories(self):
    #     sheet = self._workbook.active

    #     self.report("\n\n    The following new categories have been added:\n")

    #     for transaction in sheet.iter_rows(
    #         min_row=6,
    #         max_row=99999,
    #         min_col=7,
    #         max_col=7,
    #         values_only=True,
    #     ):
    #         if len(transaction) < 6:
    #             continue

    #         category_name = self._massage_category_name(transaction)

    #         if category_name:
    #             cat_id = self._categories_table.select_id_using_name(category_name)
    #             if cat_id is None:
    #                 self.report(f"      {category_name}\n")
    #                 new_category = CategoryData(category_name)
    #                 self._categories_table.insert(new_category)
