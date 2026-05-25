"""
transactions_processor.py

This module provides the TransactionsProcessor class for processing
transactions from an Excel spreadsheet.
"""

from datetime import datetime
from logging import getLogger

import pandas as pd
from python.models.database.accounts import Account
from python.models.database.categories_table import CategoriesTable
from python.models.database.invest_trans import InvestTrans
from python.services.std_logging import function_logger


# ======================================================================
class InvestingTransactionsProcessor:
    def __init__(self, db_conn, report, file_path):
        self._logger = getLogger()
        self._logger.info(f"Begin 'TransactionsProcessor.__init__({file_path=})")

        self._db_conn = db_conn
        self._report = report
        self._file_path = file_path

        self._accounts = Account()
        self._invest_trans = InvestTrans()
        self._categories_table = CategoriesTable(db_conn)

        self._logger.info("End   'TransactionsProcessor.__init__()")

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
        #  if start_date is not None:
        #      use_start_date = start_date
        #  if finish_date is not None:
        #      end_date = finish_date
        #  Delete the existing transactions for this date range.
        self.delete_obsolete_tranactions(start_date, end_date)

        #  Load data into dataframe and use pandas to clean it up for processingA
        pd.set_option("future.no_silent_downcasting", True)
        df = pd.read_excel(self._file_path, engine="openpyxl", header=4)
        #  Remove spaces in the column names
        df.columns = df.columns.str.replace(" ", "")
        # Drop rows that are all NaN
        df = df.dropna(axis=0, how="all")
        df = df.dropna(axis=1, how="all")  # Drop columns that are all NaN
        df = df.iloc[:-4]  # Drop the last 4 rows

        # Fill in NaN values with the previous value for the listed columns
        cols = ["Date", "Account"]
        df.loc[:, cols] = df.loc[:, cols].ffill()
        #  df.loc[:,cols] =  df.result.infer_objects(copy=False)
        #  df.loc[:,cols].infer_objects(copy=True)

        #  Replace NaN with 'U' in the Clr column
        #  cols = ["Clr"]
        #  df.loc[:, cols] = df.loc[:, cols].fillna("U")

        cols = ["Category"]
        df.loc[:, cols] = df.loc[:, cols].fillna("")
        #  Load the transactions from the dataframe
        # print(df.columns)
        rc = self.load_transactions_from_dataframe(df)
        return rc

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

            nt.account_fk = self._accounts.get_id(self._db_conn, row.Account)
            nt.transaction_date = row.Date
            nt.action = row.Action
            nt.security_fk = 0
            nt.symbol = row.Symbol
            nt.category_fk = self._categories_table.get_id_using_name(row.Category)
            nt.memo = row.Memo
            nt.price = row.Price
            nt.shares = row.Shares
            nt.commission = row.Commission
            nt.amount = row.Cash

            self._invest_trans.insert(self._db_conn, nt)


            amount_string = f"{nt.amount:10.2f}"
            self.report(
                f"      {row.Account.ljust(35)} {nt.transaction_date.strftime('%m/%d/%y').ljust(10)} \
                     {row.Category.ljust(35)} {amount_string} \n"
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

    #  ----------------------------------------------------------------------
    @function_logger
    def _set_category_name(self, row):
        if row.Num == "Added":
            return "Added"
        if row.Num == "Bought":
            return "Bought"
        if row.Num == "Removed":
            return "Removed"
        if row.Num == "StkSplit":
            return "Stock Split"
        if row.Num == "Sold":
            return "Sold"

        return "Unknown"

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
