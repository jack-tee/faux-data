from dataclasses import dataclass, field
from typing import List

import numpy as np
import pandas as pd
import yaml

from .column import Column
from .factory import ColumnFactory, TargetFactory
from .target import Target


@dataclass(kw_only=True)
class Table:
    name: str
    rows: int
    columns: List[Column]
    targets: List[Target] = field(default_factory=list, repr=False)
    output_cols: List[str] = field(default_factory=list)
    df: pd.DataFrame = None
    complete: bool = False
    error: Exception = None

    @classmethod
    def parse_from_yaml(cls, yaml_str):
        conf = yaml.safe_load(yaml_str)
        return cls(**conf)

    def __init__(self,
                 name: str,
                 rows: int,
                 columns: list,
                 output_cols: list = None,
                 targets: list = None):
        try:
            self.name = name
            self.rows = rows
            self.columns = self.parse_cols(columns)
            self.targets = self.parse_targets(targets)
            self.output_cols = output_cols if output_cols else None

        except Exception as e:
            self.complete = False
            raise TableParsingException(f"Error on table [{self.name}]. {e}")

    def parse_cols(self, columns) -> list:
        cols = []
        for column in columns:
            cols.append(ColumnFactory.parse(column))

        return cols

    def parse_targets(self, targets) -> list:
        targs = []

        if not targets:
            return targs

        for target in targets:
            targs.append(TargetFactory.parse(target))

        return targs

    def generate(self) -> None:
        """Generates the table data"""
        try:
            self.df = pd.DataFrame({"rowId": np.arange(self.rows)})
            for column in self.columns:
                column.maybe_add_column(self.df)

        except Exception as e:
            self.complete = False
            self.error = TableGenerationException(
                f"Error on table [{self.name}]. {e}")

            raise self.error

        else:
            self.df.drop(columns="rowId", inplace=True)

            if self.output_cols:
                self.df = self.df[self.output_cols]

            self.complete = True

    def load(self):
        """Loads `self.df` to the specified targets"""
        if not self.targets:
            print("No targets!")

        try:
            for target in self.targets:
                target.save(self)

        except Exception as e:
            self.complete = False
            self.error = TableLoadingException(
                f"Error on table [{self.name}]. {e}")

            raise self.error

    def run(self):
        self.generate()
        self.load()

    def result(self):
        return "yope"

    def __repr__(self):
        if isinstance(self.df, pd.DataFrame):
            df_repr = self.df.head(5)  #.to_markdown(index=False)
            df_types = self.df.dtypes
        else:
            df_repr = "Not generated"
            df_types = ""

        return f"""
Table: {self.name}
Sample:
{df_repr}
{df_types}"""


class TableParsingException(Exception):
    pass


class TableGenerationException(Exception):
    pass


class TableLoadingException(Exception):
    pass
