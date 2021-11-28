import dataclasses
from dataclasses import dataclass, field
from typing import List

import numpy as np
import pandas as pd
import yaml

from datafaker.column import Column
from datafaker.target import Target


@dataclass(kw_only=True)
class Table:
    name: str
    rows: int
    columns: List[Column]
    targets: List[Target]
    df: pd.DataFrame = None
    complete: bool = False
    error: Exception = None

    @classmethod
    def parse_from_yaml(cls, yaml_str):
        conf = yaml.safe_load(yaml_str)
        return cls(**conf)

    def __init__(self, name: str, rows: int, columns: list):
        try:
            self.name = name
            self.rows = rows
            self.df = pd.DataFrame({"rowId": np.arange(self.rows)})
            self.columns = self.parse_cols(columns)
            self.targets = []

        except Exception as e:
            self.complete = False
            self.error = TableParsingException(
                f"Error on table [{self.name}]. {e}")

    def parse_cols(self, columns) -> list:
        cols = []
        try:
            for column in columns:
                cols.append(Column.parse(column))

        except Exception as e:
            self.complete = False
            self.error = TableParsingException(
                f"Error parsing column [{column.get('name')}]. {e}")
        return cols

    def generate(self) -> pd.DataFrame:
        """Generates the table data"""
        try:
            for column in self.columns:
                column.maybe_add_column(self.df)

        except Exception as e:
            self.complete = False
            self.error = TableGenerationException(
                f"Error on table [{self.name}]. {e}")

            raise self.error

        else:
            self.df.drop(columns="rowId", inplace=True)
            self.complete = True

    def load(self):
        """Loads `self.df` to the specified targets"""

    def result(self):
        return "yope"


class TableParsingException(Exception):
    pass


class TableGenerationException(Exception):
    pass
