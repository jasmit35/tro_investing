"""
category_data.py
"""

import os
import sys
from dataclasses import dataclass
from logging import getLogger

code_path = os.path.abspath("../tro/python")
sys.path.append(code_path)

code_path = os.path.abspath("../local/python")
sys.path.append(code_path)

#  from std_logging import function_logger


@dataclass
class CategoryData:
    category_id: int = 0
    category_name: str = ""
    category_type_fk: int = 0
    category_group_fk: int = 0
    category_description: str = ""
    category_hidden: bool = False

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, category):
        self._logger = getLogger()
        self._logger.info("Begin 'category_data.__init__' arguments - {category}")

        self.category_id = 0
        if category:
            self.category_name = category
        self.category_type_fk = 0
        self.category_group_fk = 0
        self.category_description = ""
        self.category_tax_line_item = ""
        self.category_hidden = False

        self._logger.info("End   'categor_data.__init__' returns - None")
        return None

    # ------------------------------------------------------------------------------------------------------------------
    def __str__(self) -> str:
        return f"CategoryData[{self.category_id=}, '{self.category_name=}', \
          {self.category_type_fk=}, {self.category_group_fk=}, '{self.category_description=}', \
            {self.category_tax_line_item=}, {self.category_hidden=}]"

    # ------------------------------------------------------------------------------------------------------------------
    def get_short_str(self) -> str:
        full_str = f"{self.category_name}, \
            {self.category_type_fk}, \
            {self.category_group_fk}, \
            {self.category_description}, \
            {self.category_tax_line_item}, \
            {self.category_hidden}"

        short_str = "".join(full_str.split())
        return short_str
