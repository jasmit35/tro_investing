"""
std_dbconn

Database connection utility functions.
"""

from fire_starter import function_logger
from psycopg import connect


#======================================================================================================================
class DatabaseConnectionError:
    def __init__(self, exception: Exception):
        raise Exception


#======================================================================================================================
@function_logger
class DatabaseConnection:
    def __init__(self, database, user_id, password, host="localhost", port="5432") -> None:
        self._database = database
        self._connection = None

        connection_string = (
            f"host={host} "
            + f"port={port} "
            + f"dbname={self._database} "
            + f"user={user_id} "
            + f"password={password}"
        )

        try:
            self._connection = connect(connection_string)
            self._connection.autocommit = True
        except Exception as e:
            raise DatabaseConnectionError(e) from e

    #-------------------------------------------------------------------------------------------------------------------------------
    def get_cursor(self) -> any:
        return self._connection.cursor()
