import random
import string
from dataclasses import dataclass, field
from typing import List

import numpy as np
import pandas as pd

pandas_type_mapping = {
    "Int": "Int64", 
    "String": "string", 
    "Float": "float64", 
    "Timestamp": "datetime64[ns]"
}


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
        if self.data_type:
            df[self.name] = df[self.name].astype(self.pandas_type())
        

    def generate(self, rows: int) -> pd.Series:
        raise NotImplementedError("Please Implement this method")

    def pandas_type(self) -> str | None:
        if self.data_type:
            return pandas_type_mapping.get(self.data_type)
        return None


@dataclass(kw_only=True)
class Fixed(Column):
    value: any

    def generate(self, rows: int) -> pd.Series:
        match self.data_type:
            case 'Int':
                return pd.Series(np.full(rows, self.value)).astype('float64').astype(self.pandas_type())
            case _:
                return pd.Series(np.full(rows, self.value), dtype=self.pandas_type())


@dataclass(kw_only=True)
class Empty(Column):
    def add_column(self, df: pd.DataFrame):
        df[self.name] = pd.Series(np.full(len(df), np.nan), dtype=self.pandas_type())


@dataclass(kw_only=True)
class MapValues(Column):
    source_column: str
    values: dict
    default: any = np.nan
    
    def add_column(self, df: pd.DataFrame):
        df[self.name] = df[self.source_column].map(self.values).fillna(self.default)



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
                return pd.Series(np.random.uniform(float(self.min), float(self.max)+1, rows)
                                          .round(decimals=self.decimal_places),
                                 dtype=self.pandas_type())

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
class Sequential(Column):
    """
    
    See https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases for `step:` values for Timestamps
    """
    start: any = 0
    step: any = 1

    def add_column(self, df: pd.DataFrame) -> None:
        if self.data_type in ['Int', 'Decimal', 'Float']:
            df[self.name] = df['rowId'] * float(self.step) + float(self.start)

        elif self.data_type == 'Timestamp':
            df[self.name] = pd.date_range(start=self.start, periods=len(df), freq=self.step)

        else:
            raise ColumnGenerationException(f"Data type [{self.data_type}] not recognised")


@dataclass(kw_only=True)
class Map(Column):
    """Creates a dict of columns based on the source cols"""
    source_columns: List[str] = field(default_factory=list)
    columns: List = field(default_factory=list)
    drop: bool = False
    select_one: bool = False

    def add_column(self, df: pd.DataFrame) -> None:
        if self.columns:
            self.drop = True
            for sub_col in self.columns:
                self.source_columns.append(sub_col.name)
                sub_col.maybe_add_column(df)


        if self.select_one:
            # randomly select one source_column per row and blank all other columns on that row
            chosen_cols = df[self.source_columns].columns.to_series().sample(len(df), replace=True, ignore_index=True)
            for col in self.source_columns:
                df.loc[chosen_cols != col, col] = np.nan

        df[self.name] = df[self.source_columns].to_dict(orient='records')

        if self.drop:
            df.drop(columns=self.source_columns, inplace=True)


@dataclass(kw_only=True)
class Array(Column):
    """Creates an array column based on a list of `source_columns:`."""
    source_columns: List[str] = field(default_factory=list)

    def add_column(self, df: pd.DataFrame) -> None:
        df[self.name] = list(df[self.source_columns].values)

class ColumnParsingException(Exception):
    pass

class ColumnGenerationException(Exception):
    pass
