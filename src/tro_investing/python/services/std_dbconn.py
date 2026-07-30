"""
std_dbconn

Database connection utility functions.
"""

from psycopg import connect
from python.services.std_logging import function_logger, getLogger


#======================================================================================================================
class DatabaseConnectionError:
    def __init__(self, exception: Exception):
        logger = getLogger()
        logger.error(f"Database connection error: {Exception}")  
        raise Exception

#======================================================================================================================
@function_logger
class DatabaseConnection:
    def __init__(self, database, user_id, password, host="localhost", port="5432"):
        self._database = database
        self._connection = None 
    
        connection_string = \
            f"host={host} " + \
            f"port={port} " + \
            f"dbname={self._database} " + \
            f"user={user_id} " + \
            f"password={password}"

        try:
            self._connection = connect(connection_string)
            self._connection.autocommit = True
        except Exception as e:
            raise DatabaseConnectionError(e) from e

    #-------------------------------------------------------------------------------------------------------------------------------
    def get_cursor(self) -> any:
        return self._connection.cursor()    
