"""
std_dbconn
"""

#  from configparser import ConfigParser


from psycopg import connect
from python.services.std_logging import function_logger
from ruamel import yaml as pyyaml


@function_logger
def get_database_connection(environment, yaml_cfg = "etc/.db_secrets.cfg"):

    yaml = pyyaml.YAML(typ="safe")
    with open(yaml_cfg) as f:
        config = yaml.load(f)

    host_name = config[environment]["hostname"]
    host_port = config[environment]["hostport"]
    database = config[environment]["database"]
    username = config[environment]["username"]
    password = config[environment]["password"]

    connstr = f"host={host_name} port={host_port} dbname={database} user={username} password={password} "

    connection = None
    try:
        connection = connect(connstr)
    except Exception as e:
        raise e 

    if connection is not None:
        connection.autocommit = True

    return connection


#  def pg_get_connection(host="localhost", port="5432", database="pgdb", username="jeff", password="password"):
#      connstr = f"dbname={database} user={username} password={password} host={host} port={port}"
#      connection = None
#
#      try:
#          connection = connect(connstr)
#      except OperationalError as e:
#          print(f"Connection error: {e}")
#
#      return connection
