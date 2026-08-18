"""
invest_trans.py

Support for managing investing transactions in the database.
"""

import datetime
from dataclasses import dataclass
from logging import getLogger

from psycopg import connect


# ======================================================================================================================
@dataclass
class InvestTran:
    transaction_id: int = 0
    account_fk: int = 0
    transaction_date: datetime.date = None
    action: str = None
    security_fk: int = 0
    symbol: str = None
    category_fk: int = 0
    memo: str = None
    price: float = 0.0
    shares: float = 0.0
    commission: float = 0.0
    amount: float = 0.0
    data_source: str = "quicken"


# ======================================================================================================================
class InvestTrans:
    def __init__(self, database_connection: connect) -> None:
        self._logger = getLogger()
        self._database_connection: connect = database_connection

    # ------------------------------------------------------------------------------------------------------------------
    def delete_range(self, start_date, end_date) -> int:
        sql = """
            DELETE FROM tro.invest_trans
            WHERE transaction_date >= %s AND transaction_date <= %s
            AND data_source = 'quicken'
            """
        with self._database_connection.cursor() as cursor:
            cursor.execute(sql, (start_date, end_date))

            #  return cursor.rowcount

    # ------------------------------------------------------------------------------------------------------------------
    def insert(self, trans) -> int:
        sql = """
            INSERT INTO tro.invest_trans
            VALUES (DEFAULT, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING transaction_id
        """
        with self._database_connection.cursor() as cursor:
            cursor.execute(
                sql,
                (
                    trans.account_fk,
                    trans.transaction_date,
                    trans.action,
                    trans.security_fk,
                    trans.symbol,
                    trans.category_fk,
                    trans.memo,
                    trans.price,
                    trans.shares,
                    trans.commission,
                    trans.amount,
                    trans.data_source,
                ),
            )
            transaction_id = cursor.fetchone()

        return transaction_id


# ======================================================================================================================
