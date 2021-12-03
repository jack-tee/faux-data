import copy
import dataclasses
from dataclasses import dataclass, field
from typing import List
import importlib

import numpy as np
import pandas as pd
import yaml

from datafaker.utils import get_parts

pandas_type_mapping = {"Int": "int64", "String": "string", "Float": "float64"}


@dataclass(kw_only=True)
class Column:
    name: str
    column_type: str
    data_type: str = None
    null_percentage: int = 0

    def maybe_add_column(self, df: pd.DataFrame) -> None:
        try:
            self.add_column(df)
            self.post_process(df)
        except Exception as e:
            raise ColumnGenerationException(
                f"Error on column [{self.name}]. Caused by: {e}.")

    def add_column(self, df: pd.DataFrame) -> None:
        df[self.name] = self.generate(len(df))

    def post_process(self, df: pd.DataFrame) -> None:
        """TBI"""
        pass

    def generate(self, rows: int) -> pd.Series:
        raise NotImplementedError("Please Implement this method")

    def pandas_type(self) -> str | None:
        if self.data_type:
            return pandas_type_mapping.get(self.data_type)
        return None


class ColumnGenerationException(Exception):
    pass