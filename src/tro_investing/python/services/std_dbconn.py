"""
std_dbconn

Database connection utility functions.
"""

from psycopg import connect

"""
# ======================================================================================================================
class DatabaseConnectionError:
    def __init__(self, exception: Exception):
        raise Exception
"""
"""
# ======================================================================================================================
class DatabaseConnection:
    _database: str
    _host: str
    _logger: any
    _password: str
    _port: str
    _user_id: str

    def __init__(self, database="xxx", user_id="xxx", password="xxx", host="localhost", port="5432") -> None:

        self._database = database
        self._host = host
        self._logger = getLogger("fire_starter")
        self._password = password
        self._port = port
        self._user_id = user_id
"""


def get_database_connection(host_name, host_port, database, username, password):
    connstr = f"host={host_name} port={host_port} dbname={database} user={username} password={password}"
    connection = None
    try:
        connection = connect(connstr)
    except Exception as e:
        raise e

    if connection is not None:
        connection.autocommit = True

    return connection


"""
    def get_cursor(self):

        connection_string = ( f"host={self._host} port={self._port} dbname={self._database}  \
            user={self._user_id} password={self._password}"
        )

        self._logger.info(f"Database connection string: {connection_string}")

        try:
            connection = connect(connection_string)
        except Exception as e:
            raise DatabaseConnectionError(e) from e

        if connection is not None:
            connection.autocommit = True

        return connection
"""
