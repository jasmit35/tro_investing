"""
categories.py
This module is used to interact with the 'categories' table in the database.
"""

from dataclasses import dataclass

from fire_starter import function_logger, getLogger
from python.services.std_dbconn import DatabaseConnection


# =======================================================================================================================
@dataclass
class Category:
    _category_id: int = 0
    _category_name: str = None
    _category_type_fk: int = 0
    _category_group_fk: int = 0
    _category_description: str = None
    _category_hidden: bool = False


# =======================================================================================================================
class Categories:
    def __init__(self, database_connection: DatabaseConnection):
        self._logger = getLogger()
        self._logger.debug(f"Begin 'Categories.__init__({database_connection=})")

        self._database_connection = database_connection

        self._logger.debug("End   'Categories.__init__' returns - None")

    def __str__(self):
        return "Categories"

    def __repr__(self):
        return "Categories"

    # ----------------------------------------------------------------------------------------------------------------------
    #  @function_logger  #  Generates too much log output to be useful
    def get_by_name(self, category_name: str, insert_missing: bool = False) -> Category:
        sql = "SELECT * FROM tro.categories WHERE category_name = %s"

        with self._database_connection.get_cursor() as cursor:
            cursor.execute(sql, (category_name,))
            results = cursor.fetchone()

        the_category = (
            None
            if results is None
            else Category(
                _category_id=results[0],
                _category_name=results[1],
                _category_type_fk=results[2],
                _category_group_fk=results[3],
                _category_description=results[4],
                _category_hidden=results[5],
            )
        )

        if the_category is None and insert_missing:
            new_category = Category(_category_name=category_name)
            the_category = self.insert(new_category)

        return the_category

    # ------------------------------------------------------------------------------------------------------------------
    @function_logger
    def insert(self, category: Category) -> int:
        sql = "INSERT INTO tro.categories VALUES (DEFAULT, %s, %s, %s, %s, %s) RETURNING category_id"

        with self._database_connection.get_cursor() as cursor:
            cursor.execute(
                sql,
                (
                    category._category_name,
                    category._category_type_fk,
                    category._category_group_fk,
                    category._category_description,
                    category._category_hidden,
                ),
            )
            category_id = cursor.fetchone()[0]

        return category_id

    # ------------------------------------------------------------------------------------------------------------------
    @function_logger
    def update(self, category_id, category_data):
        sql = """
            update tro.categories
                set category_name = %s,
                    category_type_fk = %s,
                    category_group_fk = %s
            where category_id = %s
            """
        with self._database_connection.get_cursor() as cursor:
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
        with self._database_connection.get_cursor() as cursor:
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
        with self._database_connection.get_cursor() as cursor:
            cursor.execute(sql)

    # ------------------------------------------------------------------------------------------------------------------
    @function_logger
    def get_row_count(self):
        sql = """
            select count(*) from tro.categories;
        """
        with self._database_connection.get_cursor() as cursor:
            cursor.execute(sql)
            row_count = cursor.fetchone()[0]

        return row_count

    # ----------------------------------------------------------------------
    @function_logger
    def check_for_new_categories(self, dataframe):
        new_category_names = []
        for category_name in dataframe["Category"].unique():
            #  Check if the category exists in the database
            category_id = self.get_by_name(category_name)

            #  If the category doesn't exist, insert it
            if category_id is None:
                new_category = Category(_category_name=category_name)
                self.insert(new_category)
                new_category_names.append(category_name)

        return new_category_names


"""
    #------------------------------------------------------------------------------------------------------------------
    def _load_cache(self):
        self._logger.info("Begin 'CategoriesTable._load_cache' arguments - None")

        sql =
            select category_name, category_id
            from tro.categories
            order by category_name

        with self._database_connection.get_cursor() as cursor:
            cursor.execute(sql)
            results = cursor.fetchall()
            for result in results:
                self._cache[result[0]] = result[1]

            entries = len(self._cache)

        self._logger.info(f"End   'CategoriesTable._load_cache' returns - {entries}")
"""
