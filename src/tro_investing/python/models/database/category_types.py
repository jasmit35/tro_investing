"""
category_types.py
"""

import os
import sys
from logging import getLogger

code_path = os.path.abspath("../tro/python")
sys.path.append(code_path)

code_path = os.path.abspath("../local/python")
sys.path.append(code_path)

from std_logging import function_logger


class CategoryTypesTable:
    # ---------------------------------------------------------------------------------------------------------------------
    def __init__(self, db_conn):
        self._logger = getLogger()
        self._logger.info("Begin 'CategoryTypesTable.__init__' arguments - ({db_conn=})")

        self._db_conn = db_conn

        self._logger.info("End   'CategoryTypesTable.__init__' returns - None")

    # ---------------------------------------------------------------------------------------------------------------------
    def __str__(self):
        return "CategoryTypesTable"

    # ---------------------------------------------------------------------------------------------------------------------
    __repr__ = __str__

    # ---------------------------------------------------------------------------------------------------------------------
    # @function_logger
    def select_id_using_name(self, category_type):
        category_type_id = None
        sql = """
            select category_type_id
            from tro.category_types
            where category_type = %s
        """
        with self._db_conn.cursor() as cursor:
            cursor.execute(sql, (category_type,))
            results = cursor.fetchone()
            if results:
                category_type_id = results[0]

        return category_type_id

    # ---------------------------------------------------------------------------------------------------------------------
    @function_logger
    def insert(self, category_type):
        if category_type in ["", None]:
            return 0
        sql = """
            insert into tro.category_types
            (category_type)
            values (%s)
        """
        with self._db_conn.cursor() as cursor:
            cursor.execute(
                sql,
                (category_type,),
            )
        category_type_id = self.select_id_using_name(category_type)
        return category_type_id
