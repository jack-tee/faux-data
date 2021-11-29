import dataclasses
from dataclasses import dataclass, field
from typing import List

import numpy as np
import pandas as pd

from datafaker.column import Column, ColumnGenerationException


ALPHABET = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')

@dataclass(kw_only=True)
class Fixed(Column):
    value: any

    def generate(self, rows: int) -> pd.Series:
        match self.data_type:
            case 'Int':
                return pd.Series(np.full(rows, self.value)).astype(self.pandas_type())
            case _:
                return pd.Series(np.full(rows, self.value), dtype=self.pandas_type())


@dataclass(kw_only=True)
class Random(Column):
    data_type: str = "Int"
    min: any
    max: any
    decimal_places: int = 4
    str_max_chars: int = 5000

    def generate(self, rows: int) -> pd.Series:
        match self.data_type:
            case 'Int':
                return pd.Series(np.random.randint(int(self.min), int(self.max)+1, rows), dtype=self.pandas_type())

            case 'Float':
                return pd.Series(np.random.uniform(float(self.min), float(self.max)+1, rows).round(decimals=self.decimal_places), dtype=self.pandas_type())

            case 'String':
                # limit how long strings can be
                self.min = min(int(self.min), self.str_max_chars)
                self.max = min(int(self.max), self.str_max_chars)
                chars = np.random.choice(ALPHABET, (rows, self.max))
                lens = np.random.randint(self.min, self.max+1, rows)
                return pd.Series(list(chars), dtype='string').str.join('')
                # np.array(list(''.join(a)[0:l] for a, l in zip(chars, lens))

            case _:
                raise ColumnGenerationException(f"Data type [{self.data_type}] not recognised")


@dataclass(kw_only=True)
class Selection(Column):
    values: List[any] = field(default_factory=list)
    source_columns: List[any] = field(default_factory=list)

    def generate(self, rows: int) -> pd.Series:
        return pd.Series(np.random.choice(self.values, rows, replace=True), dtype=self.pandas_type())


@dataclass(kw_only=True)
class Map(Column):
    """Creates a dict of columns based on the source cols"""
    source_columns: List[str] = field(default_factory=list)
    drop: bool = False

    def add_column(self, df: pd.DataFrame) -> None:
        df[self.name] = df[self.source_columns].to_dict(orient='records')

        if self.drop:
            df.drop(columns=self.source_columns, inplace=True)