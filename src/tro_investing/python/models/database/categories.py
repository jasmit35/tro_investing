"""
categories.py
===================
This module contains the Categories class which is used to interact with the 'categories' table in the database.
"""
from dataclasses import dataclass
from logging import getLogger

from python.services.std_logging import function_logger


@dataclass
class Category:
    category_id: int = 0
    category_name: str = ""
    category_type_fk: int = 0
    category_group_fk: int = 0
    category_description: str = ""
    category_hidden: bool = False

class Categories:
    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, db_conn):
        self._logger = getLogger()
        self._logger.info(f"Begin 'Categories.__init__' arguments - ({db_conn=})")

        self._db_conn = db_conn

        self._logger.info("End   'Categories.__init__' returns - None")

    # ------------------------------------------------------------------------------------------------------------------
    def __str__(self):
        return "Categories"

    __repr__ = __str__

    # ------------------------------------------------------------------------------------------------------------------
    @function_logger
    def get_id(self, category_name, insert_missing=False):
        sql = "select category_id from tro.categories where category_name = %s"

        with self._db_conn.cursor() as cursor:
            cursor.execute(sql, (str(category_name),))
            results = cursor.fetchone()

        category_id = None if results is None else results[0]

        if category_id is None and insert_missing:
            category_id = self.insert(Category(category_name=str(category_name)))

        return category_id

    #------------------------------------------------------------------------------------------------------------------
    @function_logger
    def insert(self, category_data):
        category_id = None
        sql = """
            insert into tro.categories (category_name, category_type_fk, category_group_fk)
            values (%s, %s, %s)
            returning category_id
        """
        with self._db_conn.cursor() as cursor:
            cursor.execute(
                sql,
                (
                    category_data.category_name,
                    category_data.category_type_fk,
                    category_data.category_group_fk,
                ),
            )
            results = cursor.fetchone()
            if results:
                category_id = results[0]
            return category_id

    #------------------------------------------------------------------------------------------------------------------
    @function_logger
    def update(self, category_id, category_data):
        sql = """
            update tro.categories
                set category_name = %s,
                    category_type_fk = %s,
                    category_group_fk = %s
            where category_id = %s
            """
        with self._db_conn.cursor() as cursor:
            cursor.execute(
                sql,
                (
                    category_data.category_name,
                    category_data.category_type_fk,
                    category_data.category_group_fk,
                    category_id,
                ),
            )

        return 0

    # ------------------------------------------------------------------------------------------------------------------
    @function_logger
    def delete_by_id(self, category_id):
        sql = """
            delete from tro.categories
            where category_id = %s
        """
        with self._db_conn.cursor() as cursor:
            cursor.execute(sql, (category_id,))
            rows_deleted = cursor.rowcount

            return rows_deleted == 1

    # ------------------------------------------------------------------------------------------------------------------
    @function_logger
    def reset(self):
        sql = """
            truncate tro.categories;
            insert into tro.categories OVERRIDING SYSTEM VALUE values (0, 'Uncategorized', 0, 0);
            select setval('tro.categories_category_id_seq', 1, false);
        """
        with self._db_conn.cursor() as cursor:
            cursor.execute(sql)

    # ------------------------------------------------------------------------------------------------------------------
    @function_logger
    def get_row_count(self):
        sql = """
            select count(*) from tro.categories;
        """
        with self._db_conn.cursor() as cursor:
            cursor.execute(sql)
            row_count = cursor.fetchone()[0]

        return row_count

"""
    # ------------------------------------------------------------------------------------------------------------------
    def _load_cache(self):
        self._logger.info("Begin 'CategoriesTable._load_cache' arguments - None")

        sql = 
            select category_name, category_id
            from tro.categories
            order by category_name
        
        with self._db_conn.cursor() as cursor:
            cursor.execute(sql)
            results = cursor.fetchall()
            for result in results:
                self._cache[result[0]] = result[1]

            entries = len(self._cache)

        self._logger.info(f"End   'CategoriesTable._load_cache' returns - {entries}")
"""