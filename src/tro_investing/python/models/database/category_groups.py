"""
category_groups.py
"""

import os
import sys
from logging import getLogger

from std_logging import function_logger

code_path = os.path.abspath("../tro/python")
sys.path.append(code_path)

# tro_code_path = os.path.abspath("../tro/local/python")
# sys.path.insert(1, tro_code_path)
# from category_data import CategoryData


class CategoryGroupsTable:
    def __init__(self, db_conn):
        self._logger = getLogger()
        self._logger.info(f"Begin 'CategoryGroupsTable.__init__' arguments - ({db_conn=})")

        self._db_conn = db_conn

        self._logger.info("End   'CategoryGroupsTable.__init__' returns - None")

    # ---------------------------------------------------------------------------------------------------------------------
    def __str__(self):
        return "CategoryGroupsTable)"

    # ---------------------------------------------------------------------------------------------------------------------
    __repr__ = __str__

    # ---------------------------------------------------------------------------------------------------------------------
    # @function_logger
    def select_id_using_name(self, category_group_name):
        category_group_id = None
        sql = """
            select category_group_id
            from tro.category_groups
            where category_group = %s
        """
        with self._db_conn.cursor() as cursor:
            cursor.execute(sql, (category_group_name,))
            results = cursor.fetchone()
            if results:
                category_group_id = results[0]

        return category_group_id

    # ---------------------------------------------------------------------------------------------------------------------
    @function_logger
    def insert(self, category_group):
        if category_group in ["", None]:
            return 0
        sql = """
            insert into tro.category_groups
            (category_group)
            values (%s)
        """
        with self._db_conn.cursor() as cursor:
            cursor.execute(
                sql,
                (category_group,),
            )
        category_group_id = self.select_id_using_name(category_group)
        return category_group_id

    # ---------------------------------------------------------------------------------------------------------------------
    # @function_logger
    # def update(self, category_id, category_data):
    #     sql = """
    #         update tro.categories
    #             set category_name = %s,
    #                 category_type_fk = %s,
    #                 category_group_fk = %s
    #         where category_id = %s
    #         """
    #     with self._db_conn.cursor() as cursor:
    #         cursor.execute(
    #             sql,
    #             (
    #                 category_data.category_name,
    #                 category_data.category_type_fk,
    #                 category_data.category_group_fk,
    #                 category_id,
    #             ),
    #         )

    #     return 0

    # ---------------------------------------------------------------------------------------------------------------------
    # @function_logger
    # def delete_by_id(self, category_id):
    #     sql = """
    #         delete from tro.categories
    #         where category_id = %s
    #     """
    #     with self._db_conn.cursor() as cursor:
    #         cursor.execute(sql, (category_id,))
    #         rows_deleted = cursor.rowcount

    #         if rows_deleted == 1:
    #             return True
    #         else:
    #             return False

    # ---------------------------------------------------------------------------------------------------------------------
    @function_logger
    def reset(self):
        sql = """
            truncate tro.category_groups;
            insert into tro.category_groups (category_group_id, category_group) values (0, 'Unknown');
            select setval('tro.category_groups_category_group_id_seq', 1, False);
        """
        with self._db_conn.cursor() as cursor:
            cursor.execute(sql)

    # ---------------------------------------------------------------------------------------------------------------------
    # @function_logger
    # def get_row_count(self):
    #     sql = """
    #         select count(*) from tro.categories;
    #     """
    #     with self._db_conn.cursor() as cursor:
    #         cursor.execute(sql)
    #         row_count = cursor.fetchone()[0]

    #     return row_count
