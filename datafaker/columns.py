import dataclasses
import random
import string
from dataclasses import dataclass, field
from typing import List

import numpy as np
import pandas as pd

from datafaker.column import Column, ColumnGenerationException

@dataclass(kw_only=True)
class Fixed(Column):
    value: any

    def generate(self, rows: int) -> pd.Series:
        match self.data_type:
            case 'Int':
                return pd.Series(np.full(rows, self.value)).astype(self.pandas_type())
            case _:
                return pd.Series(np.full(rows, self.value), dtype=self.pandas_type())


unit_factor = {
    's' :1E9,
    'ms':1E6,
    'us':1E3,
    'ns':1
}

@dataclass(kw_only=True)
class Random(Column):
    data_type: str = "Int"
    min: any
    max: any
    decimal_places: int = 4
    str_max_chars: int = 5000
    time_unit: str = 'ms'

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
                return pd.Series(list(''.join(random.choices(string.ascii_letters, k=random.randint(self.min, self.max))) for _ in range(rows)), dtype=self.pandas_type())
            
            case 'Timestamp':
                date_ints_series = self.random_date_ints(self.min, self.max, rows, self.time_unit)
                return pd.to_datetime(date_ints_series, unit=self.time_unit)

            case _:
                raise ColumnGenerationException(f"Data type [{self.data_type}] not recognised")


    def random_date_ints(self, start, end, rows, unit='ms'):
        start, end = pd.Timestamp(start), pd.Timestamp(end)
        return pd.Series(np.random.uniform(start.value // unit_factor[unit], end.value // unit_factor[unit], rows)).astype(int)




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
