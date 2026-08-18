"""
securities.py

Model for managing security information in the database.
"""

from dataclasses import dataclass


# ======================================================================================================================
@dataclass
class Security:
    _security_id: int
    _security_name: str
    _security_symbol: str
    _security_type: str
    _security_class: str


# ======================================================================================================================
class Securities:
    def __init__(self, db_conn) -> None:
        self._database_connection = db_conn

    # ------------------------------------------------------------------------------------------------------------------
    def get_by_name(self, security_name=None, insert_missing=False) -> Security:
        sql = "select * from tro.securities where security_name = %s"

        with self._database_connection.cursor() as cursor:
            cursor.execute(sql, (security_name,))
            results = cursor.fetchone()

            the_security = (
                None
                if results is None
                else Security(
                    _security_id=results[0],
                    _security_name=results[1],
                    _security_symbol=results[2],
                    _security_type=results[3],
                    _security_class=results[4],
                )
            )

        if the_security is None and insert_missing is True:
            the_security = Security()
            the_security._security_name = security_name

            the_security = self.insert(the_security)

        return the_security

    # ------------------------------------------------------------------------------------------------------------------
    def insert(self, security):
        sql = "insert into tro.securities values (DEFAULT, %s, %s, %s, %s) returning security_id"

        with self._database_connection.cursor() as cursor:
            cursor.execute(
                sql,
                (security._security_name, security._security_symbol, security._security_type, security._security_class),
            )
            security_id = cursor.fetchone()[0]

        return security_id

    # ------------------------------------------------------------------------------------------------------------------
    def check_for_new_securities(self, dataframe):
        new_security_names = []

        for security_name in dataframe["Security"].unique():
            #  insure the security exists in the database
            security = self.get_by_name(security_name)
            if security is None:
                new_security_names.append(security_name)
                self.insert(Security(_security_name=security_name))

        return new_security_names
