"""
accounts.py
Model for managing account information in the database.
"""

from dataclasses import dataclass

from fire_starter import function_logger, getLogger
from python.services.std_dbconn import DatabaseConnection


@dataclass
class Account:
    _account_id: int = 0
    _account_name: str = None
    _account_type: str = "unknown"


class Accounts:
    _logger: any = None
    _database_connection: DatabaseConnection = None

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, database_connection: DatabaseConnection):
        self._logger = getLogger("fire_starter")
        self._logger.debug(f"Begin 'Accounts.__init__' arguments - ({database_connection=})")

        self._database_connection = database_connection

        self._logger.debug("End   'Accounts.__init__' returns - None")

    def __str__(self):
        return "Accounts"

    def __repr__(self):
        return "Accounts"

    # ----------------------------------------------------------------------
    def get_by_name(self, account_name: str, insert_missing: bool = False) -> Account:
        sql = "SELECT * FROM tro.accounts WHERE account_name = %s"

        with self._database_connection.get_cursor() as cursor:
            cursor.execute(sql, (account_name,))
            results = cursor.fetchone()

        the_account = (
            None
            if results is None
            else Account(_account_id=results[0], _account_name=results[1], _account_type=results[2])
        )

        if the_account is None and insert_missing is True:
            the_account = Account(_account_name=account_name)
            self.insert(the_account)

        return the_account

    # ----------------------------------------------------------------------
    def insert(self, account: Account):

        sql = "INSERT INTO tro.accounts VALUES (DEFAULT, %s, %s) RETURNING account_id"

        with self._database_connection.get_cursor() as cursor:
            cursor.execute(sql, (account._account_name, account._account_type))
            account_id = cursor.fetchone()[0]

        return account_id

    # ----------------------------------------------------------------------
    @function_logger
    def check_for_new_accounts(self, dataframe):
        new_account_names = []
        for account_name in dataframe["Account"].unique():
            #  Check if the account exists in the database
            account = self.get_by_name(account_name)

            #  If the account doesn't exist, insert it
            if account is None:
                new_account = Account(_account_name=account_name, _account_type="Unknown")
                self.insert(new_account)
                new_account_names.append(account_name)

        return new_account_names


# ======================================================================================================================
