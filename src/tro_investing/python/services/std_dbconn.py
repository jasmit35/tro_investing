"""
std_dbconn

Database connection utility functions.
"""

from psycopg import connect
from python.services.std_logging import getLogger


#======================================================================================================================
class DatabaseConnectionError(Exception):
    def __init__(self):
        logger = getLogger()
        logger.error(f"Database connection error: {self.args[0]}")  
        raise Exception

#======================================================================================================================
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
