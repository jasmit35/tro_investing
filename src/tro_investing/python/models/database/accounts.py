"""
accounts.py
Model for managing account information in the database.
"""

from dataclasses import dataclass


@dataclass
class Account:
    account_id: int = None
    account_name: str = None
    account_type: str = None

    #----------------------------------------------------------------------
    def get_id(self, db_conn, account_name, insert_missing=False):
        sql = "select account_id from tro.accounts where account_name = %s"

        with db_conn.cursor() as cursor:
            cursor.execute(sql, (account_name,))
            results = cursor.fetchone()
            
        account_id = None if results is None else results[0]
        
        if account_id is None and insert_missing is True:
            account_id = self.insert(db_conn, account_name)
        
        return account_id

    #----------------------------------------------------------------------
    def insert(self, db_conn, account_name):
        sql = """
            insert into tro.accounts (account_name, account_type)
            values (%s, 'Unknown')
            returning account_id
        """
        
        with db_conn.cursor() as cursor:
            cursor.execute(sql, (account_name,))
            account_id = cursor.fetchone()[0]
        
        return account_id