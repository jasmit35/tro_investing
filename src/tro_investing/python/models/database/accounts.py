"""
accounts.py
Model for managing account information in the database.
"""

from dataclasses import dataclass
from logging import getLogger


@dataclass
class Account:
    account_id: int = 0 
    account_name: str = None
    account_type: str = None

class Accounts:
    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, db_conn):
        self._logger = getLogger()
        self._logger.info(f"Begin 'Accounts.__init__' arguments - ({db_conn=})")

        self._db_conn = db_conn

        self._logger.info("End   'Accounts.__init__' returns - None")

    # ------------------------------------------------------------------------------------------------------------------
    def __str__(self):
        return "Accounts"

    __repr__ = __str__

    # ----------------------------------------------------------------------
    def get_id(self, account_name, insert_missing=False):
        sql = "select account_id from tro.accounts where account_name = %s"

        with self._db_conn.cursor() as cursor:
            cursor.execute(sql, (str(account_name), ))
            results = cursor.fetchone()

        account_id = None if results is None else results[0]

        if account_id is None and insert_missing is True:
            account_id = self.insert(account_name)

        return account_id

    # ----------------------------------------------------------------------
    def insert(self, account_name):
        sql = """
            insert into tro.accounts (account_name, account_type)
            values (%s, 'Unknown')
            returning account_id
        """

        with self._db_conn.cursor() as cursor:
            cursor.execute(sql, (account_name,))
            account_id = cursor.fetchone()[0]

        return account_id

    # ----------------------------------------------------------------------
    def check_dataframe_for_new_accounts(self, dataframe):
        new_account_names = []
        for account_name in dataframe["Account"].unique():

            #  Check if the account exists in the database
            account_id = self.get_id(account_name)

            #  If the account doesn't exist, insert it
            if account_id is None:
                account_id = self.insert(account_name)
                new_account_names.append(account_name)

        return new_account_names

