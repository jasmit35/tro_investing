"""
securities.py
Model for managing security information in the database.
"""
from dataclasses import dataclass
from logging import getLogger


@dataclass
class Security:
    security_id: int = None
    security_name: str = None
    security_symbol: str = None 
    security_type: str = "Unknown"
    security_class: str = None 

    #----------------------------------------------------------------------
class Securities:
    #------------------------------------------------------------------------------------------------------------------
    def __init__(self, db_conn):
        self._logger = getLogger()
        self._logger.info(f"Begin 'Securities.__init__' arguments - ({db_conn=})") 

        self._db_conn = db_conn

        self._logger.info("End   'Securities.__init__' returns - None")
    
    #----------------------------------------------------------------------
    def get_id(self, security_symbol, security_name=None, insert_missing=False):
        sql = "select security_id from tro.securities where security_symbol = %s"

        with self._db_conn.cursor() as cursor:
            cursor.execute(sql, (str(security_symbol),))
            results = cursor.fetchone()

        security_id = None if results is None else results[0]

        if security_id is None and security_name is not None:
            sql = "select security_id from tro.securities where security_name = %s"

            with self._db_conn.cursor() as cursor:
                cursor.execute(sql, (str(security_name),))
                results = cursor.fetchone()

            security_id = None if results is None else results[0]

        if security_id is None and insert_missing is True:
            security_id = self.insert(security_name=security_name, security_symbol=security_symbol)

        return security_id


    # ----------------------------------------------------------------------
    def insert(self, security_name="Unknown", security_symbol="unknown"):
        sql = """
            insert into tro.securities (security_name, security_symbol)
                values (%s, %s)
            returning security_id
        """

        with self._db_conn.cursor() as cursor:
            cursor.execute(sql, (security_name, security_symbol),)
            security_id = cursor.fetchone()[0]

        return security_id
